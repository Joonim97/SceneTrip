from unittest.mock import patch  # 객체 모킹 라이브러리
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from rest_framework import status
from .models import Location, LocationSave
from .serializers import LocationSerializer
from .views import get_nearby_place
import json
import urllib


class LocationSaveModelTest(TestCase):

    def setUp(self):
        # 테스트를 위한 유저 생성 및 촬영지 객체 가져오기.
        self.user = get_user_model().objects.create_user(
            username="testuser", password="secret"
        )
        self.location = Location.objects.get(place_name="임진각")

    def test_create_location_save(self):
        # LocationSave 인스턴스가 유효한 유저, 촬영지에 대해 생성되는지 테스트
        location_save = LocationSave.objects.create(
            user=self.user, location=self.location
        )
        self.assertEqual(location_save.user, self.user)
        self.assertEqual(location_save.location, self.location)

    def test_unique_user_location_combination(self):
        # 동일한 촬영지가 중복 저장되는 오류가 발생하는지 테스트
        LocationSave.objects.create(user=self.user, location=self.location)
        with self.assertRaises(IntegrityError):
            LocationSave.objects.create(user=self.user, location=self.location)

    def test_saved_at_auto_now_add(self):
        # saved_at 필드가 자동으로 채워지는지 테스트
        location_save = LocationSave.objects.create(
            user=self.user, location=self.location
        )
        self.assertIsNotNone(location_save.saved_at)


class LocationListAPIViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        Location.objects.get(title="1987")

    def test_get_locations_by_title(self):
        # 작품 title 순으로 정렬
        response = self.client.get("/locations/lists/?sort_by=title")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(len(data), 8)
        self.assertEqual(data[0]["place_name"], "민주인권기념관")

    def test_get_locations_by_popularity(self):
        # 인기도(저장된 수) 순으로 정렬
        response = self.client.get("/locations/lists/?sort_by=popularity")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(len(data), 8)
        self.assertEqual(data[0]["place_name"], "임진각")


class LocationRegionAPIViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_locations_by_region(self):
        # 특정 지역의 촬영지 데이터 가져오기
        response = self.client.get("/locations/lists/서울특별시/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(len(data["서울특별시"]), 7080)

    def test_invalid_region(self):
        # 유효하지 않은 지역명 입력 시
        response = self.client.get("/locations/lists/써울특뼐시/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = json.loads(response.content)
        self.assertEqual(data["error"], "Invalid region")


class LocationDetailAPIViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.location = Location.objects.get(title="1987", place_name="임진각")

    def test_get_location_detail(self):
        # 촬영지 상세조회 테스트
        pk = self.location.pk
        response = self.client.get(f"/locations/lists/detail/{pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = LocationSerializer(self.location)
        self.assertEqual(json.loads(response.content), serializer.data)


class LocationSearchAPIViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        Location.objects.get(title="건축학개론")

    def test_search_locations(self):
        # 유효한 키워드로 검색
        response = self.client.get("/locations/search/?keyword=건축학개론")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["title"], "Test Location")

    def test_no_search_results(self):
        # 검색 키워드에 해당하는 검색결과가 없는 경우.
        response = self.client.get("/locations/search/?keyword=검색불가한키워드")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(data["message"], "검색 결과가 없습니다")

    def test_empty_search_term(self):
        # 키워드에 해당하는 검색결과가 없는 경우.
        response = self.client.get("/locations/search/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = json.loads(response.content)
        self.assertIn(
            "keyword", data["error"]
        )


class LocationSaveViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = self.client.post(
            "/accounts/login/", {"userid": "km111", "password": "kkm12341234*"}
        ).json()
        self.client.force_authenticate(token=self.user["token"])
        self.location = Location.objects.get(title="건축학개론")

    def test_save_location(self):
        response = self.client.post(f"/locations/{self.location.pk}/saves/")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = json.loads(response.content)
        self.assertEqual(data["message"], "촬영지 정보가 저장되었습니다.")
        location = Location.objects.get(pk=self.location.pk)
        self.assertEqual(location.save_count, 1)

    def test_unsave_location(self):
        # 촬영지 취소
        LocationSave.objects.create(user=self.user, location=self.location)
        response = self.client.post(f"/locations/{self.location.pk}/save/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        data = json.loads(response.content)
        self.assertEqual(data["message"], "촬영지 정보가 삭제되었습니다.")
        location = Location.objects.get(pk=self.location.pk)
        self.assertEqual(location.save_count, 0)

    def test_unauthorized_save(self):
        self.client.force_authenticate(user=None)  # Logout
        response = self.client.post(f"/locations/{self.location.pk}/save/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class GetNearbyPlaceTest(TestCase):
    def setUp(self):
        self.location = Location.objects.create(
            place_name="Test Location", address="Seoul, Korea"
        )

    @patch("urllib.request.urlopen")
    def test_successful_request(self, mock_urlopen):
        # 네이버 검색 API 응답 mock
        mock_urlopen.return_value.read.return_value = (
            b'{"items": [{"title": "Test Restaurant"}]}'
        )
        mock_urlopen.return_value.getcode.return_value = 200

        result = get_nearby_place("Test Location")
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], "Test Restaurant")

    def test_no_location_found(self):
        result = get_nearby_place("Nonexistent Location")
        self.assertEqual(
            result["error"], "No location found for place_name 'Nonexistent Location'"
        )

    @patch("urllib.request.urlopen")
    def test_api_error(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.URLError("Server Error")
        result = get_nearby_place("Test Location")
        self.assertIn("Error occurred", result["error"])

    @patch("Location.objects.annotate")
    def test_database_error(self, mock_annotate):
        mock_annotate.side_effect = Exception("Database Error")
        result = get_nearby_place("Test Location")
        self.assertIn("Error retrieving address", result["error"])

    def test_empty_place_name(self):
        result = get_nearby_place("")
        self.assertEqual(result["error"], "place_name is required")


class AiPlanningAPIViewTest(TestCase):
    @patch("views.get_nearby_place")
    @patch("langchain.chains.LLMChain.run")
    def test_successful_planning(self, mock_llm_chain, mock_get_nearby_place):
        # Naver Maps API와 LLM이 정상적으로 작동하는 경우
        mock_get_nearby_place.return_value = [{"title": "Test Restaurant"}]
        mock_llm_chain.return_value = "Your travel plan..."

        # 요청 생성
        request = self.client.post("/api/planning/", {"place_name": "Test Place"})

        # 응답 확인
        self.assertEqual(request.status_code, 200)
        self.assertIn("travel_plan", request.data)

        # ... 다른 테스트 케이스 

        @patch("views.get_nearby_place")
        def test_no_nearby_places(self, mock_get_nearby_place):
            # 근처 장소를 찾을 수 없는 경우
            mock_get_nearby_place.return_value = []

            # 요청 생성 및 응답 확인


        @patch("langchain.chains.LLMChain.run")
        def test_llm_error(self, mock_llm_chain):
            # LLM 오류 발생 시
            mock_llm_chain.side_effect = Exception("LLM Error")

            # 요청 생성 및 응답 확인
