from rest_framework.viewsets import ModelViewSet
from .serializers import *
from .models import * 
from apps.core.permissions import IsSuperAdmin

class MunicipalityViewSet(ModelViewSet):
    queryset = Municipality.objects.all()
    serializer_class = MunicipalitySerializers
    permission_classes = [IsSuperAdmin]

