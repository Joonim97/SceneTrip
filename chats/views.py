from django.shortcuts import render
from rest_framework.response import Response
from chats.models import ChatRoom
from chats.serializers import MessageSerializer
from rest_framework.decorators import api_view

def index(request):
    return render(request, 'chat/index.html')

def room(request, room_name):
    return render(request, 'chat/room.html', {
        'room_name': room_name
    })