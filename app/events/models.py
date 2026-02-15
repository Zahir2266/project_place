import os
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image

class Location(models.Model):
    name = models.CharField("Название места", max_length=255)
    lat = models.DecimalField(
        "Широта", 
        max_digits=9, 
        decimal_places=6,
        help_text="Географическая широта в десятичном формате"    
    )
    lon = models.DecimalField(
        "Долгота",
        max_digits=9,
        decimal_places=6,
        help_text="Географическая широта/долгота в десятичном формате"        
        )

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
        help_text="Оценка мероприятия от 0 до 25", 
        validators=[MinValueValidator(0), MaxValueValidator(25)],
        default=0
    )
    status = models.CharField(
        "Статус", 
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='draft',
        help_text="Опубликованные мероприятия видны всем, черновики — только админам"
    )

    def __str__(self):
        return self.title

class EventImage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField("Изображение", upload_to='events/')
    thumbnail = models.ImageField("Превью", upload_to='events/thumbnails/', editable=False, null=True)

    def save(self, *args, **kwargs):
        if self.image and not self.thumbnail:
            self.thumbnail = self.make_thumbnail(self.image)
        super().save(*args, **kwargs)

    def make_thumbnail(self, image):
        img = Image.open(image)
        
        # Уменьшение до 200px
        width, height = img.size
        if width < height:
            new_width = 200
            new_height = int(height * (200 / width))
        else:
            new_height = 200
            new_width = int(width * (200 / height))
            
        img.thumbnail((new_width, new_height), Image.LANCZOS)

        thumb_name, thumb_extension = os.path.splitext(image.name)
        thumb_extension = thumb_extension.lower()
        thumb_filename = f"{thumb_name}_thumb{thumb_extension}"

        if thumb_extension in ['.jpg', '.jpeg']:
            FTYPE = 'JPEG'
        elif thumb_extension == '.png':
            FTYPE = 'PNG'
        else:
            return None

        temp_thumb = BytesIO()
        img.save(temp_thumb, FTYPE)
        temp_thumb.seek(0)

        # Сохранение в thumbnail
        return ContentFile(temp_thumb.read(), name=thumb_filename)
    
class WeatherData(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name='weather')
    temperature = models.FloatField("Температура (°C)")
    humidity = models.FloatField("Влажность (%)")
    pressure = models.FloatField("Давление (мм рт. ст.)")
    wind_direction = models.CharField("Направление ветра", max_length=50)
    wind_speed = models.FloatField("Скорость ветра (м/с)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Погода для {self.event.title}"