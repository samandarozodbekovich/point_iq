import json

from django.core.management import BaseCommand
from django.db import transaction

from apps.areas.districts.models import District
from apps.citizens.people_consume.models import PeopleConsume

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('people_consume', type=str, help='People consume json file')

    def handle(self, *args, **options):
        file_path = options['people_consume']
        self.stdout.write(f"reading {file_path}")

        try:
            with open(file_path) as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stdout.write("file not found")
        except json.JSONDecodeError as e:
            self.stdout.write(f"error: {e}")

        bulk_data = []
        skipped_count = 0

        existing_records = set(
            PeopleConsume.objects.values_list('district', 'month', 'year')
        )

        for i in data:
            district_instance = District.objects.get(id=i["district"])
            key = (district_instance.id, i["month"], i["year"])
            if key in existing_records:
                skipped_count +=1
                continue
            bulk_data.append(
                PeopleConsume(
                    district=district_instance,
                    month=i["month"],
                    year=i["year"],
                    consume_gas=i["consume_gas"],
                    consume_electric=i["consume_electric"],
                    bus_station=i["bus_station"],
                )
            )
        uploaded_count = self.upload_people_consume(bulk_data)
        self.stdout.write(f"{uploaded_count} people consumed have been uploaded to database")
        if skipped_count:
            self.stdout.write(f"skipped {skipped_count} people have been skipped")

    @transaction.atomic
    def upload_people_consume(self, bulk_data):
        if not bulk_data:
            return 0
        PeopleConsume.objects.bulk_create(bulk_data)
        return len(bulk_data)


