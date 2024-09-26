from . import views
from django.urls import path
from .views import SignupAPIView, VerifyEmailAPIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

app_name = 'accounts'

urlpatterns = [
    path("signup/", SignupAPIView.as_view(), name="signup"),
    path('verify/<str:token>/', VerifyEmailAPIView.as_view(), name='verify_email'),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair") # 로그인로직
    ]