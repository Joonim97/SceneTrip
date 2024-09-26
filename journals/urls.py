from django.urls import path, include
from .views import CommentView

urlpatterns = [
    path('<int:journal_pk>/comments/', CommentView)
]
