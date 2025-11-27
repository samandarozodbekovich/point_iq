
from apps.citizens.people_consume.models import PeopleConsume
from apps.citizens.people_consume.serializers import PeopleConsumeSerializer
from apps.core.views import BaseBulkMethods
from apps.shared.views.base_view_set import BaseModelViewSet

class PeopleConsumeViewSet(BaseModelViewSet, BaseBulkMethods):
    model = PeopleConsume
    serializer_class = PeopleConsumeSerializer


