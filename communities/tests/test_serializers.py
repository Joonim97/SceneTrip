from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from communities.models import (
    Community, Comment, CommentLike, CommunityLike, CommunityDislike, CommunityImage
)
from communities.serializers import (
    CommentSerializer, CommentLikeSerializer, CommunityLikeSerializer, 
    CommunityDislikeSerializer, CommunitySerializer, CommunityDetailSerializer
)
from django.utils import timezone

User = get_user_model()

class CommunitySerializerTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.community = Community.objects.create(
            category='정보',
            title='Test Community',
            author=self.user,
            content='Test content for community'
        )
        self.comment = Comment.objects.create(
            user=self.user,
            community=self.community,
            content='Test comment'
        )
        self.community_image = CommunityImage.objects.create(
            community=self.community,
            community_image='path/to/image.jpg'
        )
        self.community_like = CommunityLike.objects.create(
            community=self.community,
            user=self.user
        )
        self.community_dislike = CommunityDislike.objects.create(
            community=self.community,
            user=self.user
        )
        self.comment_like = CommentLike.objects.create(
            comment=self.comment,
            user=self.user,
            like_type='like'
        )

    def test_comment_serializer(self):
        # CommentSerializer 테스트
        serializer = CommentSerializer(instance=self.comment)
        data = serializer.data
        self.assertEqual(data['content'], 'Test comment')
        self.assertEqual(data['like_count'], 1)  # 1개의 좋아요
        self.assertEqual(data['dislike_count'], 0)
        self.assertEqual(data['replies'], [])  # 답글 없음

    def test_comment_like_serializer(self):
        # CommentLikeSerializer 테스트
        serializer = CommentLikeSerializer(instance=self.comment_like)
        data = serializer.data
        self.assertEqual(data['like_type'], 'like')
        self.assertEqual(data['comment'], self.comment.id)

    def test_community_like_serializer(self):
        # CommunityLikeSerializer 테스트
        serializer = CommunityLikeSerializer(instance=self.community_like)
        data = serializer.data
        self.assertEqual(data['user'], self.user.id)

    def test_community_dislike_serializer(self):
        # CommunityDislikeSerializer 테스트
        serializer = CommunityDislikeSerializer(instance=self.community_dislike)
        data = serializer.data
        self.assertEqual(data['user'], self.user.id)

    def test_community_serializer(self):
        # CommunitySerializer 테스트
        serializer = CommunitySerializer(instance=self.community)
        data = serializer.data
        self.assertEqual(data['title'], 'Test Community')
        self.assertEqual(data['author'], self.user.username)
        self.assertEqual(data['comments_count'], 1)  # 1개의 댓글
        self.assertEqual(data['unusables_count'], 0)  # 신고 없음
        self.assertEqual(data['likes_count'], 1)  # 1개의 좋아요
        self.assertEqual(data['dislikes_count'], 1)  # 1개의 싫어요
        self.assertEqual(len(data['likes']), 1)
        self.assertEqual(len(data['dislikes']), 1)
        self.assertEqual(len(data['community_images']), 1)

    def test_community_detail_serializer(self):
        # CommunityDetailSerializer 테스트
        serializer = CommunityDetailSerializer(instance=self.community)
        data = serializer.data
        self.assertEqual(data['title'], 'Test Community')
        self.assertEqual(data['comments_count'], 1)  # 1개의 댓글
        self.assertEqual(len(data['comments']), 1)  # 댓글 1개 포함
        self.assertEqual(len(data['community_images']), 1)

    def test_create_comment_with_serializer(self):
        # CommentSerializer를 통해 댓글 생성 테스트
        data = {
            'community': self.community.id,
            'content': 'New comment'
        }
        serializer = CommentSerializer(data=data, context={'request': self.client.request()})
        self.assertTrue(serializer.is_valid())
        comment = serializer.save(user=self.user)
        self.assertEqual(comment.content, 'New comment')
        self.assertEqual(comment.community, self.community)
        self.assertEqual(comment.user, self.user)
