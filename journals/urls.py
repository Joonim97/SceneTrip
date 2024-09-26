from django.urls import path
from .views import (
    JournalListAPIView, 
    # JournalDetailAPIView, 
)

app_name = "journals"

urlpatterns = [
    path('', JournalListAPIView.as_view(), name='jounal-list'),
] 