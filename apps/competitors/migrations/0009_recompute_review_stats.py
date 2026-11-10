from django.db import migrations
from django.db.models import Avg, Count


def recompute(apps, schema_editor):
    """Fill average_rating and review_count from the reviews.

    The review signal never assigned review_count, so it is 0 on existing
    rows, and the competitor serializer now reads both stored fields instead
    of aggregating per row.
    """
    Competitor = apps.get_model('competitors', 'Competitor')
    rows = Competitor.objects.annotate(avg=Avg('reviews__rating'), cnt=Count('reviews'))
    for c in rows.iterator():
        avg = round(c.avg, 2) if c.avg is not None else None
        if c.average_rating != avg or c.review_count != c.cnt:
            Competitor.objects.filter(pk=c.pk).update(average_rating=avg, review_count=c.cnt)


class Migration(migrations.Migration):

    dependencies = [
        ('competitors', '0008_competitor_location'),
    ]

    operations = [
        migrations.RunPython(recompute, migrations.RunPython.noop),
    ]
