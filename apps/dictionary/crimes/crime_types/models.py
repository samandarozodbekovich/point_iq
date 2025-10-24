
from apps.shared.models import BaseTimeModel, BaseNameModel


class CrimeTypes(BaseTimeModel, BaseNameModel):


    def __str__(self):
        return self.name_uz
