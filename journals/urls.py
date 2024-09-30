from django.urls import path, include
from .views import CommentView, CommentLikeView, JournalListAPIView, JournalDetailAPIView, JournalSearchSet, JournalLikeAPIView

app_name = "journals"

urlpatterns = [
    #특정 게시물 댓글 조회 및 댓글 생성
    path('<int:journal_pk>/comments/', CommentView.as_view, name='comment'),
    #댓글 수정, 삭제
    path('comments/<int:comment_id>/', CommentView.as_view, name='comment_detatil'),
    #댓글 좋아요, 싫어요
    path('<int:journal_pk>/comments/<int:comment_id>/<str:like_type>/', CommentLikeView.as_view, name='comment_like'),

    path('', JournalListAPIView.as_view(), name='jounal_list'), # 저널 전체목록, 저널작성
    path('<int:pk>/', JournalDetailAPIView.as_view(), name='jounal_detail'), # 저널 상세,수정,삭제
    path('search/', JournalSearchSet.as_view(), name='journal_search'), # 저널 검색
    path('<int:pk>/like/', JournalLikeAPIView.as_view(), name='journal_like') # 저널 좋아요/좋아요취소
] 
