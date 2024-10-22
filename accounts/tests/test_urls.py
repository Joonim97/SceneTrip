from django.urls import reverse
from django.test import TestCase

class UrlsTests(TestCase):

    def test_signup_url(self):
        url = reverse('accounts:signup')
        self.assertEqual(url, '/signup/')

    def test_login_page_url(self):
        url = reverse('accounts:login_page')
        self.assertEqual(url, '/login-page/')

    def test_token_obtain_pair_url(self):
        url = reverse('accounts:token_obtain_pair')
        self.assertEqual(url, '/login/')

    def test_subscribe_url(self):
        url = reverse('accounts:subscribes', kwargs={'nickname': 'test_nickname'})
        self.assertEqual(url, '/test_nickname/subscribes/')

    def test_verify_email_url(self):
        url = reverse('accounts:verify_email', kwargs={'token': 'test_token'})
        self.assertEqual(url, '/verify/test_token/')

    def test_verify_journal_email_url(self):
        url = reverse('accounts:verify_journalemail', kwargs={'token': 'test_token'})
        self.assertEqual(url, '/journalists/verify/test_token')

    def test_password_reset_url(self):
        url = reverse('accounts:password_reset')
        self.assertEqual(url, '/passwordreset/')

    def test_password_reset_confirm_url(self):
        url = reverse('accounts:passwordverifyemail', kwargs={'token': 'test_token'})
        self.assertEqual(url, '/passwordchange/verify/test_token/')

    def test_email_reset_url(self):
        url = reverse('accounts:email_reset')
        self.assertEqual(url, '/emailreset/')

    def test_email_reset_confirm_url(self):
        url = reverse('accounts:emailverifyemail', kwargs={'token': 'test_token'})
        self.assertEqual(url, '/emailchange/verify/test_token/')

    def test_mypage_url(self):
        url = reverse('accounts:mypage', kwargs={'nickname': 'test_nickname'})
        self.assertEqual(url, '/test_nickname/mypage/')

    def test_logout_url(self):
        url = reverse('accounts:logout')
        self.assertEqual(url, '/logout/')

    def test_like_journals_url(self):
        url = reverse('accounts:journal_like', kwargs={'nickname': 'test_nickname'})
        self.assertEqual(url, '/test_nickname/mypage/journallike/')

    def test_my_journals_url(self):
        url = reverse('accounts:my_journals', kwargs={'nickname': 'test_nickname'})
        self.assertEqual(url, '/test_nickname/mypage/myjournals/')

    def test_saved_locations_url(self):
        url = reverse('accounts:saved_locations', kwargs={'nickname': 'test_nickname'})
        self.assertEqual(url, '/test_nickname/mypage/savedlocations/')

    def test_subscribings_url(self):
        url = reverse('accounts:subscribings', kwargs={'nickname': 'test_nickname'})
        self.assertEqual(url, '/test_nickname/mypage/subscribings/')

    def test_my_communities_url(self):
        url = reverse('accounts:my_communities', kwargs={'nickname': 'test_nickname'})
        self.assertEqual(url, '/test_nickname/mypage/communitiesauthor/')

    def test_subscribings_journal_url(self):
        url = reverse('accounts:subscribings_journal', kwargs={'nickname': 'test_nickname', 'sub_nickname': 'test_sub'})
        self.assertEqual(url, '/test_nickname/mypage/test_sub/')

    def test_delete_account_url(self):
        url = reverse('accounts:accounts_delete', kwargs={'nickname': 'test_nickname'})
        self.assertEqual(url, '/test_nickname/delete/')

    def test_user_info_url(self):
        url = reverse('accounts:user_info')
        self.assertEqual(url, '/user-info/')

    def test_mypage_view_url(self):
        url = reverse('accounts:my_page', kwargs={'nickname': 'test_nickname'})
        self.assertEqual(url, '/test_nickname/mypage/')

    def test_kakaologinpage_url(self):
        url = reverse('accounts:kakaologinpage')
        self.assertEqual(url, '/kakaologinpage/')

    def test_social_login_url(self):
        url = reverse('accounts:kakao_login', kwargs={'provider': 'kakao'})
        self.assertEqual(url, '/social/login/kakao/')

    def test_social_callback_url(self):
        url = reverse('accounts:kakao_callback', kwargs={'provider': 'kakao'})
        self.assertEqual(url, '/social/callback/kakao/')
