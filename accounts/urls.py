from . import views
from django.urls import path
from .views import SignupAPIView, VerifyEmailAPIView, LogoutAPIView, SubscribeView, Mypage
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

app_name = 'accounts'

urlpatterns = [
    path("signup/", SignupAPIView.as_view(), name="signup"), # 회원가입
    path("<str:nickname>/subscribes/", SubscribeView.as_view(), name="subscribes"), # 구독
    path('verify/<str:token>/', VerifyEmailAPIView.as_view(), name='verify_email'), # 이메일 인증
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("logout/", LogoutAPIView.as_view(), name="logout"), # 로그아웃
    path("<str:nickname>/mypage/", Mypage.as_view(), name="mypage"), # 마이페이지
    ]