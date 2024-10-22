from rest_framework import status
from rest_framework.test import APITestCase
from models import User
from serializers import UserSerializer, PasswordCheckSerializer, EmailCheckSerializer, SubUsernameSerializer, MyPageSerializer

class UserSerializerTests(APITestCase):

    def setUp(self):
        # 테스트 사용자 생성
        self.user = User.objects.create_user(
            username='testuser',
            user_id='testuser123',
            email='testuser@example.com',
            password='password123',
            nickname='testnickname'
        )

    def test_valid_user_serializer(self):
        # 유효한 사용자 데이터 테스트
        data = {
            'username': 'newuser',
            'password': 'Password123!',
            'nickname': 'newnickname',
            'email': 'newuser@example.com',
            'user_id': 'newuser123',
            'gender': 'Male',
            'grade': User.NORMAL
        }
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_duplicate_email(self):
        # 이메일중복 검증
        data = {
            'username': 'newuser',
            'password': 'Password123!',
            'nickname': 'newnickname',
            'email': 'testuser@example.com',  # 이미 존재하는 이메일주소
            'user_id': 'newuser123',
            'gender': 'Male',
            'grade': User.NORMAL
        }
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors['non_field_errors'], ["사용 중인 이메일입니다."])

    def test_invalid_nickname_length(self):
        # 닉네임길이 검증
        data = {
            'username': 'newuser',
            'password': 'Password123!',
            'nickname': 'ab',  # 유효하지 않은 닉네임
            'email': 'newuser@example.com',
            'user_id': 'newuser123',
            'gender': 'Male',
            'grade': User.NORMAL
        }
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors['nickname'], ["닉네임은 3자 이상 20자 이하여야 합니다."])

    def test_password_validation(self):
        # 비밀번호 유효성 검증
        data = {
            'username': 'newuser',
            'password': 'short',  # 유효하지 않은 비밀번호
            'nickname': 'newnickname',
            'email': 'newuser@example.com',
            'user_id': 'newuser123',
            'gender': 'Male',
            'grade': User.NORMAL
        }
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors['password'], ["비밀번호는 10글자 이상 20글자 이하여야 합니다."])

class PasswordCheckSerializerTests(APITestCase):

    def test_valid_password(self):
        # 유효한 비밀번호 테스트
        data = {'password': 'Password123!'}
        serializer = PasswordCheckSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_password_missing_letter(self):
        # 알파벳이 없는 비밀번호 검증
        data = {'password': '1234567890!'}
        serializer = PasswordCheckSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors['password'], ["비밀번호는 하나 이상의 영문이 포함되어야 합니다."])

    def test_invalid_password_missing_number(self):
        # 숫자가 없는 비밀번호 검증
        data = {'password': 'Password!'}
        serializer = PasswordCheckSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors['password'], ["비밀번호는 하나 이상의 숫자가 포함되어야 합니다."])

class EmailCheckSerializerTests(APITestCase):

    def test_valid_email(self):
        # 유효한 이메일 테스트
        data = {'new_email': 'newemail@example.com'}
        serializer = EmailCheckSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_email(self):
        # 유효하지 않은 이메일 검증
        data = {'new_email': 'invalidemail'}
        serializer = EmailCheckSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors['new_email'], ["이메일을 입력해주십시오."])

class SubUsernameSerializerTests(APITestCase):

    def setUp(self):
        # 테스트용 사용자 생성
        self.user = User.objects.create_user(
            username='testuser',
            user_id='testuser123',
            email='testuser@example.com',
            password='password123',
            nickname='testnickname'
        )

    def test_sub_username_serialization(self):
        # 사용자 닉네임 직렬화 테스트
        serializer = SubUsernameSerializer(self.user)
        self.assertEqual(serializer.data, {'nickname': 'testnickname'})

class MyPageSerializerTests(APITestCase):

    def setUp(self):
        # 테스트용 사용자 생성
        self.user = User.objects.create_user(
            username='testuser',
            user_id='testuser123',
            email='testuser@example.com',
            password='password123',
            nickname='testnickname'
        )

    def test_my_page_serialization(self):
        # 마이페이지 직렬화 테스트
        serializer = MyPageSerializer(self.user)
        expected_data = {
            'username': 'testuser',
            'nickname': 'testnickname',
            'email': 'testuser@example.com',
            'birth_date': None,
            'gender': None,
            'subscribings': [],  
            'my_journals': [], 
            'profile_image': None,
            'location_save': [], 
            'communities_author': [], 
            'journal_likes': []  
        }
        self.assertEqual(serializer.data, expected_data)
