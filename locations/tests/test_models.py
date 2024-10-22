from django.test import TestCase
from django.contrib.auth import get_user_model
from models import Location, LocationSave

class LocationModelTests(TestCase):
    
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
    
    def test_location_creation(self):
        """Location 모델 생성 확인"""
        self.assertEqual(self.location.title, "Test Movie Location")
        self.assertEqual(self.location.place_name, "Test Place")
        self.assertEqual(self.location.latitude, 37.5665)
        self.assertEqual(self.location.longitude, 126.9780)

class LocationSaveModelTests(TestCase):
    
    def setUp(self):
        # 테스트용 유저
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser", 
            password="testpassword"
        )
        
        # 테스트용 Location
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

        # LocationSave 생성
        self.location_save = LocationSave.objects.create(
            user=self.user,
            location=self.location
        )

    def test_location_save_creation(self):
        """LocationSave 모델 생성 확인"""
        self.assertEqual(self.location_save.user, self.user)
        self.assertEqual(self.location_save.location, self.location)
        self.assertIsNotNone(self.location_save.saved_at)

    def test_unique_constraint(self):
        """같은 Location을 두번 저장할 수 없는지 확인"""
        with self.assertRaises(Exception):
            LocationSave.objects.create(user=self.user, location=self.location)
