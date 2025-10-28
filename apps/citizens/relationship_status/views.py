from apps.citizens.relationship_status.models import RelationshipStatus
from apps.citizens.relationship_status.serializers import RelationshipStatusSerializer
from apps.dictionary.views import BaseModelViewSet


class RelationshipStatusViewSet(BaseModelViewSet):
    model = RelationshipStatus
    serializer_class = RelationshipStatusSerializer