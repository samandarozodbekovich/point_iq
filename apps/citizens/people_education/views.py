from apps.citizens.people_education.models import PeopleEducation
from apps.citizens.people_education.serializers import PeopleEducationSerializer
from apps.core.views import BaseBulkMethods

from apps.shared.views.base_view_set import BaseModelViewSet


class PeopleEducationViewSet(BaseModelViewSet, BaseBulkMethods):
    model = PeopleEducation
    serializer_class = PeopleEducationSerializer
