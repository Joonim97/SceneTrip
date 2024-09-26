from . import views
from django.urls import path
from .views import SignupAPIView, VerifyEmailAPIView, SigninAPIView, LogoutAPIView, SubscribeView, Mypage

app_name = 'accounts'

urlpatterns = [
    path("signup/", SignupAPIView.as_view(), name="signup"), # 회원가입
    path("<str:nickname>/subscribes/", SubscribeView.as_view(), name="subscribes"), # 구독
    path('verify/<str:token>/', VerifyEmailAPIView.as_view(), name='verify_email'), # 이메일 인증
    path("login/", SigninAPIView.as_view(), name="login"), # 로그인
    path("logout/", LogoutAPIView.as_view(), name="logout"), # 로그아웃
    path("<str:nickname>/mypage/", Mypage.as_view(), name="mypage"), # 마이페이지
    ]