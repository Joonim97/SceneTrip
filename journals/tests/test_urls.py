from django.test import SimpleTestCase
from django.urls import reverse, resolve
from journals.views import (CommentView, CommentLikeView, DislikedCommentsView,
                            JournalListAPIView, JournalDetailAPIView, JournalLikeAPIView)

# reverse() : url패턴이름, 인자를 사용해 url을 생성함
# resolve() : url이 어느 클래스에 연결되는지 확인함
# SimpleTestCase : 데이터베이스가 필요없는 테스트케이스에 사용함

class TestJournalUrls(SimpleTestCase):

    def test_journal_comment_url(self): # 저널댓글 url
        url = reverse('journals:journal-comment', args=[1]) # args=[1] : 어떤 저널의 id인지
        self.assertEqual(resolve(url).func.view_class, CommentView)

    def test_journal_reply_url(self): # 저널대댓글 url
        url = reverse('journals:journal-reply', args=[1, 2]) # args=[1,2] 1:저널id, 2:부모댓글id
        self.assertEqual(resolve(url).func.view_class, CommentView)

    def test_journal_comment_detail_url(self): # 저널댓글 수정/삭제 url
        url = reverse('journals:journal-comment-detail', args=[1]) # args=[1] :댓글id
        self.assertEqual(resolve(url).func.view_class, CommentView)

    def test_journal_comment_like_url(self): # 저널댓글 좋아요싫어요 url
        url = reverse('journals:journal-comment-like', args=[1, 'like']) # args=[1,'like'] 1:댓글id, 'like':좋아요타입
        self.assertEqual(resolve(url).func.view_class, CommentLikeView)

    def test_disliked_comments_url(self): # 저널 일정수이상싫어요댓글 조회 url
        url = reverse('journals:disliked-comments', args=[100]) # args=[100] : 싫어요 100개이상
        self.assertEqual(resolve(url).func.view_class, DislikedCommentsView)

    def test_journal_list_url(self): # 저널목록 url
        url = reverse('journals:journal_list')
        self.assertEqual(resolve(url).func.view_class, JournalListAPIView)

    def test_journal_detail_url(self): # 저널상세 url
        url = reverse('journals:journal_detail', args=[1]) # args=[1] :저널id
        self.assertEqual(resolve(url).func.view_class, JournalDetailAPIView)

    def test_journal_like_url(self): # 저널 좋아요/좋아요취소 url
        url = reverse('journals:journal_like', args=[1])
        self.assertEqual(resolve(url).func.view_class, JournalLikeAPIView)
