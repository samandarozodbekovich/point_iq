
from apps.citizens.relationship_status.models import RelationshipStatus, RelationshipStatusPopulation
from apps.citizens.relationship_status.serializers import RelationshipStatusSerializer, \
    RelationshipStatusPopulationSerializer
from apps.core.views import BaseBulkMethods
from apps.shared.views.base_view_set import BaseModelViewSet


class RelationshipStatusViewSet(BaseModelViewSet):
    model = RelationshipStatus
    serializer_class = RelationshipStatusSerializer




class RelationshipStatusPopulationViewSet(BaseModelViewSet, BaseBulkMethods):
    model = RelationshipStatusPopulation
    serializer_class = RelationshipStatusPopulationSerializer
