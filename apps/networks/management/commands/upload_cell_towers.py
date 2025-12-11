import json
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from apps.networks.models import CellTower

class Command(BaseCommand):
    help = 'Import cell tower data from JSON/GeoJSON file (unique by mcc+mnc+lac+cellid) with batch saving'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, default='cell.geojson')
        parser.add_argument('--batch-size', type=int, default=1000)
        parser.add_argument('--clear', action='store_true')
        parser.add_argument('--debug', action='store_true')

    def handle(self, *args, **options):
        file_path = options['file']
        batch_size = options['batch_size']
        debug = options['debug']

        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("Cell Tower Import Started"))
        self.stdout.write("=" * 60)

        # Load JSON
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            raise CommandError(f"Cannot load JSON: {e}")

        # Extract features
        if isinstance(data, dict) and data.get("type") == "FeatureCollection":
            items = data.get("features", [])
        elif isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            items = [data]
        else:
            raise CommandError("Unsupported JSON format")

        total = len(items)
        self.stdout.write(f"✓ Loaded {total} items")

        # Clear table if needed
        if options["clear"]:
            count = CellTower.objects.count()
            if count > 0:
                confirm = input(f"Delete {count} rows? (yes/no): ")
                if confirm.lower() == "yes":
                    CellTower.objects.all().delete()
                    self.stdout.write("✓ Table cleared")

        created_total = 0
        updated_total = 0
        error_total = 0
        batch = []

        for i, item in enumerate(items, start=1):
            try:
                # GeoJSON format
                if "properties" in item and "geometry" in item:
                    props = item["properties"] or {}
                    geom = item["geometry"] or {}
                    coords = geom.get("coordinates", [])
                    lon, lat = (coords[0], coords[1]) if len(coords) >= 2 else (None, None)
                else:
                    props = item
                    lat = props.get("lat") or props.get("latitude")
                    lon = props.get("lon") or props.get("longitude")

                # Validate coordinates
                try:
                    lat = float(lat)
                    lon = float(lon)
                except:
                    if debug:
                        self.stdout.write(f"[DEBUG] Skip {i}: bad lat/lon → {lat}, {lon}")
                    error_total += 1
                    continue

                def to_int(v):
                    try:
                        return int(float(v))
                    except:
                        return None

                mcc = to_int(props.get("mcc"))
                mnc = to_int(props.get("mnc") or props.get("net"))
                lac = to_int(props.get("lac") or props.get("area"))
                cellid = to_int(
                    props.get("cellid") or props.get("cid") or props.get("cell") or props.get("area")
                )

                if None in (mcc, mnc, cellid):
                    if debug:
                        self.stdout.write(
                            f"[DEBUG] Skip {i}: Missing required → mcc={mcc}, mnc={mnc}, cellid={cellid}"
                        )
                    error_total += 1
                    continue

                # Check for duplicates in DB
                exists = CellTower.objects.filter(
                    mcc=mcc, mnc=mnc, lac=lac or 0, cellid=cellid
                ).first()

                if exists:
                    updated_total += 1
                    continue

                # Build tower object
                tower = CellTower(
                    latitude=lat,
                    longitude=lon,
                    radio=props.get("radio") or props.get("radio_type") or "",
                    mcc=mcc,
                    mnc=mnc,
                    lac=lac or 0,
                    cellid=cellid,
                    range_meters=props.get("range") or props.get("range_meters"),
                    samples=props.get("samples"),
                )

                batch.append(tower)

                # Save batch if full
                if len(batch) >= batch_size:
                    created_total += self._save_batch(batch)
                    batch = []

                    self.stdout.write(
                        f"Progress {i}/{total} | Created {created_total} | Updated {updated_total} | Errors {error_total}"
                    )

            except Exception as e:
                error_total += 1
                self.stdout.write(self.style.ERROR(f"Record {i} error: {e}"))

        # Save remaining batch
        if batch:
            created_total += self._save_batch(batch)

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("IMPORT FINISHED"))
        self.stdout.write(f"✓ Total: {total}")
        self.stdout.write(f"✓ Created: {created_total}")
        self.stdout.write(f"✓ Updated (skipped duplicates): {updated_total}")
        self.stdout.write(f"✗ Errors: {error_total}")
        self.stdout.write("=" * 60)

    @transaction.atomic
    def _save_batch(self, batch):
        CellTower.objects.bulk_create(batch)
        return len(batch)
