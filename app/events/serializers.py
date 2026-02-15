from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field, OpenApiTypes
from .models import Location, Event, EventImage, WeatherData

class WeatherSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherData
        fields = [
            'temperature', 'humidity', 'pressure', 
            'wind_direction', 'wind_speed', 'created_at'
        ]

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name', 'lat', 'lon']

class EventImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventImage
        fields = ['id', 'image', 'thumbnail']

class EventSerializer(serializers.ModelSerializer):

    images = EventImageSerializer(many=True, read_only=True)
    weather = WeatherSerializer(read_only=True) 

    uploaded_images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False, use_url=False),
        write_only=True,
        required=False,
        label="Загрузка изображений"
    )

    location_details = LocationSerializer(source='location', read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'images', 'uploaded_images', 
            'pub_date', 'start_date', 'end_date', 'author', 
            'location', 'location_details', 'weather',
            'rating', 'status'
        ]
        read_only_fields = ['author', 'pub_date', 'weather']

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        event = Event.objects.create(**validated_data)
        for image in uploaded_images:
            EventImage.objects.create(event=event, image=image)
        return event