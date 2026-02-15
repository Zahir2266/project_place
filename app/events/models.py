from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Location(models.Model):
    name = models.CharField("Название места", max_length=255)
    lat = models.DecimalField("Широта", max_digits=9, decimal_places=6)
    lon = models.DecimalField("Долгота", max_digits=9, decimal_places=6)

    def __str__(self):
        return self.name

class Event(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('published', 'Опубликовано'),
    ]

    title = models.CharField("Название", max_length=255)
    description = models.TextField("Описание")
    
    
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)
    start_date = models.DateTimeField("Дата начала проведения")
    end_date = models.DateTimeField("Дата завершения проведения")
    
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='events')
    
    rating = models.PositiveIntegerField(
        "Рейтинг", 
        validators=[MinValueValidator(0), MaxValueValidator(25)],
        default=0
    )
    status = models.CharField("Статус", max_length=10, choices=STATUS_CHOICES, default='draft')

    def __str__(self):
        return self.title

class EventImage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField("Изображение", upload_to='events/')