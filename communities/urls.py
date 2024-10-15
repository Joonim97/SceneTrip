from django.urls import path
from .views import (
    CommentView, CommentLikeView, CommunityListAPIView, CommunityDetailAPIView,
    CommunityUnusableAPIView,CommunityLikeAPIView, CommunityDislikeAPIView, CommunityWriteView, CommunityListView
    )

app_name = "communities"

urlpatterns = [
    #특정 게시물 댓글 조회 및 댓글 생성
    path('<int:community_id>/comments/', CommentView.as_view(), name='community-comment'),
    # 대댓글
    path('<int:community_id>/comments/<int:parent_id>/', CommentView.as_view(), name='community-reply'),
    #댓글 수정, 삭제
    path('comments/<int:comment_id>/', CommentView.as_view(), name='community-comment_detatil'),
    #댓글 좋아요, 싫어요
    path('comments/<int:comment_id>/<str:like_type>/', CommentLikeView.as_view(), name='community-comment-like'),
    # 커뮤글 전체목록조회
    path('', CommunityListAPIView.as_view(), name='community-list'),
    # 커뮤글 상세조회
    path('<int:pk>/', CommunityDetailAPIView.as_view(), name='community-detail'),
    # 커뮤글 신고
    path('<int:pk>/unusables/' , CommunityUnusableAPIView.as_view() , name='unusable'), 
    # 커뮤 좋아요
    path('<int:pk>/like/', CommunityLikeAPIView.as_view(), name='journal_like'), 
    # 커뮤 싫어요
    path('<int:pk>/dislike/', CommunityDislikeAPIView.as_view(), name='journal_dislike'),
    
    path('write/', CommunityWriteView.as_view(), name='community_write'),
    path('list/', CommunityListView.as_view(), name='community_list'),
]   