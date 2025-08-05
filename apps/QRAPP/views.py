from rest_framework import viewsets
from .models import QR
from .serializers import QRSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly

class QRViewSet(viewsets.ModelViewSet):
    queryset = QR.objects.all()
    serializer_class = QRSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
