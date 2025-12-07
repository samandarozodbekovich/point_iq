from rest_framework import serializers
from .models import CellTower

class CellTowerSerializer(serializers.ModelSerializer):

    class Meta:
        model = CellTower
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']




