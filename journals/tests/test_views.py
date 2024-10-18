from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from models import Journal, Comment, CommentLike, JournalLike

User = get_user_model()

class JournalListAPIViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass", grade="author")
        self.journal = Journal.objects.create(title="Test Journal", content="Test Content", author=self.user)
        self.url = reverse('journal-list')  # 'journal-list'라는 URL 네임이 설정되어 있다고 가정

    def test_journal_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_journal_search(self):
        response = self.client.get(self.url, {'search': 'Test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Test Journal', response.data[0]['title'])

    def test_journal_create(self):
        self.client.login(username="testuser", password="testpass")
        data = {
            'title': 'New Journal',
            'content': 'New Content'
        }
        response = self.client.post(self.url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_journal_create_without_author_grade(self):
        self.user.grade = "user"
        self.user.save()
        self.client.login(username="testuser", password="testpass")
        data = {
            'title': 'New Journal',
            'content': 'New Content'
        }
        response = self.client.post(self.url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class JournalDetailAPIViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass", grade="author")
        self.journal = Journal.objects.create(title="Test Journal", content="Test Content", author=self.user)
        self.url = reverse('journal-detail', kwargs={'pk': self.journal.pk})

    def test_journal_detail(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_journal_update(self):
        self.client.login(username="testuser", password="testpass")
        data = {
            'title': 'Updated Title',
            'content': 'Updated Content'
        }
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Title')

    def test_journal_delete(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class JournalLikeAPIViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass", grade="author")
        self.journal = Journal.objects.create(title="Test Journal", content="Test Content", author=self.user)
        self.url = reverse('journal-like', kwargs={'pk': self.journal.pk})

    def test_journal_like(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_journal_unlike(self):
        self.client.login(username="testuser", password="testpass")
        JournalLike.objects.create(journal=self.journal, user=self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CommentViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass", grade="author")
        self.journal = Journal.objects.create(title="Test Journal", content="Test Content", author=self.user)
        self.comment = Comment.objects.create(journal=self.journal, user=self.user, content="Test Comment")
        self.url = reverse('journal-comments', kwargs={'journal_id': self.journal.pk})

    def test_comment_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_comment_create(self):
        self.client.login(username="testuser", password="testpass")
        data = {
            'content': 'New Comment'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_comment_update(self):
        self.client.login(username="testuser", password="testpass")
        comment_url = reverse('comment-detail', kwargs={'comment_id': self.comment.pk})
        data = {
            'content': 'Updated Comment'
        }
        response = self.client.put(comment_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], 'Updated Comment')

    def test_comment_delete(self):
        self.client.login(username="testuser", password="testpass")
        comment_url = reverse('comment-detail', kwargs={'comment_id': self.comment.pk})
        response = self.client.delete(comment_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class CommentLikeViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass", grade="author")
        self.journal = Journal.objects.create(title="Test Journal", content="Test Content", author=self.user)
        self.comment = Comment.objects.create(journal=self.journal, user=self.user, content="Test Comment")
        self.url = reverse('comment-like', kwargs={'comment_id': self.comment.pk, 'like_type': 'like'})

    def test_comment_like(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_comment_dislike_and_delete(self):
        self.client.login(username="testuser", password="testpass")
        dislike_url = reverse('comment-like', kwargs={'comment_id': self.comment.pk, 'like_type': 'dislike'})
        for _ in range(100):
            CommentLike.objects.create(comment=self.comment, user=self.user, like_type='dislike')
        response = self.client.post(dislike_url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(Comment.objects.filter(id=self.comment.pk).exists())


class DislikedCommentsViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass", grade="author")
        self.journal = Journal.objects.create(title="Test Journal", content="Test Content", author=self.user)
        self.comment = Comment.objects.create(journal=self.journal, user=self.user, content="Test Comment")
        self.url = reverse('disliked-comments', kwargs={'min_dislikes': 10})

    def test_disliked_comments(self):
        for _ in range(10):
            CommentLike.objects.create(comment=self.comment, user=self.user, like_type='dislike')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
