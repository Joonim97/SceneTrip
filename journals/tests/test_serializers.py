from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from journals.models import Journal, JournalImage, JournalLike, Comment, CommentLike
from journals.serializers import (
    CommentSerializer, 
    CommentLikeSerializer, 
    JournalImageSerializer, 
    JournalLikeSerializer, 
    JournalSerializer, 
    JournalDetailSerializer
)

User = get_user_model()

class CommentSerializerTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser", password="testpass")
        self.journal = Journal.objects.create(title="Test Journal", content="Test content", author=self.user)
        self.comment = Comment.objects.create(user=self.user, journal=self.journal, content="Test comment")
        self.comment_like = CommentLike.objects.create(user=self.user, comment=self.comment, like_type="like")

    def test_comment_serializer_data(self):
        serializer = CommentSerializer(instance=self.comment)
        data = serializer.data
        self.assertEqual(data["content"], "Test comment")
        self.assertEqual(data["like_count"], 1)
        self.assertEqual(data["dislike_count"], 0)
        self.assertIn("replies", data)

    def test_comment_serializer_create(self):
        data = {
            "content": "Another test comment",
            "parent": None
        }
        serializer = CommentSerializer(data=data, context={"request": self.client.request()})
        serializer.is_valid()
        comment = serializer.save(journal=self.journal)
        self.assertEqual(comment.content, "Another test comment")
        self.assertEqual(comment.journal, self.journal)

class CommentLikeSerializerTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser", password="testpass")
        self.journal = Journal.objects.create(title="Test Journal", content="Test content", author=self.user)
        self.comment = Comment.objects.create(user=self.user, journal=self.journal, content="Test comment")
        self.comment_like = CommentLike.objects.create(user=self.user, comment=self.comment, like_type="like")

    def test_comment_like_serializer_data(self):
        serializer = CommentLikeSerializer(instance=self.comment_like)
        data = serializer.data
        self.assertEqual(data["like_type"], "like")

class JournalImageSerializerTest(APITestCase):
    def setUp(self):
        self.journal = Journal.objects.create(title="Test Journal", content="Test content")

    def test_journal_image_serializer_data(self):
        journal_image = JournalImage.objects.create(journal=self.journal, journal_image="test_image.jpg")
        serializer = JournalImageSerializer(instance=journal_image)
        data = serializer.data
        self.assertEqual(data["journal_image"], "test_image.jpg")

class JournalLikeSerializerTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser", password="testpass")
        self.journal = Journal.objects.create(title="Test Journal", content="Test content", author=self.user)
        self.journal_like = JournalLike.objects.create(user=self.user, journal=self.journal)

    def test_journal_like_serializer_data(self):
        serializer = JournalLikeSerializer(instance=self.journal_like)
        data = serializer.data
        self.assertEqual(data["user"], self.user.id)
        self.assertIn("journalLikeKey", data)

class JournalSerializerTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser", password="testpass")
        self.journal = Journal.objects.create(title="Test Journal", content="Test content", author=self.user)

    def test_journal_serializer_data(self):
        serializer = JournalSerializer(instance=self.journal)
        data = serializer.data
        self.assertEqual(data["title"], "Test Journal")
        self.assertEqual(data["content"], "Test content")
        self.assertEqual(data["hit_count"], 0)
        self.assertEqual(data["likes_count"], 0)

class JournalDetailSerializerTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser", password="testpass")
        self.journal = Journal.objects.create(title="Test Journal", content="Test content", author=self.user)
        self.comment = Comment.objects.create(user=self.user, journal=self.journal, content="Test comment")

    def test_journal_detail_serializer_data(self):
        serializer = JournalDetailSerializer(instance=self.journal)
        data = serializer.data
        self.assertEqual(data["title"], "Test Journal")
        self.assertEqual(data["comments_count"], 1)
        self.assertEqual(data["comments"][0]["content"], "Test comment")
