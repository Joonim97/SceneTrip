from django.urls import path, include
from .views import (CommentView, CommentLikeView, DislikedCommentsView,
            JournalListAPIView,JournalDetailAPIView, JournalLikeAPIView,JournalLikeListAPIView)

app_name = "journals"

urlpatterns = [
    #특정 게시물 댓글 조회 및 댓글 생성
    path('<int:journal_id>/comments/', CommentView.as_view(), name='journal-comment'),
    # 대댓글
    path('<int:journal_id>/comments/<int:parent_id>/', CommentView.as_view(), name='journal-reply'),
    #댓글 수정, 삭제
    path('comments/<int:comment_id>/', CommentView.as_view(), name='journal-comment-detatil'),
    #댓글 좋아요, 싫어요
    path('comments/<int:comment_id>/<str:like_type>/', CommentLikeView.as_view(), name='journal-comment-like'),
    path('comments/disliked/<int:min_dislikes>/', DislikedCommentsView.as_view(), name='disliked-comments'),
    
    
    path('', JournalListAPIView.as_view(), name='jounal_list'), # 저널 전체목록, 저널작성
    path('<int:pk>/', JournalDetailAPIView.as_view(), name='jounal_detail'), # 저널 상세,수정,삭제
    path('<int:pk>/like/', JournalLikeAPIView.as_view(), name='journal_like'), # 저널 좋아요/좋아요취소
    path('likes/', JournalLikeListAPIView.as_view(), name='journal_likelist') # 좋아요한 저널 보기
] 
