from django.urls import path
from .views import LocationListAPIView, LocationSearchAPIView, LocationDetailAPIView, LocationsaveView

app_name = "locations"

urlpatterns = [
    path("lists/", LocationListAPIView.as_view(), name="location-list"),
    path("search/", LocationSearchAPIView.as_view(), name="location-search"),
    # path("lists/<str:지역명>/"),
    path("lists/<int:pk>/", LocationDetailAPIView.as_view(), name="location-detail"),
    # path("<int:pk>/saves/", LocationsaveView.as_view(), name="location-save"),
    # path("lists/plans/"),
]
