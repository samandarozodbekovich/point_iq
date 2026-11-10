from apps.areas.districts.models import District
from apps.shared.models import BaseTimeModel
from django.db import models

# Calendar order of the Uzbek month names stored in PeopleConsume.month.
MONTHS = ('yanvar', 'fevral', 'mart', 'aprel', 'may', 'iyun',
          'iyul', 'avgust', 'sentabr', 'oktabr', 'noyabr', 'dekabr')


class PeopleConsume(BaseTimeModel):
    district = models.ForeignKey(District, on_delete=models.SET_NULL , null=True, blank=True)
    month = models.CharField(max_length=10, null=True, blank=True)
    year = models.CharField(max_length=4, null=True, blank=True)
    consume_gas = models.IntegerField(null=True, blank=True)
    consume_electric = models.IntegerField(null=True, blank=True)
    bus_station = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f'people of {self.district} in {self.month} of {self.year}'

    @property
    def period(self):
        """(year, month number) for sorting; unknown values sort first."""
        try:
            year = int(self.year)
        except (TypeError, ValueError):
            year = 0
        month = (self.month or '').strip().lower()
        return year, MONTHS.index(month) + 1 if month in MONTHS else 0

    @classmethod
    def latest_for_district(cls, district):
        # month is text, so order_by('-month') sorts alphabetically
        # ('yanvar' > 'oktabr'). Pick the latest in Python: a district has
        # a few dozen rows at most.
        return max(cls.objects.filter(district=district), key=lambda r: r.period, default=None)