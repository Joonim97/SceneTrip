from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from communities.models import Community, Comment, CommentLike
from django.contrib.auth.models import User

class CommunityURLsTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.community = Community.objects.create(title='Test Community', content='Test Content', author=self.user)
        self.comment = Comment.objects.create(community=self.community, user=self.user, content='Test Comment')
    
    def test_community_comment_list_create(self):
        # 특정 게시물 댓글 조회
        url = reverse('communities:community-comment', kwargs={'community_id': self.community.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 댓글 생성
        self.client.force_authenticate(user=self.user)
        data = {'content': 'New comment', 'user': self.user.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_community_reply_create(self):
        # 대댓글 생성
        url = reverse('communities:community-reply', kwargs={'community_id': self.community.id, 'parent_id': self.comment.id})
        self.client.force_authenticate(user=self.user)
        data = {'content': 'Reply to comment', 'user': self.user.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_community_comment_detail_update_delete(self):
        # 댓글 수정
        url = reverse('communities:community-comment_detatil', kwargs={'comment_id': self.comment.id})
        self.client.force_authenticate(user=self.user)
        data = {'content': 'Updated comment'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 댓글 삭제
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_community_comment_like(self):
        # 댓글 좋아요
        url = reverse('communities:community-comment-like', kwargs={'comment_id': self.comment.id, 'like_type': 'like'})
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 댓글 싫어요
        url = reverse('communities:community-comment-like', kwargs={'comment_id': self.comment.id, 'like_type': 'dislike'})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_community_list_create(self):
        # 커뮤니티 글 목록 조회
        url = reverse('communities:community-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 커뮤니티 글 작성
        self.client.force_authenticate(user=self.user)
        data = {'title': 'New Community', 'content': 'Community Content', 'author': self.user.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_community_detail(self):
        # 커뮤니티 글 상세 조회
        url = reverse('communities:community-detail', kwargs={'pk': self.community.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_community_unusable(self):
        # 커뮤니티 글 신고
        url = reverse('communities:unusable', kwargs={'pk': self.community.id})
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_community_like(self):
        # 커뮤니티 글 좋아요
        url = reverse('communities:journal_like', kwargs={'pk': self.community.id})
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_community_dislike(self):
        # 커뮤니티 글 싫어요
        url = reverse('communities:journal_dislike', kwargs={'pk': self.community.id})
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
