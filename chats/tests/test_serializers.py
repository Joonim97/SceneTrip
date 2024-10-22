from rest_framework.test import APITestCase
from chats.models import ShopUser, VisitorUser, ChatRoom, Message
from chats.serializers import ChatRoomSerializer, MessageSerializer

class TestSerializers(APITestCase):

    def setUp(self):
        # 테스트용 ShopUser와 VisitorUser 생성
        self.shop_user = ShopUser.objects.create(shop_user_email='shop@example.com')
        self.visitor_user = VisitorUser.objects.create(visitor_user_email='visitor@example.com')

        # 테스트용 ChatRoom 생성
        self.chat_room = ChatRoom.objects.create(shop_user=self.shop_user, visitor_user=self.visitor_user)

        # 테스트용 Message 생성
        self.message1 = Message.objects.create(room=self.chat_room, sender_email='shop@example.com', text='First message')
        self.message2 = Message.objects.create(room=self.chat_room, sender_email='visitor@example.com', text='Second message')

    def test_message_serializer(self):
        # MessageSerializer의 동작을 테스트
        message_serializer = MessageSerializer(self.message1)
        data = message_serializer.data

        # 필드 직렬화 확인
        self.assertEqual(data['room'], self.chat_room.id)
        self.assertEqual(data['sender_email'], 'shop@example.com')
        self.assertEqual(data['text'], 'First message')

    def test_chat_room_serializer(self):
        # ChatRoomSerializer의 동작을 테스트 (latest_message, opponent_email 포함)
        request = self.client.get('/', {'email': 'shop@example.com'})  # Mock request with 'shop@example.com'
        serializer_context = {'request': request}

        chat_room_serializer = ChatRoomSerializer(self.chat_room, context=serializer_context)
        data = chat_room_serializer.data

        # 필드 직렬화 확인
        self.assertEqual(data['shop_user_email'], 'shop@example.com')
        self.assertEqual(data['visitor_user_email'], 'visitor@example.com')
        self.assertEqual(data['latest_message'], 'Second message')  # 최신메시지가 'Second message'인지 확인
        self.assertEqual(data['opponent_email'], 'visitor@example.com')  # 상대방이메일 반환 확인

    def test_chat_room_opponent_email(self):
        # 상대방이메일 반환 테스트
        request = self.client.get('/', {'email': 'visitor@example.com'})  # Mock request with 'visitor@example.com'
        serializer_context = {'request': request}

        chat_room_serializer = ChatRoomSerializer(self.chat_room, context=serializer_context)
        data = chat_room_serializer.data

        # 방문자 이메일로 요청시, 상대방이 shopuser임을 확인
        self.assertEqual(data['opponent_email'], 'shop@example.com')

    def test_chat_room_messages(self):
        # ChatRoom에서 관련된 메시지들이 잘 직렬화되는지 테스트
        request = self.client.get('/', {'email': 'shop@example.com'})  # Mock request with 'shop@example.com'
        serializer_context = {'request': request}

        chat_room_serializer = ChatRoomSerializer(self.chat_room, context=serializer_context)
        data = chat_room_serializer.data

        # 메시지가 잘 직렬화되었는지 확인
        self.assertEqual(len(data['messages']), 2)
        self.assertEqual(data['messages'][0]['text'], 'First message')
        self.assertEqual(data['messages'][1]['text'], 'Second message')
