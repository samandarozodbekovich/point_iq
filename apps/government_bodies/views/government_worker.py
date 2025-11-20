from apps.core.views import BaseBulkMethods
from apps.government_bodies.models import GovernmentWorker
from apps.government_bodies.serializers import GovernmentWorkerSerializer
from apps.shared.views.base_view_set import BaseModelViewSet


class GovernmentWorkerViewSet(BaseModelViewSet, BaseBulkMethods):
    model = GovernmentWorker
    serializer_class = GovernmentWorkerSerializer
