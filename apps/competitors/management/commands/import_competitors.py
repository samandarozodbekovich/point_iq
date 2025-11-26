
from django.core import serializers
from django.core.management.base import BaseCommand

from apps.competitors.competitor.models import Competitor
from apps.shared.management.commands.base_import_commands import BaseImportCommand

class Command(BaseImportCommand):
    model = Competitor

# class Command(BaseCommand):
#     help = "Import items from JSON file with progress bar and duplicate protection"
#
#     def add_arguments(self, parser):
#         parser.add_argument("file", type=str, help="JSON file path")
#
#     def handle(self, *args, **options):
#         file_path = options["file"]
#
#         try:
#             with open(file_path, "r", encoding="utf-8") as f:
#                 data = f.read()
#             for obj in serializers.deserialize("json", data):
#                 model_class = obj.object.__class__
#                 pk = obj.object.pk
#                 if not model_class.objects.filter(pk=pk).exists():
#                     obj.save()
#             self.stdout.write(self.style.SUCCESS("Successfully imported competitors"))
#         except Exception as e:
#             self.stderr.write(self.style.ERROR(str(e)))