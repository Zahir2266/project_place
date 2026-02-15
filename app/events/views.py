from django.shortcuts import render
from rest_framework import viewsets, permissions, filters as drf_filters
from .models import Location, Event
from .serializers import LocationSerializer, EventSerializer
from .filters import EventFilter
from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema(tags=['Места проведения'])
@extend_schema_view(
    list=extend_schema(summary="Список мест", description="Доступно только администратору"),
    create=extend_schema(summary="Создать новое место", description="Доступно только администратору"),
    retrieve=extend_schema(summary="Просмотр одного места", description="Доступно только администратору"),
    update=extend_schema(summary="Изменить место", description="Доступно только администратору"),
    partial_update=extend_schema(summary="Изменить место (частично)", description="Доступно только администратору"),
    destroy=extend_schema(summary="Удалить место", description="Доступно только администратору"),
)
class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

    # Ограничение на доступа только суперюзу
    permission_classes = [permissions.IsAdminUser]



@extend_schema(tags=['Мероприятия'])
@extend_schema_view(
    list=extend_schema(
        summary="Получить список всех мероприятий", 
        description="Обычные пользователи видят только опубликованные мероприятия. Суперпользователи видят всё."
    ),
    retrieve=extend_schema(
        summary="Детальная информация о мероприятии",
        description="Позволяет увидеть погоду, рейтинг и полный список изображений."
    ),
    # create -  описание загрузки файлов
    create=extend_schema(
        summary="Создать новое мероприятие",
        description="Доступно только администратору. Можно загрузить несколько изображений в поле uploaded_images.",
        request={
            'multipart/form-data': EventSerializer,
        },
    ),
    update=extend_schema(summary="Редактировать мероприятие", description="Только для администратора"),
    partial_update=extend_schema(summary="Редактировать мероприятие (частично)", description="Только для администратора"),
    destroy=extend_schema(summary="Удалить мероприятие", description="Только для администратора"),
)
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