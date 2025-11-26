
from apps.government_bodies.models import GovernmentBody
from apps.shared.management.commands.base_import_commands import BaseImportCommand

class Command(BaseImportCommand):
    model = GovernmentBody


