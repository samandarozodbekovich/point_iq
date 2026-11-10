# PointIQ (get_place) — backend

Biznes uchun joy tanlashga yordam beradigan API: berilgan nuqta atrofidagi
raqobatchilar, aholi va demografiya, transport va yo'l oqimi, mobil minoralar
bo'yicha ma'lumot yig'adi, joyni baholaydi va AI orqali tavsiya beradi.
Hozircha Toshkent shahri uchun.

## Texnologiyalar

| Qism | Nima |
|---|---|
| Til / framework | Python 3.12, Django 6.1, Django REST Framework |
| Baza | PostgreSQL 16 + PostGIS |
| Fon vazifalar | Celery (worker + beat), Redis (broker, kesh, rate limit) |
| Autentifikatsiya | JWT (SimpleJWT), telefon + SMS kod |
| Tashqi xizmatlar | OpenAI, Google Places, 2GIS, Overpass (OpenStreetMap), OpenCellID, Nominatim |

## Loyiha tuzilmasi

```
get_place/        settings, urls, celery
apps/
  users/          ro'yxatdan o'tish, SMS kod (OTP), login, parolni tiklash
  areas/          shaharlar va tumanlar (chegaralari PostGIS'da)
  citizens/       aholi, ta'lim, iste'mol — tuman bo'yicha statistika
  competitors/    raqobatchilar, kategoriyalar, sharhlar, Google/2GIS importi
  dictionary/     transport tugunlari, POI, yo'llar, heatmap, joy tahlili
  government_bodies/  davlat organlari va xodimlar
  property/       ko'chmas mulk e'lonlari va rasmlari
  networks/       mobil minoralar (OpenCellID)
  ai/             AI chat va so'rovlar tarixi
  shared/         umumiy viewset'lar, ruxsatlar, throttle, pagination
data/             boshlang'ich ma'lumotlar (tumanlar GeoJSON, kategoriyalar, ...)
```

## Lokal ishga tushirish

