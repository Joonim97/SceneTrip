from django.urls import reverse, resolve
from django.test import TestCase
from questions.views import (
    QuestionListView,
    QuestionDetailAPIView,
    CommentCreateView,
    CommentUpdateView
)

class QuestionsURLsTestCase(TestCase):
    def test_question_list_url(self):
        # Test the question list URL routing
        url = reverse('questions:question-list')
        self.assertEqual(resolve(url).func.view_class, QuestionListView)
    
    def test_question_detail_url(self):
        # Test the question detail URL routing with a key
        url = reverse('questions:question-detail', args=['some-question-key'])
        self.assertEqual(resolve(url).func.view_class, QuestionDetailAPIView)

    def test_comment_create_url(self):
        # Test the comment creation URL routing
        url = reverse('questions:question-comment', args=['some-question-key'])
        self.assertEqual(resolve(url).func.view_class, CommentCreateView)

    def test_comment_update_url(self):
        # Test the comment update URL routing
        url = reverse('questions:questions-comment-detatil', args=['some-comment-key'])
        self.assertEqual(resolve(url).func.view_class, CommentUpdateView)

