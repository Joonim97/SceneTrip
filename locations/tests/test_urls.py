from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

class LocationURLTests(APITestCase):

    def test_location_list(self):
        url = reverse('locations:location-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_location_search(self):
        url = reverse('locations:location-search')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_location_region_list(self):
        region = "seoul"  # 예시 지역
        url = reverse('locations:location-region-list', args=[region])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_location_detail(self):
        pk = 1  # 테스트용 pk
        url = reverse('locations:location-detail', args=[pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_location_save(self):
        location_id = 1  # 테스트용 location id
        url = reverse('locations:location-save', args=[location_id])
        response = self.client.post(url)  # 저장-post
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_location_list_view(self):
        url = reverse('locations:location_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_location_detail_view(self):
        pk = 1  # 테스트용 pk
        url = reverse('locations:location_detail', args=[pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_trip_planning(self):
        url = reverse('locations:trip-planning')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_plan_response(self):
        url = reverse('locations:plan-response')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
