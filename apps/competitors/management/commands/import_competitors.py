
from apps.competitors.competitor.models import Competitor
from apps.shared.management.commands.base_import_commands import BaseImportCommand

class Command(BaseImportCommand):
    model = Competitor
