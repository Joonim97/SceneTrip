from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from models import Location, LocationSave

User = get_user_model()

class LocationAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.location1 = Location.objects.create(title="Test Location 1", place_name="Place 1", save_count=10, address="서울특별시 마포구")
        self.location2 = Location.objects.create(title="Test Location 2", place_name="Place 2", save_count=5, address="경기도 성남시")

    def test_location_list_view(self):
        url = reverse('location-list')  
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Test Location 1', str(response.data))
        self.assertIn('Test Location 2', str(response.data))

    def test_location_list_sort_by_title(self):
        url = reverse('location-list') + "?sort_by=title"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 데이터가 title로 정렬됐는지 확인
        sorted_titles = sorted([self.location1.title, self.location2.title])
        response_titles = [loc['title'] for loc in response.data]
        self.assertEqual(sorted_titles, response_titles)

    def test_location_list_sort_by_popularity(self):
        url = reverse('location-list') + "?sort_by=popularity"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # save_count 순으로 정렬됐는지 확인
        sorted_save_counts = sorted([self.location1.save_count, self.location2.save_count], reverse=True)
        response_save_counts = [loc['save_count'] for loc in response.data]
        self.assertEqual(sorted_save_counts, response_save_counts)

    def test_location_region_view(self):
        url = reverse('location-region', kwargs={'region': '서울특별시'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('서울특별시', str(response.data))

    def test_location_region_invalid_region(self):
        url = reverse('location-region', kwargs={'region': 'invalid_region'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_location_detail_view(self):
        url = reverse('location-detail', kwargs={'pk': self.location1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.location1.title)

    def test_location_save_post(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse('location-save', kwargs={'id': self.location1.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LocationSave.objects.count(), 1)

        # 저장된 location 삭제 테스트
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(LocationSave.objects.count(), 0)

    def test_location_search_view(self):
        url = reverse('location-search') + "?keyword=Place"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Place 1', str(response.data))
        self.assertIn('Place 2', str(response.data))

    def test_ai_planning_view(self):
        url = reverse('ai-planning')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        post_response = self.client.post(url, {'place_name': 'Test Place'})
        self.assertEqual(post_response.status_code, status.HTTP_200_OK)

