from . import views
from django.urls import path
from .views import (SignupAPIView, VerifyEmailAPIView, LogoutAPIView, SubscribeView, Mypage, PasswordResetRequestView,
                    PasswordResetConfirmView, EmailResetRequestView,
                    EamilResetConfirmView, MyJournalsListAPIView, SavedLocationsListAPIView, SubscribingsListAPIView, SubsribingsjournalAPI, MyCommunityListAPIView, DeleteAPIView)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

app_name = 'accounts'

urlpatterns = [
    path("signup/", SignupAPIView.as_view(), name="signup"), # 회원가입
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("<str:nickname>/subscribes/", SubscribeView.as_view(), name="subscribes"), # 구독
    path('verify/<str:token>/', VerifyEmailAPIView.as_view(), name='verify_email'), # 회원가입 이메일 인증
    path('passwordreset/', PasswordResetRequestView.as_view(), name='password_reset'), # 비밀번호 초기화
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'), #비밀번호 재설정
    path('emailreset/', EmailResetRequestView.as_view(), name='email_reset'), # 이메일 초기화
    path('emailchange/verify/<str:token>/', EamilResetConfirmView.as_view(), name='verify_email'), # 이메일변경 이메일 인증
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutAPIView.as_view(), name="logout"), # 로그아웃
    path("<str:nickname>/mypage/", Mypage.as_view(), name="mypage"), # 마이페이지
    path('<str:nickname>/mypage/my_journals/', MyJournalsListAPIView.as_view(), name='my_journals'), # 내가 쓴 글 전체보기
    path('<str:nickname>/mypage/saved_locations/', SavedLocationsListAPIView.as_view(), name='saved_locations'), # 저장한 촬영지 전체보기
    path('<str:nickname>/mypage/subscribings/', SubscribingsListAPIView.as_view(), name='subscribings'), # 내가 구독한 사람 전체보기
    path('<str:nickname>/mypage/communities_author/', MyCommunityListAPIView.as_view(), name='my_journals'), # 내가 쓴 글 전체보기
    path('<str:nickname>/mypage/<str:sub_nickname>/', SubsribingsjournalAPI.as_view(), name='subscribings_journal'), # 내가 구독한 인원 글 보기
    path('<str:nickname>/delete/', DeleteAPIView.as_view(), name='accounts_delete')
]