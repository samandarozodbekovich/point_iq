import json
from django.core.management.base import BaseCommand


class BaseImportCommand(BaseCommand):
    help = "Import JSON data with progress bar, duplicate check, ForeignKey support, and pk update"

    def add_arguments(self, parser):
        parser.add_argument("file", type=str, help="Path to JSON file")
        parser.add_argument(
            "--unique-field",
            type=str,
            default="name_uz",
            help="Field used to prevent duplicates (default: name_uz)"
        )

    def handle(self, *args, **options):
        file_path = options['file']
        unique_field = options['unique_field']
        model = getattr(self, 'model', None)
        if model is None:
            return self.stderr.write(self.style.ERROR("Model not defined in child class"))

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            return self.stderr.write(self.style.ERROR("File not found"))
        except json.JSONDecodeError:
            return self.stderr.write(self.style.ERROR("Invalid JSON format"))

        total = len(data)
        if total == 0:
            return self.stdout.write(self.style.WARNING("JSON file is empty"))

        self.stdout.write(f"Importing {total} rows...")

        added = 0
        updated = 0
        skipped = 0

        for i, entry in enumerate(data, start=1):
            if "fields" in entry:
                fields = entry["fields"]
                pk = entry.get("pk")
            else:
                fields = entry
                pk = fields.get("pk")

            # resolve ForeignKey fields given as a pk
            for field in model._meta.fields:
                if field.is_relation and field.name in fields:
                    value = fields[field.name]
                    if isinstance(value, int):  # only when an id was given
                        fields[field.name + "_id"] = value
                        del fields[field.name]
                    elif isinstance(value, dict) and "pk" in value:
                        fields[field.name + "_id"] = value["pk"]
                        del fields[field.name]

            # Duplicate or pk check
            obj = None
            if pk:
                obj = model.objects.filter(pk=pk).first()
            elif unique_field in fields:
                obj = model.objects.filter(**{unique_field: fields[unique_field]}).first()

            if obj:
                for key, value in fields.items():
                    setattr(obj, key, value)
                obj.save()
                updated += 1
            else:
                model.objects.create(**fields)
                added += 1

            # Progress bar
            progress = int((i / total) * 50)
            bar = "█" * progress + "-" * (50 - progress)
            print(f"\r[{bar}] {i}/{total}", end="")

        print()
        self.stdout.write(
            self.style.SUCCESS(f"Added: {added}, Updated: {updated}, Skipped: {skipped}, Total: {total}")
        )
