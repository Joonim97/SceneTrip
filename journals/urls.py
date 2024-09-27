from django.urls import path
from .views import (
    JournalListAPIView, JournalDetailAPIView, JournalSearchSet
)

app_name = "journals"

urlpatterns = [
    path('', JournalListAPIView.as_view(), name='jounal-list'),
    path('<int:pk>/', JournalDetailAPIView.as_view(), name='jounal-detail'),
    path('search/', JournalSearchSet.as_view(), name='journal-search')
] 