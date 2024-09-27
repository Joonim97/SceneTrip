from django.urls import path
from .views import CommunityListAPIView, CommunityDetailAPIView

app_name = "communities"

urlpatterns = [
    path('', CommunityListAPIView.as_view(), name='community-list'),
    path('<int:pk>/', CommunityDetailAPIView.as_view(), name='community-detail'),
]