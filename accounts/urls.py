from . import views
from django.urls import path
from .views import SignupAPIView, VerifyEmailAPIView

app_name = 'accounts'

urlpatterns = [
    path("signup/", SignupAPIView.as_view(), name="signup"),
    path('verify/<str:token>/', VerifyEmailAPIView.as_view(), name='verify_email'),
    ]