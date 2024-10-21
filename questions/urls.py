from django.urls import path
from .views import QnaListView, QnaWriteView, QuestionListView, QuestionDetailAPIView, CommentCreateView, CommentUpdateView,CommentDeleteView
from questions import views

app_name = "questions"

urlpatterns =  [
    # 큐앤에이 전체목록조회, 작성
    path('', QuestionListView.as_view(), name='question-list'),
    # 큐앤에이 상세조회, 수정, 삭제
    path('<str:key>/', QuestionDetailAPIView.as_view(), name='question-detail'),

    # 댓글 조회, 생성
    path('<str:key>/comments/', CommentCreateView.as_view(), name='question-comment'),
    # 댓글 수정, 삭제
    path('comments/<str:key>/', CommentUpdateView.as_view(), name='questions-comment-detatil'),
    path('qna/page/', QnaListView.as_view(), name='qna-list'), # Q&A 전체페이지
    path('qna/page/write/', QnaWriteView.as_view(), name='qna_write') # Q&A 글 작성 페이지
    ]