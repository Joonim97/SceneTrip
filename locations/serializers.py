from rest_framework import serializers
from .models import Location, LocationSave


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = "__all__"

class LocationSaveSerializer(serializers.ModelSerializer):
    location = LocationSerializer()  # LocationSerializer를 통해 Location 필드를 직렬화

    class Meta:
        model = LocationSave
        fields = ['user', 'location', 'saved_at']
