from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Location
from .serializers import LocationSerializer

class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

    # Ограничение на доступа только суперюзу
    permission_classes = [permissions.IsAdminUser]
