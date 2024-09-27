from django.urls import path, include
from .views import CommentView, CommentLikeView

urlpatterns = [
    #특정 게시물 댓글 조회 및 댓글 생성
    path('<int:community_pk>/comments/', CommentView.as_view, name='comment'),
    #댓글 수정, 삭제
    path('comments/<int:comment_id>/', CommentView.as_view, name='comment_detatil'),
    #댓글 좋아요, 싫어요
    path('<int:community_pk>/comments/<int:comment_id>/<str:like_type>/', CommentLikeView.as_view, name='comment_like'),
]
