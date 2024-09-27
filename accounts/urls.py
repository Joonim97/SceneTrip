from . import views
from django.urls import path
from .views import SignupAPIView, VerifyEmailAPIView, LogoutAPIView, SubscribeView, Mypage, PasswordResetRequestView, PasswordResetConfirmView, EmailResetRequestView, EamilResetConfirmView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

app_name = 'accounts'

urlpatterns = [
    path("signup/", SignupAPIView.as_view(), name="signup"), # 회원가입
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("<str:nickname>/subscribes/", SubscribeView.as_view(), name="subscribes"), # 구독
    path('verify/<str:token>/', VerifyEmailAPIView.as_view(), name='verify_email'), # 이메일 인증
    path('password_reset/', PasswordResetRequestView.as_view(), name='password_reset'), # 비밀번호 초기화
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'), #비밀번호 재설정
    path('email_reset/', EmailResetRequestView.as_view(), name='email_reset'), # 이메일 초기화
    path('emailreset/<uidb64>/<token>/', EamilResetConfirmView.as_view(), name='password_reset_confirm'), # 이메일 재설정
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutAPIView.as_view(), name="logout"), # 로그아웃
    path("<str:nickname>/mypage/", Mypage.as_view(), name="mypage"), # 마이페이지
    ]