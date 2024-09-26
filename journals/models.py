from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.conf import settings

User=get_user_model()

class Journal(models.Model):
    id=models.IntegerField(primary_key=True)
    title = models.CharField(max_length=40)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # author = models.ForeignKey(User, on_delete=models.CASCADE)
    # image = models.ImageField(upload_to="%Y/%m/%d")