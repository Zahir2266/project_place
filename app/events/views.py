from django.shortcuts import render
from rest_framework import viewsets, permissions, filters as drf_filters
from .models import Location, Event
from .serializers import LocationSerializer, EventSerializer
from .filters import EventFilter


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

    # Ограничение на доступа только суперюзу
    permission_classes = [permissions.IsAdminUser]

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    filterset_class = EventFilter
    # Поиск по названию или месту
    search_fields = ['title', 'location__name']  
    # Сортировка
    ordering_fields = ['title', 'start_date', 'end_date'] 
     # Сортировка по умолчанию
    ordering = ['title']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        user = self.request.user
        queryset = Event.objects.all()
        
        # Не суперюзер - показ опубликованные
        if not (user.is_authenticated and user.is_staff):
            queryset = queryset.filter(status='published')
        
        return queryset

    def perform_create(self, serializer):
        # Автор - текущий пользователь
        serializer.save(author=self.request.user)