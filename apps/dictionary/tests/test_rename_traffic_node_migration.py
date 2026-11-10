"""Migration 0002_rename_trafficnotemodel keeps existing rows."""
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class RenameTrafficNodeMigrationTests(TransactionTestCase):
    before = [("dictionary", "0001_initial")]
    after = [("dictionary", "0002_rename_trafficnotemodel")]

    def migrate(self, target):
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()
        executor.migrate(target)
        return executor.loader.project_state(target).apps

    def test_rows_survive_the_rename(self):
        old_apps = self.migrate(self.before)
        Old = old_apps.get_model("dictionary", "TrafficNoteModel")
        Old.objects.create(name="Metro", location="SRID=4326;POINT(69.2 41.3)", node_type="transit", base_weight=8)

        new_apps = self.migrate(self.after)
        New = new_apps.get_model("dictionary", "TrafficNodeModel")
        self.assertEqual(list(New.objects.values_list("name", "node_type")), [("Metro", "transit")])
