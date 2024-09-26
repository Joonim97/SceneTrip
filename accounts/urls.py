from . import views
from django.urls import path
from .views import SignupAPIView, VerifyEmailAPIView, SigninAPIView, LogoutAPIView, SubscribeView

app_name = 'accounts'

urlpatterns = [
    path("signup/", SignupAPIView.as_view(), name="signup"),
    path('verify/<str:token>/', VerifyEmailAPIView.as_view(), name='verify_email'),
    path("login/", SigninAPIView.as_view(), name="login"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path("<str:nickname>/subscribes/", SubscribeView.as_view(), name="subscribes"),
    ]