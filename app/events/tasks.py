import requests
from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import Event, WeatherData

@shared_task
def send_event_email_task(event_id, recipient_list, subject, message):
    """Задача 1: Отправка Email при публикации"""
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        fail_silently=False,
    )

@shared_task
def check_for_publication():
    """Задача 2: Автопубликация мероприятий при наступлении даты"""
    now = timezone.now()

    events_to_publish = Event.objects.filter(
        status='draft', 
        pub_date__lte=now
    )
    
    for event in events_to_publish:
        event.status = 'published'
        event.save()

        print(f"Event '{event.title}' has been published automatically.")

@shared_task
def update_weather_task():
    """Задача 3: Получение погоды для мест проведения"""
    events = Event.objects.filter(status='published')
    
    for event in events:
        loc = event.location
        url = f"https://api.open-meteo.com/v1/forecast?latitude={loc.lat}&longitude={loc.lon}&current_weather=true&hourly=relativehumidity_2m,surface_pressure"
        
        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            current = data['current_weather']
            
            # Сохраняем данные
            WeatherData.objects.update_or_create(
                event=event,
                defaults={
                    'temperature': current['temperature'],
                    'wind_speed': current['windspeed'],
                    'wind_direction': str(current['winddirection']),
                    'humidity': 50.0,
                    'pressure': 760.0,
                }
            )
        except Exception as e:
            print(f"Error fetching weather for {event.title}: {e}")