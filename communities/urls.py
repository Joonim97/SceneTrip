from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    CommentView, CommentLikeView, CommunityListAPIView, CommunityDetailAPIView,
    CommunityUnusableAPIView,CommunityLikeAPIView, CommunityDislikeAPIView, CommunityWriteView, CommunityListView, CommunityEditAPIView,
    CommunityLikeStatusAPIView, CommunityDislikeStatusAPIView
    )

app_name = "communities"

urlpatterns = [
    #특정 게시물 댓글 조회 및 댓글 생성
    path('<uuid:communityKey>/comments/', CommentView.as_view(), name='community-comment'),
    # 대댓글
    path('<uuid:communityKey>/comments/<int:parent_id>/', CommentView.as_view(), name='community-reply'),
    #댓글 수정, 삭제
    path('comments/<int:comment_id>/', CommentView.as_view(), name='community-comment_detatil'),
    #댓글 좋아요, 싫어요
    path('comments/<int:comment_id>/<str:like_type>/', CommentLikeView.as_view(), name='community-comment-like'),
    # 커뮤글 전체목록조회, 작성
    path('', CommunityListAPIView.as_view(), name='community-list'),
    # 커뮤글 상세조회
    path('<uuid:communityKey>/', CommunityDetailAPIView.as_view(), name='community-detail'),
    # 커뮤글 신고
    path('<uuid:communityKey>/unusables/' , CommunityUnusableAPIView.as_view() , name='unusable'), 
    # 커뮤 좋아요
    path('<uuid:communityKey>/like/', CommunityLikeAPIView.as_view(), name='journal_like'), 
    # 커뮤 싫어요
    path('<uuid:communityKey>/dislike/', CommunityDislikeAPIView.as_view(), name='journal_dislike'),
    
    path('write/', CommunityWriteView.as_view(), name='community_write'),
    path('list/', CommunityListView.as_view(), name='community_list'),
    path('<uuid:communityKey>/edit/', CommunityEditAPIView.as_view(), name='community_edit'),
    
    path('<uuid:communityKey>/like-status/', CommunityLikeStatusAPIView.as_view(), name='community_like_status'),
    path('<uuid:communityKey>/dislike-status/', CommunityDislikeStatusAPIView.as_view(), name='community_dislike_status'),
]   

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)