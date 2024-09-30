from django.urls import path
from .views import LocationListAPIView, LocationSearchAPIView, LocationRegionAPIView, LocationDetailAPIView, LocationSaveView

app_name = "locations"

urlpatterns = [
    path("lists/", LocationListAPIView.as_view(), name="location-list"),
    path("search/", LocationSearchAPIView.as_view(), name="location-search"),
    path("lists/<str:region>/", LocationRegionAPIView.as_view(), name="location-region-list"),
    path("lists/<int:pk>/", LocationDetailAPIView.as_view(), name="location-detail"),
    path("<int:id>/saves/", LocationSaveView.as_view(), name="location-save"),
    # path("lists/plans/"),
]
