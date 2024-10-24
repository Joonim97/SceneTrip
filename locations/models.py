from django.db import models
from django.contrib.auth import get_user_model


class Location(models.Model):
    id = models.IntegerField(primary_key=True)
    media_type = models.CharField(max_length=20)
    title = models.CharField(max_length=300)
    place_name = models.CharField(max_length=300)
    place_type = models.CharField(max_length=100)
    place_description = models.TextField(max_length=300)
    opening_hours = models.TextField(max_length=300)
    break_time = models.CharField(max_length=100)
    closed_day = models.CharField(max_length=100)
    address = models.CharField(max_length=300)
    latitude = models.FloatField(max_length=8)
    longitude = models.FloatField(max_length=10)
    tel = models.CharField(max_length=20)
    created_at = models.CharField(max_length=10)
    save_count = models.IntegerField(default=0)


class LocationSave(models.Model):
    User = get_user_model()

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="location_save")
    location = models.ForeignKey(Location, on_delete=models.CASCADE, default=1)
    saved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'location')