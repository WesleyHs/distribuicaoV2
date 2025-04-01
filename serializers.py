from rest_framework import serializers
from .models import modelDistribuicaoV2

class DistribuicaoV2Serializer(serializers.ModelSerializer):
    class Meta:
        model = modelDistribuicaoV2
        fields = '__all__'