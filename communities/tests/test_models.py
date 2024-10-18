from django.test import TestCase
from django.contrib.auth import get_user_model
from communities.models import (
    Community, CommunityImage, Comment, CommentLike,
    CommunityLike, CommunityDislike
)
import uuid

User = get_user_model()

class CommunityModelTestCase(TestCase):
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

    def test_community_creation(self):
        # Community 모델 생성 테스트
        self.assertEqual(self.community.title, 'Test Community')
        self.assertEqual(self.community.author, self.user)
        self.assertEqual(self.community.category, '정보')
        self.assertTrue(isinstance(self.community.communityKey, uuid.UUID))  # UUID 검증
        self.assertEqual(str(self.community), 'Test Community')

    def test_community_image_creation(self):
        # CommunityImage 모델 생성 테스트
        community_image = CommunityImage.objects.create(
            community=self.community,
            community_image='path/to/image.jpg'
        )
        self.assertEqual(community_image.community, self.community)
        self.assertEqual(community_image.community_image, 'path/to/image.jpg')

    def test_comment_creation(self):
        # Comment 모델 생성 테스트
        self.assertEqual(self.comment.content, 'Test comment')
        self.assertEqual(self.comment.user, self.user)
        self.assertEqual(self.comment.community, self.community)
        self.assertTrue(isinstance(self.comment.CommentKey, uuid.UUID))  # UUID 검증
        self.assertEqual(str(self.comment), f'Comment by {self.user.username} on {self.community.title}')

    def test_comment_like_creation(self):
        # CommentLike 모델 생성 테스트
        comment_like = CommentLike.objects.create(
            user=self.user,
            comment=self.comment,
            like_type='like'
        )
        self.assertEqual(comment_like.user, self.user)
        self.assertEqual(comment_like.comment, self.comment)
        self.assertEqual(comment_like.like_type, 'like')

    def test_community_like_creation(self):
        # CommunityLike 모델 생성 테스트
        community_like = CommunityLike.objects.create(
            community=self.community,
            user=self.user
        )
        self.assertEqual(community_like.community, self.community)
        self.assertEqual(community_like.user, self.user)
        self.assertTrue(isinstance(community_like.communityLikeKey, uuid.UUID))  # UUID 검증

    def test_community_dislike_creation(self):
        # CommunityDislike 모델 생성 테스트
        community_dislike = CommunityDislike.objects.create(
            community=self.community,
            user=self.user
        )
        self.assertEqual(community_dislike.community, self.community)
        self.assertEqual(community_dislike.user, self.user)
        self.assertTrue(isinstance(community_dislike.communityDislikeKey, uuid.UUID))  # UUID 검증

    def test_unique_together_constraints(self):
        # CommunityLike, CommunityDislike, CommentLike 의 unique_together 제약 조건 테스트
        CommunityLike.objects.create(community=self.community, user=self.user)
        with self.assertRaises(Exception):  # 중복 좋아요 시도 시 예외 발생 테스트
            CommunityLike.objects.create(community=self.community, user=self.user)

        CommunityDislike.objects.create(community=self.community, user=self.user)
        with self.assertRaises(Exception):  # 중복 싫어요 시도 시 예외 발생 테스트
            CommunityDislike.objects.create(community=self.community, user=self.user)

        CommentLike.objects.create(comment=self.comment, user=self.user, like_type='like')
        with self.assertRaises(Exception):  # 중복 댓글 좋아요 시도 시 예외 발생 테스트
            CommentLike.objects.create(comment=self.comment, user=self.user, like_type='like')
