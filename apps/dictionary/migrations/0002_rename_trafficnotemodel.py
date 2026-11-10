from django.db import migrations


class Migration(migrations.Migration):
    """TrafficNoteModel -> TrafficNodeModel: it models a traffic node.

    Written by hand: without the interactive "did you rename?" prompt,
    makemigrations emits DeleteModel + CreateModel, which drops the data.
    RenameModel renames the table and keeps every row.
    """

    dependencies = [
        ("dictionary", "0001_initial"),
    ]

    operations = [
        migrations.RenameModel(old_name="TrafficNoteModel", new_name="TrafficNodeModel"),
    ]
