from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from communities.models import Community, Comment, CommentLike, CommunityLike, CommunityDislike

class CommunityTests(APITestCase):
    def setUp(self):
        # 사용자 생성
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        self.community = Community.objects.create(author=self.user, title='Test Community', content='Test Content')

    def test_create_comment(self):
        url = reverse('comment-create', kwargs={'community_id': self.community.id})
        data = {'content': 'Test comment'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.first().content, 'Test comment')

    def test_edit_comment(self):
        comment = Comment.objects.create(community=self.community, user=self.user, content='Original comment')
        url = reverse('comment-edit', kwargs={'comment_id': comment.id})
        data = {'content': 'Updated comment'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Comment.objects.first().content, 'Updated comment')

    def test_delete_comment(self):
        comment = Comment.objects.create(community=self.community, user=self.user, content='Test comment')
        url = reverse('comment-delete', kwargs={'comment_id': comment.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 0)

    def test_like_comment(self):
        comment = Comment.objects.create(community=self.community, user=self.user, content='Test comment')
        url = reverse('comment-like', kwargs={'comment_id': comment.id, 'like_type': 'like'})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CommentLike.objects.count(), 1)
        self.assertEqual(CommentLike.objects.first().like_type, 'like')

    def test_community_like(self):
        url = reverse('community-like', kwargs={'pk': self.community.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CommunityLike.objects.count(), 1)

    def test_community_dislike(self):
        url = reverse('community-dislike', kwargs={'pk': self.community.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CommunityDislike.objects.count(), 1)

    def test_community_report(self):
        url = reverse('community-report', kwargs={'pk': self.community.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.user, self.community.unusables.all())

    def test_community_detail_view(self):
        url = reverse('community-detail', kwargs={'pk': self.community.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Community')

    def test_community_update(self):
        url = reverse('community-detail', kwargs={'pk': self.community.id})
        data = {'title': 'Updated Title'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.community.refresh_from_db()
        self.assertEqual(self.community.title, 'Updated Title')

    def test_community_delete(self):
        url = reverse('community-detail', kwargs={'pk': self.community.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Community.objects.count(), 0)
