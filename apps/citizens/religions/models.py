from apps.shared.models import BaseTimeModel, BaseNameModel


class Religion(BaseTimeModel, BaseNameModel):
    pass

    def __str__(self):
        return self.name_uz
