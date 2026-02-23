from rest_framework_gis.serializers import GeoFeatureModelSerializer

from apps.dictionary.population_traffic.models.traffic_note import TrafficNoteModel


class TrafficNodeGeoSerializer(GeoFeatureModelSerializer):

    class Meta:
        model = TrafficNoteModel
        geo_field = 'location'
        fields = ('id', 'name', 'node_type', 'base_weight')