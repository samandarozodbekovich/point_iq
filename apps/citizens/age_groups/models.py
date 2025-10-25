from apps.shared.models import BaseNameModel, BaseTimeModel


class AgeGroup(BaseNameModel, BaseTimeModel):

    class Meta:
        verbose_name = "Age Group"
        verbose_name_plural = "Age Groups"
        ordering = ["id"]

    def __str__(self):
        return self.name_uz


