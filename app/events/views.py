from django.shortcuts import render
from rest_framework import viewsets, permissions, filters as drf_filters
from .models import Location, Event
from .serializers import LocationSerializer, EventSerializer
from .filters import EventFilter
from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema(tags=['Места проведения'])
@extend_schema_view(
    list=extend_schema(summary="Список мест"),
    create=extend_schema(
        summary="Создать место",
        request=LocationSerializer,
    ),
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
        description="Доступно только администратору. Поле uploaded_images позволяет выбрать несколько файлов.",
        
        # Ручное переопределение схемы запроса для поддержки multipart/form-data (загрузка файлов)
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string'},
                    'description': {'type': 'string'},
                    'location': {'type': 'integer'},
                    'start_date': {'type': 'string', 'format': 'date-time'},
                    'end_date': {'type': 'string', 'format': 'date-time'},
                    'rating': {'type': 'integer', 'minimum': 0, 'maximum': 25},
                    'status': {'type': 'string', 'enum': ['draft', 'published']},
                    'uploaded_images': {
                        'type': 'array',
                        'items': {'type': 'string', 'format': 'binary'}
                    }
                },
                'required': ['title', 'location', 'start_date', 'end_date']
            }
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

    # Тригер для email при публикации
    def perform_update(self, serializer):
        instance = serializer.save()
        if instance.status == 'published':
            from .tasks import send_event_email_task
            send_event_email_task.delay(
                event_id=instance.id,
                recipient_list=['admin@example.com'],
                subject=f"Опубликовано: {instance.title}",
                message=f"Мероприятие {instance.title} теперь доступно для всех."
            )