from rest_framework import serializers
from .models import *

class MunicipalitySerializers(serializers.ModelSerializer):
    class Meta:
        model = Municipality
        fields = '__all__'

class MunicipalityAwareModelSerializers(serializers.ModelSerializer):
    class Meta:
        model = MunicipalityAwareModel
        fields = '__all__'