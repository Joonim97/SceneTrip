from . import views
from django.urls import path
from .views import (SignupAPIView, SocialLoginView, VerifyEmailAPIView, LogoutAPIView, SubscribeView, Mypage, 
                    PasswordResetRequestView, PasswordResetConfirmView, EmailResetRequestView,
                    EamilResetConfirmView, MyJournalsListAPIView, SavedLocationsListAPIView, 
                    LikeJournalsListAPIView, SubscribingsListAPIView, SubsribingsjournalAPI, 
                    MyCommunityListAPIView, DeleteAPIView, VerifyjJurnalEmailAPIView, SocialCallbackView)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

app_name = 'accounts'

urlpatterns = [
    path("signup/", SignupAPIView.as_view(), name="signup"), # 회원가입
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"), # 로그인
    path("<str:nickname>/subscribes/", SubscribeView.as_view(), name="subscribes"), # 구독
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"), # 리프레시 토큰
    ######## email send 관련 url
    path('verify/<str:token>/', VerifyEmailAPIView.as_view(), name='verify_email'), # 회원가입 이메일 인증, 이 path 없으면 이메일 인증시 Not Found 에러 발생
    path('journalists/verify/<str:token>', VerifyjJurnalEmailAPIView.as_view(), name='verify_journalemail'), # 회원가입 grade가 저널일 경우
    path('passwordreset/', PasswordResetRequestView.as_view(), name='password_reset'), # 비밀번호 초기화
    path('passwordchange/verify/<str:token>/', PasswordResetConfirmView.as_view(), name='passwordverifyemail'), # 비밀번호 변경 이메일 인증
    path('emailreset/', EmailResetRequestView.as_view(), name='email_reset'), # 이메일 초기화
    path('emailchange/verify/<str:token>/', EamilResetConfirmView.as_view(), name='emailverifyemail'), # 이메일변경 이메일 인증
    ######## 이 아래 url 31번 줄까지 마이페이지 관련된 url
    path("<str:nickname>/mypage/", Mypage.as_view(), name="mypage"), # 마이페이지
    path('<str:nickname>/mypage/journallike/', LikeJournalsListAPIView.as_view(), name='journal_like'), # 내가 좋아요한 저널 글 목록
    path('<str:nickname>/mypage/myjournals/', MyJournalsListAPIView.as_view(), name='my_journals'), # 내가 쓴 글 전체보기
    path('<str:nickname>/mypage/savedlocations/', SavedLocationsListAPIView.as_view(), name='saved_locations'), # 저장한 촬영지 전체보기
    path('<str:nickname>/mypage/subscribings/', SubscribingsListAPIView.as_view(), name='subscribings'), # 내가 구독한 사람 전체보기
    path('<str:nickname>/mypage/communitiesauthor/', MyCommunityListAPIView.as_view(), name='my_communities'), # 내가 쓴 커뮤니티 글 전체보기
    path('<str:nickname>/mypage/<str:sub_nickname>/', SubsribingsjournalAPI.as_view(), name='subscribings_journal'), # 내가 구독한 인원 글 보기
    # 회원탈퇴 및 로그아웃
    path("logout/", LogoutAPIView.as_view(), name="logout"), # 로그아웃
    path('<str:nickname>/delete/', DeleteAPIView.as_view(), name='accounts_delete'), # 회원탈퇴
    # path('sociallogin/index.html', LoginView.as_view(template_name='accounts/index.html'), name='sologin'),
    # path('social/login/<str:provider>/', SocialLoginView.as_view(), name='social_login'),
    # path('social/callback/<str:provider>/', SocialCallbackView.as_view(), name='social_callback')
    path('kakaologinpage/', views.kakaologinpage, name='kakaologinpage'),
    path('index/', views.index, name='index'),
    path('social/login/<str:provider>/', SocialLoginView.as_view() ,name='kakao_login'),  # 카카오 로그인 URL
    path('social/callback/<str:provider>/', SocialCallbackView.as_view(), name='kakao_callback'),  # 카카오 콜백 URL
    # path('kakao/login/callback/', views.KakaoLogin.as_view(), name='kakao_login_callback'),  # Django-Allauth나 Django-Rest-Framework와 연동된 로그인 콜백
]
