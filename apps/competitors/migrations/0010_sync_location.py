from django.contrib.gis.geos import Point
from django.db import migrations


def sync(apps, schema_editor):
    """Make location match latitude/longitude on every existing row.

    Rows written by bulk_create without a hand-built Point have no location,
    and rows whose coordinates were removed still have the old one.
    """
    Competitor = apps.get_model('competitors', 'Competitor')
    for c in Competitor.objects.only('id', 'latitude', 'longitude', 'location').iterator():
        if c.latitude is not None and c.longitude is not None:
            expected = Point(float(c.longitude), float(c.latitude), srid=4326)
        else:
            expected = None
        if (c.location is None) != (expected is None) or \
                (expected is not None and not c.location.equals_exact(expected, tolerance=1e-9)):
            Competitor.objects.filter(pk=c.pk).update(location=expected)


class Migration(migrations.Migration):

    dependencies = [
        ("competitors", "0009_recompute_review_stats"),
    ]

    operations = [
        migrations.RunPython(sync, migrations.RunPython.noop),
    ]
