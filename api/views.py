from rest_framework import viewsets, permissions

from api import models, serializers


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = models.Profile.objects.filter(active=True)
    serializer_class = serializers.ProfileSerializer
    permission_classes = [permissions.DjangoModelPermissions]
