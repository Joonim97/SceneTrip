from django.urls import path
from .views import CommentView, QnaListView, QnaWriteView, QuestionListView, QuestionDetailAPIView
from questions import views
from django.conf import settings
from django.conf.urls.static import static

app_name = "questions"

urlpatterns =  [
    # 큐앤에이 전체목록조회, 작성
    path('', QuestionListView.as_view(), name='question-list'),
    # 큐앤에이 상세조회, 수정, 삭제
    path('<str:key>/', QuestionDetailAPIView.as_view(), name='question-detail'),
    # 댓글 조회, 생성, 수정, 삭제
    path('<str:key>/comments/', CommentView.as_view(), name='question-comment'),
    # 댓글 수정, 삭제
    path('qna/page/', QnaListView.as_view(), name='qna-list'), # Q&A 전체페이지
    path('qna/page/write/', QnaWriteView.as_view(), name='qna_write'), # Q&A 글 작성 페이지
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)