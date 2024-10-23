from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import (CommentView, CommentLikeView, DislikedCommentsView, JournalListAPIView, JournalDetailAPIView, JournalLikeAPIView, 
                    JournalWriteView, JournalListView, JournalLikeStatusAPIView, JournalEditView)

app_name = "journals"

urlpatterns = [
    #특정 게시물 댓글 조회 및 댓글 생성
    path('<uuid:journalKey>/comments/', CommentView.as_view(), name='journal-comment'),
    # 대댓글
    path('<uuid:journalKey>/comments/<int:parent_id>/', CommentView.as_view(), name='journal-reply'),
    # 댓글 수정, 삭제
    path('comments/<int:comment_id>/', CommentView.as_view(), name='journal-comment-detail'),
    # 댓글 좋아요, 싫어요
    path('comments/<int:comment_id>/<str:like_type>/', CommentLikeView.as_view(), name='journal-comment-like'),
    # 일정 수 이상의 싫어요를 받은 댓글을 필터링. 100이상이면 삭제.
    path('comments/disliked/<int:min_dislikes>/', DislikedCommentsView.as_view(), name='disliked-comments'),

    # 저널 전체목록, 저널작성
    path('', JournalListAPIView.as_view(), name='journal_list'),
    # 저널 상세,수정,삭제
    path('<uuid:journalKey>/', JournalDetailAPIView.as_view(), name='journal_detail'),
    # 저널 좋아요/좋아요취소
    path('<uuid:journalKey>/like/', JournalLikeAPIView.as_view(), name='journal_like'),
    
    
    path('write/', JournalWriteView.as_view(), name='journal-write'),
    path('list/', JournalListView.as_view(), name='journal_list'),
    path('<uuid:journalKey>/like-status/', JournalLikeStatusAPIView.as_view(), name='journal_like_status'),  # 좋아요 상태 확인 API 경로

    path('<uuid:journalKey>/edit/', JournalEditView.as_view(), name='journal_edit'),  # 추가된 수정 페이지 경로
] 

