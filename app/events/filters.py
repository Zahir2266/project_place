from django_filters import rest_framework as filters
from .models import Event, Location

class EventFilter(filters.FilterSet):
    # Диапазон даты начала
    start_date = filters.DateTimeFromToRangeFilter(
        label="Дата начала: диапазон (ГГГГ-ММ-ДД ЧЧ:ММ)"
    )
    
    # Диапазон даты завершения
    end_date = filters.DateTimeFromToRangeFilter(
        label="Дата завершения: диапазон (ГГГГ-ММ-ДД ЧЧ:ММ)"
    )
    
    # Рейтинг
    rating = filters.RangeFilter(
        label="Рейтинг: диапазон (от 0 до 25)"
    )
    
    # Множественный выбор мест проведения
    location = filters.ModelMultipleChoiceFilter(
        queryset=Location.objects.all(),
        label='Места проведения (можно выбрать несколько ID)'
    )

    class Meta:
        model = Event
        fields = ['start_date', 'end_date', 'rating', 'location', 'status']