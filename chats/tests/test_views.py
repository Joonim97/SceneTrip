from django.test import TestCase
from django.urls import reverse

class ChatViewsTests(TestCase):
    
    def test_index_view_get(self):
        # index뷰에 대한 GET 요청 테스트
        response = self.client.get(reverse('chats:chat_index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat/index.html')

    def test_index_view_post(self):
        # index뷰에 대한 POST 요청 테스트
        response = self.client.post(reverse('chats:chat_index'))
        self.assertRedirects(response, reverse('chats:chat_index'))

    def test_room_view_get(self):
        room_name = 'test_room'
        # room뷰에 대한 GET 요청 테스트
        response = self.client.get(reverse('chats:room', args=[room_name]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat/room.html')
        self.assertContains(response, room_name)  # room_name이 포함되어있는지 확인

    def test_room_view_post(self):
        room_name = 'test_room'
        # room뷰에 대한 POST 요청 테스트
        response = self.client.post(reverse('chats:room', args=[room_name]))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'Message sent', 'room_name': room_name})  # JSON 응답 확인
