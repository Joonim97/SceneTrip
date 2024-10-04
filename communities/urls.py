from django.urls import path, include
from .views import CommentView, CommentLikeView, DislikedCommentsView, CommunityListAPIView, CommunityDetailAPIView, CommunityUnusableAPIView

app_name = "communities"

urlpatterns = [
    #특정 게시물 댓글 조회 및 댓글 생성
    path('<int:community_pk>/comments/', CommentView.as_view, name='community-comment'),
    # 대댓글
    path('<int:community_id>/comments/<int:parent_id>/', CommentView.as_view(), name='community-reply'),
    #댓글 수정, 삭제
    path('comments/<int:comment_id>/', CommentView.as_view, name='community-comment_detatil'),
    #댓글 좋아요, 싫어요
    path('comments/<int:comment_id>/<str:like_type>/', CommentLikeView.as_view(), name='community-comment-like'),
    path('comments/disliked/<int:min_dislikes>/', DislikedCommentsView.as_view(), name='community-disliked-comments'),
    path('', CommunityListAPIView.as_view(), name='community-list'),
    path('<int:pk>/', CommunityDetailAPIView.as_view(), name='community-detail'),
    path('<int:pk>/unusables/' , CommunityUnusableAPIView.as_view() , name='unusable'), # 커뮤글 신고
]   