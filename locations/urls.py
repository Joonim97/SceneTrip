from django.urls import path
from .views import LocationListAPIView, LocationSearchAPIView, LocationRegionAPIView, LocationDetailAPIView, LocationSaveView, RecommendAPIView

app_name = "locations"

urlpatterns = [
    path("lists/", LocationListAPIView.as_view(), name="location-list"), # 촬영지 목록 조회
    path("search/", LocationSearchAPIView.as_view(), name="location-search"), # 촬영지 검색
    path("lists/<str:region>/", LocationRegionAPIView.as_view(), name="location-region-list"), # 촬영지 지역별 조회
    path("lists/detail/<int:pk>/", LocationDetailAPIView.as_view(), name="location-detail"), # 촬영지 상세조회
    path("<int:id>/saves/", LocationSaveView.as_view(), name="location-save"), # 촬영지 저장
    path("plans/", RecommendAPIView.as_view(), name="trip-planning"),
]
