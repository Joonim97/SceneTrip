from django.test import TestCase
from chats.models import ShopUser, VisitorUser, ChatRoom, Message

class TestModels(TestCase):

    def setUp(self):
        # ShopUser와 VisitorUser 객체 생성
        self.shop_user = ShopUser.objects.create(shop_user_email='shop@example.com')
        self.visitor_user = VisitorUser.objects.create(visitor_user_email='visitor@example.com')
        
        # ChatRoom 객체 생성
        self.chat_room = ChatRoom.objects.create(shop_user=self.shop_user, visitor_user=self.visitor_user)

    def test_shop_user_creation(self):
        # ShopUser 생성 확인
        self.assertEqual(self.shop_user.shop_user_email, 'shop@example.com')
    
    def test_visitor_user_creation(self):
        # VisitorUser 생성 확인
        self.assertEqual(self.visitor_user.visitor_user_email, 'visitor@example.com')

    def test_chat_room_creation(self):
        # ChatRoom 생성 확인
        chat_room = ChatRoom.objects.get(id=self.chat_room.id)
        self.assertEqual(chat_room.shop_user, self.shop_user)
        self.assertEqual(chat_room.visitor_user, self.visitor_user)

    def test_unique_together_constraint(self):
        # 같은 shop_user와 visitor_user로 Chatroom을 중복생성할 때 예외가 발생하는지 확인
        with self.assertRaises(Exception):
            ChatRoom.objects.create(shop_user=self.shop_user, visitor_user=self.visitor_user)

    def test_message_creation(self):
        # Message가 ChatRoom에 속하고, 올바르게 생성되는지 확인
        message = Message.objects.create(
            room=self.chat_room,
            sender_email='sender@example.com',
            text='Hello, this is a test message.'
        )
        self.assertEqual(message.room, self.chat_room)
        self.assertEqual(message.sender_email, 'sender@example.com')
        self.assertEqual(message.text, 'Hello, this is a test message.')

    def test_chat_room_message_relation(self):
        # 여러 메시지를 ChatRoom에 추가하고, related_name을 통해 메시지를 가져오는지 확인
        message1 = Message.objects.create(
            room=self.chat_room,
            sender_email='sender1@example.com',
            text='First message.'
        )
        message2 = Message.objects.create(
            room=self.chat_room,
            sender_email='sender2@example.com',
            text='Second message.'
        )

        # ChatRoom에서 관련메시지들이 제대로 조회되는지 확인
        messages = self.chat_room.messages.all()
        self.assertEqual(messages.count(), 2)
        self.assertIn(message1, messages)
        self.assertIn(message2, messages)
