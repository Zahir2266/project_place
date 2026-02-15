from django_filters import rest_framework as filters
from .models import Event, Location

class EventFilter(filters.FilterSet):
    # Диапазон даты начала
    start_date = filters.DateTimeFromToRangeFilter()
    
    # Диапазон даты завершения
    end_date = filters.DateTimeFromToRangeFilter()
    
    # Рейтинг
    rating = filters.RangeFilter()
    
    # Множественный выбор мест проведения
    location = filters.ModelMultipleChoiceFilter(
        queryset=Location.objects.all()
    )

    class Meta:
        model = Event
        fields = ['start_date', 'end_date', 'rating', 'location', 'status']