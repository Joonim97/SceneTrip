from rest_framework.test import APITestCase
from questions.models import Questions, Comments
from questions.serializers import CommentSerializer, QuestionSerializer, QuestionDetailSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class CommentSerializerTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.question = Questions.objects.create(author=self.user, title="Test Question", content="This is a test.")
        self.comment = Comments.objects.create(user=self.user, question=self.question, content="Test comment")

    def test_comment_serializer_fields(self):
        # CommentSerializer 필드 테스트
        serializer = CommentSerializer(instance=self.comment)
        data = serializer.data

        self.assertEqual(set(data.keys()), {'id', 'question', 'user', 'content', 'created_at', 'replies'})
        self.assertEqual(data['content'], "Test comment")

    def test_comment_serializer_create(self):
        # CommentSerializer 생성 테스트
        data = {'question': self.question.id, 'content': 'Another comment'}
        serializer = CommentSerializer(data=data, context={'request': self.client.request()})
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()

        self.assertEqual(comment.content, 'Another comment')
        self.assertEqual(comment.user, self.user)  # 요청 컨텍스트에서 유저가 추가되었는지 확인

class QuestionSerializerTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.question = Questions.objects.create(author=self.user, title="Test Question", content="This is a test.")

    def test_question_serializer_fields(self):
        # QuestionSerializer 필드 테스트
        serializer = QuestionSerializer(instance=self.question)
        data = serializer.data

        self.assertEqual(set(data.keys()), {'questionKey', 'title', 'author', 'content', 'image', 'created_at', 'comments_count'})
        self.assertEqual(data['title'], "Test Question")
        self.assertEqual(data['author'], self.user.nickname)

    def test_question_serializer_comments_count(self):
        # comments_count가 제대로 동작하는지 테스트
        comment = Comments.objects.create(user=self.user, question=self.question, content="Test comment")
        serializer = QuestionSerializer(instance=self.question)
        data = serializer.data

        self.assertEqual(data['comments_count'], 1)  # 댓글이 하나 있는지 확인

class QuestionDetailSerializerTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.question = Questions.objects.create(author=self.user, title="Test Question", content="This is a test.")
        self.comment = Comments.objects.create(user=self.user, question=self.question, content="Test comment")

    def test_question_detail_serializer_fields(self):
        # QuestionDetailSerializer 필드 테스트
        serializer = QuestionDetailSerializer(instance=self.question)
        data = serializer.data

        self.assertEqual(set(data.keys()), {'questionKey', 'title', 'author', 'content', 'image', 'created_at', 'comments_count', 'comments'})
        self.assertEqual(data['title'], "Test Question")
        self.assertEqual(len(data['comments']), 1)  # 댓글이 하나 있는지 확인
        self.assertEqual(data['comments'][0]['content'], "Test comment")