Kerak: Python 3.12, PostgreSQL 16 + PostGIS, Redis, GDAL/GEOS.
Windows'da GDAL [OSGeo4W](https://trac.osgeo.org/osgeo4w/) orqali
`C:\OSGeo4W` ga o'rnatilgan bo'lishi kerak (yo'li `settings.py` da).

```bash
python -m venv venv
venv\Scripts\activate            # Linux/macOS: source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env             # qiymatlarni to'ldiring (pastga qarang)

# PostgreSQL'da baza va PostGIS
createdb get_place_db
psql get_place_db -c "CREATE EXTENSION postgis;"

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# alohida terminallarda
celery -A get_place worker -l info
celery -A get_place beat -l info
```

## Docker bilan

```bash
cp .env.example .env             # DB_HOST=db, REDIS_HOST=redis
docker compose up -d --build
```

Servislar: `db` (PostGIS), `redis`, `api` (gunicorn, `migrate` va
`collectstatic` ni o'zi bajaradi), `celery`, `celery-beat`.

`api` va `db` portlari faqat `127.0.0.1` da ochiq: tashqaridan so'rovlar
shu serverdagi reverse proxy (nginx va h.k.) orqali keladi. Proxy boshqa
mashinada bo'lsa, `docker-compose.yml` dagi `ports` ni moslang.

## Muhit o'zgaruvchilari (`.env`)

Ro'yxat `.env.example` da. `.env` hech qachon git'ga qo'shilmaydi.

| O'zgaruvchi | Vazifasi |
|---|---|
| `SECRET_KEY`, `DEBUG` | Django |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | PostgreSQL |
| `REDIS_HOST`, `REDIS_PORT`, `CELERY_*` | Redis va Celery |
| `OPENAI_API_KEY` | AI chat |
| `GOOGLE_MAP_API_KEY` | Google Places (raqobatchilar tahlili) |
| `TWO_GIS_API_KEY` | 2GIS qidiruv va import |
| `OPENCELLID_KEY` | mobil minoralar |
| `ESKIZ_EMAIL`, `ESKIZ_PASSWORD` | SMS (Eskiz) |
| `NUM_PROXIES` | server oldidagi proxy'lar soni; rate limit uchun mijoz IP'si shundan aniqlanadi (odatda `1`) |
| `CORS_ALLOWED_ORIGINS` | API'ni chaqira oladigan frontend manzillari, vergul bilan |

`ALLOWED_HOSTS` hozircha `settings.py` ichida ro'yxat sifatida yozilgan.

## Boshlang'ich ma'lumotlarni yuklash

```bash
# Tumanlar (har bir fayl uchun; tashkent.geojson — butun shahar)
python manage.py upload_districts data/districts/chilanzar.geojson

# Raqobatchi kategoriyalari — mavjud bazada avval --dry-run
python manage.py upload_category data/competitors/competitor_category.json --dry-run
python manage.py upload_category data/competitors/competitor_category.json

# Iste'mol statistikasi
python manage.py upload_people_consume data/citizens/people_consume.json

# Mobil minoralar: fayldan yoki OpenCellID'dan
python manage.py upload_cell_towers --file data/cell_towers/cell.geojson
python manage.py sync_towers

# Transport tugunlari, POI va yo'llar (Overpass)
python manage.py fetch_tashkent_data --lat 41.311 --lng 69.240 --radius 800

# JSON'dan import (dublikat tekshiruvi --unique-field bo'yicha, default name_uz)
python manage.py import_competitors <fayl.json>
python manage.py import_branch <fayl.json>
```

## API

Barcha endpointlar `/api/` ostida. Hujjatlar: `/swagger/` va `/redoc/`.

### Autentifikatsiya

1. `POST /api/users/signup/` — telefon raqam; javobda vaqtinchalik token.
   Telefonga 6 xonali kod yuboriladi.
2. `POST /api/users/verify/` — kod (token bilan).
3. `PUT /api/users/change-info/` — ism va parol; ro'yxatdan o'tish shu bilan
   tugaydi, javobda yangi tokenlar keladi.
4. `POST /api/users/login/`, `POST /api/users/login-refresh/`,
   `POST /api/users/logout/`.

Parolni tiklash: `POST /api/users/forgot-password/` (kod yuboriladi), keyin
`PUT /api/users/reset-password/` (`phone_number`, `code`, `password`,
`confirm_password`). Parol o'zgarganda userning barcha eski sessiyalari
yopiladi.

Kod 5 marta noto'g'ri kiritilsa bloklanadi — yangi kod so'rash kerak.

### Cheklovlar

| Nima | Limit |
|---|---|
| AI chat | userga soatiga 20 |
| Google Places | userga soatiga 10 |
| 2GIS | userga soatiga 30 |
| Kod yuborish | telefon raqamga soatiga 5 |
| Kod tekshirish | telefon raqamga soatiga 10 |
| Ro'yxatdan o'tish | IP'ga soatiga 10 |

Qiymatlar `settings.py` dagi `REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]` da.
Pullik tashqi API'larni chaqiradigan endpointlar login talab qiladi.

### Ruxsatlar va sahifalash

- Ma'lumotnomalar (tumanlar, aholi, davlat organlari, ...) hamma uchun o'qish
  uchun ochiq, yozish faqat admin uchun.
- E'lonlar va ularning rasmlarini login qilgan user yaratadi; o'zgartirish —
  faqat egasi yoki admin.
- Raqobatchilar va e'lonlar ro'yxati sahifalanadi: 50 tadan,
  `?page=` va `?page_size=` (200 gacha); javobda `next` / `previous`.
- Heatmap (`/api/statistics/heatmap/`) uchun `in_bbox=xmin,ymin,xmax,ymax`
  majburiy (har tomoni 0.5° gacha).

## Testlar

Har bir ilovaning testlari `apps/<ilova>/tests/` da, har bir API yoki klass
uchun alohida fayl (masalan `apps/users/tests/test_password_reset.py`).
Umumiy yordamchilar: `apps/shared/testing.py`.

```bash
python manage.py test
```

Testlar haqiqiy PostgreSQL + PostGIS bilan ishlaydi: `.env` dagi
foydalanuvchi test bazasini yarata olishi kerak. Tashqi xizmatlar
(OpenAI, Google, 2GIS, Celery) testlarda mock qilinadi.

## Deploy

```bash
git pull
docker compose up -d --build     # migrate api konteynerida bajariladi
```

Yangi migratsiyalar kelganda ma'lumot yuklash buyruqlari ham kerak bo'lishi
mumkin — commit xabarlariga qarang (masalan, tumanlar chegarasi uchun
`upload_districts` ni qayta ishga tushirish).
