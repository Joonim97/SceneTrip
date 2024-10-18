from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from questions.models import Questions, Comments

User = get_user_model()

class QuestionListViewTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.question_data = {
            'title': 'Test Question',
            'content': 'This is a test question.',
        }

    def test_get_questions(self):
        # 질문 목록 조회 테스트
        Questions.objects.create(author=self.user, **self.question_data)
        response = self.client.get(reverse('questions:question-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_question_authenticated(self):
        # 질문 생성 테스트
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('questions:question-list'), self.question_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Questions.objects.count(), 1)

    def test_create_question_unauthenticated(self):
        # 권한외 사용자로 질문생성 테스트
        response = self.client.post(reverse('questions:question-list'), self.question_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class QuestionDetailAPIViewTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.other_user = User.objects.create_user(username='otheruser', password='otherpassword')
        self.question = Questions.objects.create(author=self.user, title='Test Question', content='Test Content')

    def test_get_question_detail_authenticated(self):
        # 본인의 질문상세조회 테스트
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('questions:question-detail', args=[self.question.questionKey]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Question')

    def test_get_question_detail_unauthenticated(self):
        # 다른 사용자가 질문상세조회 테스트
        response = self.client.get(reverse('questions:question-detail', args=[self.question.questionKey]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_question_authenticated_owner(self):
        # 권한외 사용자 질문수정 테스트
        self.client.login(username='testuser', password='password')
        response = self.client.put(reverse('questions:question-detail', args=[self.question.questionKey]), {
            'title': 'Updated Question',
            'content': 'Updated Content',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.question.refresh_from_db()
        self.assertEqual(self.question.title, 'Updated Question')

    def test_update_question_authenticated_not_owner(self):
        # 다른 사용자가 질문수정 테스트
        self.client.login(username='otheruser', password='otherpassword')
        response = self.client.put(reverse('questions:question-detail', args=[self.question.questionKey]), {
            'title': 'Updated Question',
            'content': 'Updated Content',
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_question_authenticated_owner(self):
        # 본인 질문 삭제 테스트
        self.client.login(username='testuser', password='password')
        response = self.client.delete(reverse('questions:question-detail', args=[self.question.questionKey]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Questions.objects.filter(pk=self.question.questionKey).exists())

    def test_delete_question_authenticated_not_owner(self):
        # 다른 사용자가 질문 삭제 테스트
        self.client.login(username='otheruser', password='otherpassword')
        response = self.client.delete(reverse('questions:question-detail', args=[self.question.questionKey]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CommentCreateViewTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.question = Questions.objects.create(author=self.user, title='Test Question', content='Test Content')

    def test_create_comment_authenticated(self):
        # 인증된 사용자 댓글 작성 테스트
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('questions:question-comment', args=[self.question.questionKey]), {
            'content': 'This is a test comment.'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comments.objects.count(), 1)

    def test_create_comment_unauthenticated(self):
        # 권한 외 사용자 댓글작성 테스트
        response = self.client.post(reverse('questions:question-comment', args=[self.question.questionKey]), {
            'content': 'This is a test comment.'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CommentUpdateViewTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.question = Questions.objects.create(author=self.user, title='Test Question', content='Test Content')
        self.comment = Comments.objects.create(user=self.user, question=self.question, content='Test Comment')

    def test_update_comment_authenticated_owner(self):
        # 본인 댓글 수정 테스트
        self.client.login(username='testuser', password='password')
        response = self.client.put(reverse('questions:questions-comment-detatil', args=[self.comment.CommentKey]), {
            'content': 'Updated Comment'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, 'Updated Comment')

    def test_update_comment_authenticated_not_owner(self):
        # 다른 사용자가 댓글수정 테스트
        other_user = User.objects.create_user(username='otheruser', password='otherpassword')
        self.client.login(username='otheruser', password='otherpassword')
        response = self.client.put(reverse('questions:questions-comment-detatil', args=[self.comment.CommentKey]), {
            'content': 'Updated Comment'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CommentDeleteViewTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.question = Questions.objects.create(author=self.user, title='Test Question', content='Test Content')
        self.comment = Comments.objects.create(user=self.user, question=self.question, content='Test Comment')

    def test_delete_comment_authenticated_owner(self):
        # 본인 댓글 삭제 테스트
        self.client.login(username='testuser', password='password')
        response = self.client.delete(reverse('questions:questions-comment-detatil', args=[self.comment.CommentKey]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comments.objects.filter(pk=self.comment.CommentKey).exists())

    def test_delete_comment_authenticated_not_owner(self):
        # 다른 사용자가 댓글 삭제 테스트
        other_user = User.objects.create_user(username='otheruser', password='otherpassword')
        self.client.login(username='otheruser', password='otherpassword')
        response = self.client.delete(reverse('questions:questions-comment-detatil', args=[self.comment.CommentKey]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
