from django.urls import path, include
from .views import CommentView, CommentLikeView, CommunityListAPIView, CommunityDetailAPIView, CommunityUnusableAPIView

app_name = "communities"

urlpatterns = [
    #특정 게시물 댓글 조회 및 댓글 생성
    path('<int:community_pk>/comments/', CommentView.as_view, name='comment'),
    #댓글 수정, 삭제
    path('comments/<int:comment_id>/', CommentView.as_view, name='comment_detatil'),
    #댓글 좋아요, 싫어요
    path('<int:community_pk>/comments/<int:comment_id>/<str:like_type>/', CommentLikeView.as_view, name='comment_like'),
    path('', CommunityListAPIView.as_view(), name='community-list'),
    path('<int:pk>/', CommunityDetailAPIView.as_view(), name='community-detail'),
    path('<int:pk>/unusable/' , CommunityUnusableAPIView.as_view() , name='unusable'), # 커뮤글 신고
]   