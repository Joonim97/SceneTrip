# tests.py
from django.urls import reverse
from django.test import TestCase
from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from routing import websocket_urlpatterns
from consumers import ChatConsumer
import asyncio

class RoutingTests(TestCase):

    async def asyncSetUp(self):
        self.room_name = 'testroom'
        self.url = reverse('chat:room', kwargs={'room_name': self.room_name})
        self.communicator = WebsocketCommunicator(ChatConsumer.as_asgi(), f'ws/api/chats/{self.room_name}/')

    async def test_routing(self):
        # WebSocket URL가 제대로 설정되었는지 확인
        connected, _ = await self.communicator.connect()
        self.assertTrue(connected)

        # 연결 후 URL이 올바른지 확인
        self.assertEqual(self.communicator.scope['url_route']['kwargs']['room_name'], self.room_name)

    async def asyncTearDown(self):
        # 테스트 종료 후 연결 해제
        await self.communicator.disconnect()
