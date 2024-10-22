# tests.py
from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from django.test import TestCase
from asgiref.testing import ApplicationCommunicator
from consumers import ChatConsumer
import json

class ChatConsumerTests(TestCase):

    async def asyncSetUp(self):
        self.room_name = 'test_room'
        self.channel_layer = get_channel_layer()
        self.communicator = WebsocketCommunicator(ChatConsumer.as_asgi(), {
            'type': 'websocket.connect',
            'url_route': {
                'kwargs': {
                    'room_name': self.room_name
                }
            }
        })

    async def test_connect(self):
        # WebSocket 연결 테스트
        connected, _ = await self.communicator.connect()
        self.assertTrue(connected)

    async def test_disconnect(self):
        # WebSocket 연결 후 disconnect 테스트
        await self.communicator.connect()
        await self.communicator.disconnect()
        # WebSocket이 제대로 종료되었는지 확인 (추가적인 테스트 필요)

    async def test_receive_message(self):
        # WebSocket 메시지 수신 및 방 그룹으로 전송 테스트
        await self.communicator.connect()
        message = {'message': 'Hello'}
        await self.communicator.send_json_to(message)

        # 방 그룹에서 메시지를 수신할 수 있는지 테스트
        response = await self.communicator.receive_json_from()
        self.assertEqual(response, message)

    async def test_chat_message(self):
        # 방 그룹으로 메시지를 전송하고 확인 테스트
        await self.communicator.connect()
        message = {'message': 'Hello group'}
        await self.communicator.send_json_to(message)

        # 채팅 메시지 수신
        response = await self.communicator.receive_json_from()
        self.assertEqual(response, message)

    async def asyncTearDown(self):
        # 테스트 종료 후 연결 해제
        await self.communicator.disconnect()
