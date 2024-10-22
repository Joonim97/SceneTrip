from django.test import SimpleTestCase
from django.urls import reverse, resolve
from chats import views

class TestChatUrls(SimpleTestCase):

    def test_chat_index_url(self):
        # URL 가져오기 위해 reverse 함수 사용
        url = reverse('chats:chat_index')
        self.assertEqual(resolve(url).func, views.index)
        # URL패턴이 views.index로 연결되는지 확인

    def test_room_url(self):
        room_name = 'test_room'
        # URL을 reverse로 생성, room_name 파라미터 포함
        url = reverse('chats:room', args=[room_name])
        resolved_func = resolve(url).func
        self.assertEqual(resolved_func, views.room)
        # URL패턴이 views.room으로 연결되는지 확인
