from django.urls import path
from .views import ChatRoomListCreateView, MessageListCreateView

app_name = 'chats'

urlpatterns = [
    path('rooms/', ChatRoomListCreateView.as_view(), name='chat-room-list-create'),  # 채팅방 리스트 및 생성
    path('rooms/<int:id>/messages/', MessageListCreateView.as_view(), name='message-list'), 
]