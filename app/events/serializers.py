from rest_framework import serializers
from .models import Location, Event, EventImage

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

    uploaded_images = serializers.ListField(
        child=serializers.ImageField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only=True, required=False
    )

    location_details = LocationSerializer(source='location', read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'images', 'uploaded_images', 
            'pub_date', 'start_date', 'end_date', 'author', 
            'location', 'location_details', 'rating', 'status'
        ]
        read_only_fields = ['author', 'pub_date']

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        event = Event.objects.create(**validated_data)
        for image in uploaded_images:
            EventImage.objects.create(event=event, image=image)
        return event