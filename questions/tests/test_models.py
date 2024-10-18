from django.test import TestCase
from django.contrib.auth import get_user_model
from questions.models import Questions, Comments
import uuid

User = get_user_model()

class QuestionsModelTestCase(TestCase):

    def setUp(self):
        # 테스트를 위한 사용자 생성
        self.user = User.objects.create_user(username='testuser', password='password')
        # Questions 모델 객체 생성
        self.question = Questions.objects.create(
            title='Test Question',
            content='This is a test question.',
            author=self.user
        )

    def test_question_creation(self):
        # 질문생성 테스트
        self.assertEqual(self.question.title, 'Test Question')
        self.assertEqual(self.question.content, 'This is a test question.')
        self.assertEqual(self.question.author, self.user)
        self.assertIsInstance(self.question.questionKey, uuid.UUID)

    def test_question_str_method(self):
        # __str__ 메소드 테스트
        self.assertEqual(str(self.question), 'Test Question')

    def test_question_auto_fields(self):
        # 자동필드 테스트 (created_at, updated_at)
        self.assertIsNotNone(self.question.created_at)
        self.assertIsNotNone(self.question.updated_at)


class CommentsModelTestCase(TestCase):

    def setUp(self):
        # 테스트를 위한 사용자, 질문 생성
        self.user = User.objects.create_user(username='testuser', password='password')
        self.question = Questions.objects.create(
            title='Test Question',
            content='This is a test question.',
            author=self.user
        )
        # Comments 모델 객체 생성
        self.comment = Comments.objects.create(
            user=self.user,
            question=self.question,
            content='This is a test comment.'
        )

    def test_comment_creation(self):
        # 댓글생성 테스트
        self.assertEqual(self.comment.content, 'This is a test comment.')
        self.assertEqual(self.comment.user, self.user)
        self.assertEqual(self.comment.question, self.question)
        self.assertIsInstance(self.comment.CommentKey, uuid.UUID)

    def test_comment_auto_fields(self):
        # 자동필드 테스트 (created_at, updated_at)
        self.assertIsNotNone(self.comment.created_at)
        self.assertIsNotNone(self.comment.updated_at)

    def test_comment_ordering(self):
        # 댓글 정렬 테스트
        comment2 = Comments.objects.create(
            user=self.user,
            question=self.question,
            content='Second test comment.'
        )
        comments = Comments.objects.all()
        self.assertEqual(comments.first(), comment2)
        self.assertEqual(comments.last(), self.comment)
