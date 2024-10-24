from django.urls import path

from . import views

app_name = "chats"

urlpatterns = [
    path('', views.index, name='chat_index'),
    path('<str:room_name>/', views.room, name='room'),
]