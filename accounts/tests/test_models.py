from django.test import TestCase
from models import User
import uuid

class UserModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            user_id='testuser123',
            email='testuser@example.com',
            password='password123',
            nickname='testnickname'
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.user_id, 'testuser123')
        self.assertEqual(self.user.email, 'testuser@example.com')
        self.assertEqual(self.user.nickname, 'testnickname')
        self.assertEqual(self.user.grade, User.NORMAL)

    def test_user_string_representation(self):
        self.assertEqual(str(self.user), 'testuser123')

    def test_user_uuid(self):
        self.assertIsInstance(self.user.uuid, uuid.UUID)

    def test_user_email_unique(self):
        with self.assertRaises(Exception):
            User.objects.create_user(
                username='anotheruser',
                user_id='anotheruser123',
                email='testuser@example.com',
                password='password123',
                nickname='anothernickname'
            )

    def test_user_subscribings(self):
        another_user = User.objects.create_user(
            username='anotheruser',
            user_id='anotheruser123',
            email='anotheruser@example.com',
            password='password123',
            nickname='anothernickname'
        )
        self.user.subscribings.add(another_user)
        self.assertIn(another_user, self.user.subscribings.all())

    def test_user_profile_image(self):
        self.user.profile_image = 'profile_images/test_image.png'
        self.user.save()
        self.assertEqual(self.user.profile_image.name, 'profile_images/test_image.png')

    def test_user_gender(self):
        self.user.gender = 'Male'
        self.user.save()
        self.assertEqual(self.user.gender, 'Male')

    def test_user_birth_date(self):
        self.user.birth_date = '1990-01-01'
        self.user.save()
        self.assertEqual(self.user.birth_date, '1990-01-01')

    def test_user_author_verification_token(self):
        self.user.author_verification_token = 'test_token'
        self.user.save()
        self.assertEqual(self.user.author_verification_token, 'test_token')

    def test_user_verification_token(self):
        self.user.verification_token = 'verification_token'
        self.user.save()
        self.assertEqual(self.user.verification_token, 'verification_token')
