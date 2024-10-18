from django.test import TestCase
from django.contrib.auth import get_user_model
from journals.models import Journal, JournalImage, JournalLike, Comment, CommentLike
import uuid

User = get_user_model()

class JournalModelTest(TestCase): # 저널생성, 저널조회, 조회수 테스트

    def setUp(self): # 테스트용 데이터 생성
        self.user = User.objects.create_user(username='testuser', password='testpw')
        self.journal = Journal.objects.create(
            title="Test Journal",
            content="This is a test journal.",
            author=self.user
        )

    def test_journal_creation(self):
        self.assertEqual(self.journal.title, "Test Journal")
        self.assertEqual(self.journal.content, "This is a test journal.")
        self.assertEqual(self.journal.author, self.user)
        self.assertIsInstance(self.journal.journalKey, uuid.UUID)

    def test_journal_hit_count(self):
        self.assertEqual(self.journal.hit_count, 0)
        self.journal.hit()
        self.assertEqual(self.journal.hit_count, 1)

    def test_journal_str(self): # str(self.journal)이 'Test Journal'로 나오는지 테스트
        self.assertEqual(str(self.journal), "Test Journal")


class JournalImageModelTest(TestCase): # 이미지경로, 이미지-저널 관계 테스트

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpw')
        self.journal = Journal.objects.create(
            title="Test Journal",
            content="This is a test journal.",
            author=self.user
        )
        self.journal_image = JournalImage.objects.create(
            journal=self.journal,
            journal_image="path/to/image.jpg"
        )

    def test_journal_image_creation(self):
        self.assertEqual(self.journal_image.journal, self.journal)
        self.assertEqual(self.journal_image.journal_image, "path/to/image.jpg")


class JournalLikeModelTest(TestCase): # 저널좋아요 생성 테스트

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpw')
        self.journal = Journal.objects.create(
            title="Test Journal",
            content="This is a test journal.",
            author=self.user
        )
        self.journal_like = JournalLike.objects.create(
            journal=self.journal,
            user=self.user
        )

    def test_journal_like_creation(self):
        self.assertEqual(self.journal_like.journal, self.journal)
        self.assertEqual(self.journal_like.user, self.user)
        self.assertIsInstance(self.journal_like.journalLikeKey, uuid.UUID)


class CommentModelTest(TestCase): # 저널댓글 생성, commentKey uuid 테스트

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpw')
        self.journal = Journal.objects.create(
            title="Test Journal",
            content="This is a test journal.",
            author=self.user
        )
        self.comment = Comment.objects.create(
            journal=self.journal,
            user=self.user,
            content="This is a test comment."
        )

    def test_comment_creation(self):
        self.assertEqual(self.comment.journal, self.journal)
        self.assertEqual(self.comment.user, self.user)
        self.assertEqual(self.comment.content, "This is a test comment.")
        self.assertIsInstance(self.comment.CommentKey, uuid.UUID)


class CommentLikeModelTest(TestCase): # 저널댓글 좋아요/싫어요 작동 테스트

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpw')
        self.journal = Journal.objects.create(
            title="Test Journal",
            content="This is a test journal.",
            author=self.user
        )
        self.comment = Comment.objects.create(
            journal=self.journal,
            user=self.user,
            content="This is a test comment."
        )
        self.comment_like = CommentLike.objects.create(
            user=self.user,
            comment=self.comment,
            like_type="like"
        )

    def test_comment_like_creation(self):
        self.assertEqual(self.comment_like.comment, self.comment)
        self.assertEqual(self.comment_like.user, self.user)
        self.assertEqual(self.comment_like.like_type, "like")
