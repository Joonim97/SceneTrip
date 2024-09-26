from django.urls import path
from .views import LocationListAPIView, LocationSearchAPIView

app_name = "locations"

urlpatterns = [
    path("lists/", LocationListAPIView.as_view(), name="location-list"),
    path("search/", LocationSearchAPIView.as_view(), name="location-search"),
    # path("lists/<str:지역명>/"),
    # path("lists/<int:pk>"),
    # path("<int:pk>/saves/"),
    # path("lists/plans"),
]
