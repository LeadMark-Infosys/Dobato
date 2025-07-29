from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action

from apps.core.views import MunicipalityTenantModelViewSet
from .models import Business, Review, Favorite
from .serializers import BusinessSerializer, ReviewSerializer, FavoriteSerializer

class BusinessViewSet(MunicipalityTenantModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        review = self.get_object()
        review.approved = True
        review.save()
        return Response({'detail': 'Review approved.'}, status=status.HTTP_200_OK)
    
class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()  
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)
