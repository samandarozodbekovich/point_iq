# PointIQ (get_place) — backend

An API that helps businesses choose a location: for a given point it gathers
competitors, population and demographics, transport and road traffic, and
mobile cell towers, scores the location and gives AI recommendations.
Currently covers Tashkent.

## Stack

| Part | What |
|---|---|
| Language / framework | Python 3.12, Django 6.1, Django REST Framework |
| Database | PostgreSQL 16 + PostGIS |
| Background jobs | Celery (worker + beat), Redis (broker, cache, rate limits) |
| Authentication | JWT (SimpleJWT), phone number + SMS code |
| External services | OpenAI, Google Places, 2GIS, Overpass (OpenStreetMap), OpenCellID, Nominatim |

## Project layout

```
get_place/        settings, urls, celery
apps/
  users/          signup, SMS codes (OTP), login, password reset
  areas/          cities and districts (boundaries in PostGIS)
  citizens/       population, education, consumption — per-district statistics
  competitors/    competitors, categories, reviews, Google/2GIS import
  dictionary/     transport nodes, POIs, roads, heatmap, location analysis
  government_bodies/  government bodies and their staff
  property/       real estate listings and their images
  networks/       mobile cell towers (OpenCellID)
  ai/             AI chat and query history
  shared/         shared viewsets, permissions, throttles, pagination
data/             seed data (district GeoJSON, categories, ...)
```

## Running locally

Requirements: Python 3.12, PostgreSQL 16 + PostGIS, Redis, GDAL/GEOS.
On Windows, GDAL is expected from [OSGeo4W](https://trac.osgeo.org/osgeo4w/)
in `C:\OSGeo4W` (path set in `settings.py`).

```bash
python -m venv venv
venv\Scripts\activate            # Linux/macOS: source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env             # fill in the values (see below)

# Database with PostGIS
createdb get_place_db
psql get_place_db -c "CREATE EXTENSION postgis;"

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# in separate terminals
celery -A get_place worker -l info
celery -A get_place beat -l info
```

## Docker

```bash
cp .env.example .env             # DB_HOST=db, REDIS_HOST=redis
docker compose up -d --build
```

Services: `db` (PostGIS), `redis`, `api` (gunicorn; runs `migrate` and
`collectstatic` on start), `celery`, `celery-beat`.

The `api` and `db` ports are bound to `127.0.0.1` only: outside traffic comes
through a reverse proxy (nginx etc.) on the same host. If the proxy runs on
another machine, adjust `ports` in `docker-compose.yml`.

## Environment variables (`.env`)

The full list is in `.env.example`. `.env` is never committed.

| Variable | Purpose |
|---|---|
| `SECRET_KEY`, `DEBUG` | Django |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | PostgreSQL |
| `REDIS_HOST`, `REDIS_PORT`, `CELERY_*` | Redis and Celery |
| `OPENAI_API_KEY` | AI chat |
| `GOOGLE_MAP_API_KEY` | Google Places (competitor analysis) |
| `TWO_GIS_API_KEY` | 2GIS search and import |
| `OPENCELLID_KEY` | cell towers |
| `ESKIZ_EMAIL`, `ESKIZ_PASSWORD` | SMS (Eskiz) |
| `NUM_PROXIES` | number of proxies in front of the app; used to find the client IP for rate limits (usually `1`) |
| `CORS_ALLOWED_ORIGINS` | frontend origins allowed to call the API, comma-separated |

`ALLOWED_HOSTS` is currently a list in `settings.py`.

## Loading seed data

```bash
# Districts (once per file; tashkent.geojson is the whole city)
python manage.py upload_districts data/districts/chilanzar.geojson

# Competitor categories — on an existing database, run --dry-run first
python manage.py upload_category data/competitors/competitor_category.json --dry-run
python manage.py upload_category data/competitors/competitor_category.json

# Consumption statistics
python manage.py upload_people_consume data/citizens/people_consume.json

# Cell towers: from a file or from OpenCellID
python manage.py upload_cell_towers --file data/cell_towers/cell.geojson
python manage.py sync_towers

# Transport nodes, POIs and roads (Overpass)
python manage.py fetch_tashkent_data --lat 41.311 --lng 69.240 --radius 800

# JSON import (duplicates checked by --unique-field, default name_uz)
python manage.py import_competitors <file.json>
python manage.py import_branch <file.json>
```

## API

All endpoints live under `/api/`. Docs: `/swagger/` and `/redoc/`.

### Authentication

1. `POST /api/users/signup/` — phone number; returns a temporary token and
   sends a 6-digit code to the phone.
2. `POST /api/users/verify/` — the code (with the token).
3. `PUT /api/users/change-info/` — name and password; completes registration
   and returns new tokens.
4. `POST /api/users/login/`, `POST /api/users/login-refresh/`,
   `POST /api/users/logout/`.

Password reset: `POST /api/users/forgot-password/` (sends a code), then
`PUT /api/users/reset-password/` (`phone_number`, `code`, `password`,
`confirm_password`). Changing the password ends all of the user's other
sessions.

A code is locked after 5 wrong attempts; request a new one.

### Rate limits

| What | Limit |
|---|---|
| AI chat | 20 per hour per user |
| Google Places | 10 per hour per user |
| 2GIS | 30 per hour per user |
| Sending codes | 5 per hour per phone number |
| Checking codes | 10 per hour per phone number |
| Signup | 10 per hour per IP |

The values are in `REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]` in `settings.py`.
Endpoints that call paid external APIs require login.

### Permissions and pagination

- Reference data (districts, population, government bodies, ...) can be read
  by anyone; only admins can write it.
- Listings and their images are created by logged-in users; only the owner
  or an admin can change them.
- Competitor and listing lists are paginated: 50 per page, `?page=` and
  `?page_size=` (up to 200); responses include `next` / `previous`.
- The heatmap (`/api/statistics/heatmap/`) requires
  `in_bbox=xmin,ymin,xmax,ymax` (at most 0.5° each way).

## Tests

Each app keeps its tests in `apps/<app>/tests/`, one file per API or class
(e.g. `apps/users/tests/test_password_reset.py`). Shared helpers live in
`apps/shared/testing.py`.

```bash
python manage.py test
```

Tests run against a real PostgreSQL + PostGIS: the database user in `.env`
must be allowed to create the test database. External services (OpenAI,
Google, 2GIS, Celery) are mocked.

## Deploy

```bash
git pull
docker compose up -d --build     # migrate runs in the api container
```

New migrations may also need a data command — check the commit messages
(e.g. re-run `upload_districts` for district boundaries).
