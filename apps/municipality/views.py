from rest_framework.viewsets import ModelViewSet
from .serializers import *
from .models import * 
from apps.core.permissions import IsSuperUser

class MunicipalityViewSet(ModelViewSet):
    queryset = Municipality.objects.all()
    serializer_class = MunicipalitySerializers
    permission_classes = [IsSuperUser]

