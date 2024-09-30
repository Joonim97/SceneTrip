from django.urls import path, include
from .views import CommentView, CommentLikeView, JournalListAPIView, JournalDetailAPIView, JournalSearchSet

app_name = "journals"

urlpatterns = [
    #특정 게시물 댓글 조회 및 댓글 생성
    path('<int:journal_pk>/comments/', CommentView.as_view, name='journal-comment'),
    #댓글 수정, 삭제
    path('comments/<int:comment_id>/', CommentView.as_view, name='journal-comment-detatil'),
    #댓글 좋아요, 싫어요
    path('<int:journal_pk>/comments/<int:comment_id>/<str:like_type>/', CommentLikeView.as_view, name='journal-comment-like'),
    path('', JournalListAPIView.as_view(), name='jounal-list'),
    path('<int:pk>/', JournalDetailAPIView.as_view(), name='jounal-detail'),
    path('search/', JournalSearchSet.as_view(), name='journal-search'),
] 
