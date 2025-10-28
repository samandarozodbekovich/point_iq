from apps.citizens.relationship_counts.models import RelationshipCount
from apps.citizens.relationship_counts.serializers import RelationshipCountSerializer
from apps.dictionary.views import BaseModelViewSet


class RelationshipCountViewSet(BaseModelViewSet):
    model = RelationshipCount
    serializer_class = RelationshipCountSerializer