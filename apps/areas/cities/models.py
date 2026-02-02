
from apps.shared.models import BaseNameModel, BaseTimeModel

class City(BaseNameModel, BaseTimeModel):
    pass

    def __str__(self):
        return self.name_uz