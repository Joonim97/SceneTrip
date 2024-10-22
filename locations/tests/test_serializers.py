from django.contrib.auth import get_user_model
from django.test import TestCase
from models import Location, LocationSave
from serializers import LocationSerializer, LocationSaveSerializer
from rest_framework.exceptions import ValidationError

class LocationSerializerTest(TestCase):

    def setUp(self):
        # 테스트용 Location 생성
        self.location = Location.objects.create(
            id=1,
            media_type="movie",
            title="Test Movie Location",
            place_name="Test Place",
            place_type="Historical",
            place_description="A famous historical site.",
            opening_hours="09:00 - 18:00",
            break_time="12:00 - 13:00",
            closed_day="Monday",
            address="123 Test St, Test City",
            latitude=37.5665,
            longitude=126.9780,
            tel="010-1234-5678",
            created_at="2021-01-01",
            save_count=0
        )

    def test_location_serializer(self):
        """LocationSerializer가 데이터를 올바르게 직렬화하는지 테스트"""
        serializer = LocationSerializer(self.location)
        data = serializer.data
        self.assertEqual(data['title'], "Test Movie Location")
        self.assertEqual(data['place_name'], "Test Place")
        self.assertEqual(data['latitude'], 37.5665)
        self.assertEqual(data['longitude'], 126.9780)

class LocationSaveSerializerTest(TestCase):

    def setUp(self):
        # 테스트용 유저 생성
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser", 
            password="testpassword"
        )
        
        # 테스트용 Location 생성
        self.location = Location.objects.create(
            id=1,
            media_type="movie",
            title="Test Movie Location",
            place_name="Test Place",
            place_type="Historical",
            place_description="A famous historical site.",
            opening_hours="09:00 - 18:00",
            break_time="12:00 - 13:00",
            closed_day="Monday",
            address="123 Test St, Test City",
            latitude=37.5665,
            longitude=126.9780,
            tel="010-1234-5678",
            created_at="2021-01-01",
            save_count=0
        )

        # 테스트용 LocationSave 생성
        self.location_save = LocationSave.objects.create(
            user=self.user,
            location=self.location
        )

    def test_location_save_serializer(self):
        """저장Serializer가 데이터를 올바르게 직렬화하는지 테스트"""
        serializer = LocationSaveSerializer(self.location_save)
        data = serializer.data
        self.assertEqual(data['user'], self.user.id)  # user가 직렬화되면 id로 나타남
        self.assertEqual(data['location']['title'], "Test Movie Location")
        self.assertIsNotNone(data['saved_at'])

    def test_location_save_serializer_invalid(self):
        """존재하지 않는 데이터로 LocationSaveSerializer가 예외를 발생시키는지 테스트"""
        invalid_data = {
            'user': None,  # user를 None으로 설정하여 오류를 유도
            'location': {
                'id': 9999,  # 존재하지 않는 location id
            }
        }
        serializer = LocationSaveSerializer(data=invalid_data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
