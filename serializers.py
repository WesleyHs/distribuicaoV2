from rest_framework import serializers
from .models import modelDistribuicaoV2

class DistribuicaoV2Serializer(serializers.ModelSerializer):

    dataAdmissao = serializers.DateTimeField(
        input_formats=['%d/%m/%Y'],  # aceita formato "12/09/2021"
        required=False, allow_null=True
    )

    class Meta:
        model = modelDistribuicaoV2
        fields = '__all__'
