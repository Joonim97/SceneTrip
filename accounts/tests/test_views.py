from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, status
from SceneTrip import settings
from communities.serializers import CommunitySerializer
from journals.serializers import JournalSerializer, JournalLikeSerializer
from locations.serializers import LocationSaveSerializer
from serializers import PasswordCheckSerializer, SubUsernameSerializer, UserSerializer, MyPageSerializer
from views import BaseListAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication
User = get_user_model() 

class AccountsAPITestCase(APITestCase):

    def setUp(self):
        # 테스트용 사용자 생성
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword',
            nickname='testnickname'
        )
        self.user.is_active = False
        self.user.verification_token = 'testtoken'
        self.user.save()

    def test_signup(self):
        url = reverse('accounts:signup')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword',
            'nickname': 'newnickname'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('이메일을 전송하였습니다.', response.data['message'])

    def test_email_verification(self):
        url = reverse('accounts:verify_email', args=['testtoken'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_login(self):
        url = reverse('accounts:login')
        response = self.client.post(url, {'username': 'testuser', 'password': 'testpassword'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_account(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse('accounts:delete', args=['testnickname'])
        response = self.client.delete(url, {'password': 'testpassword'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_mypage_access(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse('accounts:mypage', args=['testnickname'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nickname'], 'testnickname')

    def test_mypage_access_other_user(self):
        other_user = User.objects.create_user(
            username='otheruser',
            email='otheruser@example.com',
            password='otherpassword',
            nickname='othernickname'
        )
        self.client.login(username='testuser', password='testpassword')
        url = reverse('accounts:mypage', args=['othernickname'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_request(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse('accounts:password_reset_request')
        response = self.client.post(url, {'email': 'testuser@example.com', 'new_password': 'newpassword'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_email_reset_request(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse('accounts:email_reset_request')
        response = self.client.post(url, {'new_email': 'newemail@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse('accounts:logout')
        response = self.client.post(url, {'refresh': 'some_refresh_token'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

# 내가 쓴 저널 목록을 가져오는 API 뷰
class MyJournalsListAPIView(BaseListAPIView):
    def get(self, request, nickname):
        user = self.get_user_nickname(nickname)

        if user == request.user:  # 요청한 사용자가 본인인지 확인
            journals = user.my_journals.select_related('author').all()  # 사용자의 모든 저널 가져오기

            # 페이지네이션
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(journals, request)
            if page is not None:
                serializer = JournalSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
            
            serializer = JournalSerializer(journals, many=True)
            return Response({'내가 쓴 글': serializer.data}, status=status.HTTP_200_OK)
        return Response({"error": "다시 시도"}, status=status.HTTP_400_BAD_REQUEST)  # 본인이 아닐 경우


# 촬영지 저장 전체 목록을 가져오는 API 뷰
class SavedLocationsListAPIView(BaseListAPIView):
    def get(self, request, nickname):
        user = self.get_user_nickname(nickname)

        if user == request.user:  # 요청한 사용자가 본인인지 확인
            saved_locations = user.location_save.select_related('location').all()  # 사용자의 모든 저장된 촬영지 가져오기

            # 페이지네이션
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(saved_locations, request)
            if page is not None: 
                serializer = LocationSaveSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = LocationSaveSerializer(saved_locations, many=True)
            return Response({'저장된 촬영지': serializer.data}, status=status.HTTP_200_OK)
        return Response({"error": "다시 시도"}, status=400)  # 본인이 아닐 경우


# 구독자 전체 목록을 가져오는 API 뷰
class SubscribingsListAPIView(BaseListAPIView):
    def get(self, request, nickname):
        user = self.get_user_nickname(nickname)

        if user == request.user:
            subscribings = user.subscribings.prefetch_related('subscribes')  # 사용자의 모든 구독 가져오기

            # 페이지네이션
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(subscribings, request)
            if page is not None: 
                serializer = SubUsernameSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = SubUsernameSerializer(subscribings, many=True)
            return Response({'구독 중인 사용자들': serializer.data}, status=status.HTTP_200_OK)
        return Response({"error": "다시 시도"}, status=400)  # 본인이 아닐 경우


# 구독자의 저널 글 목록을 가져오는 API 뷰
class SubsribingsjournalAPI(BaseListAPIView):
    def get(self, request, nickname, sub_nickname):
        user = self.get_user_nickname(nickname)
        sub_user = get_object_or_404(User, nickname=sub_nickname)  # 구독한 사용자를 조회
        
        if user.subscribings.filter(nickname=sub_nickname).exists(): 
            journals = sub_user.my_journals.select_related('author').all()  # 구독한 사용자가 작성한 저널들 가져오기

            # 페이지네이션
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(journals, request)
            if page is not None:
                serializer = JournalSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = JournalSerializer(journals, many=True)
            return Response({'구독한 사용자의 글': serializer.data}, status=status.HTTP_200_OK)
        return Response({"error": "구독한 사용자가 아닙니다."}, status=400)

# 내가 작성한 커뮤니티 목록을 가져오는 API 뷰
class MyCommunityListAPIView(BaseListAPIView):
    def get(self, request, nickname):
        user = self.get_user_nickname(nickname)

        if user == request.user:
            communities = user.communities_author.select_related('author').all()  # 사용자가 작성한 모든 커뮤니티 가져오기

            # 페이지네이션
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(communities, request)
            if page is not None:
                serializer = CommunitySerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
            
            serializer = CommunitySerializer(communities, many=True)
            return Response({'커뮤니티 내가 쓴 글': serializer.data}, status=status.HTTP_200_OK)
        return Response({"error": "다시 시도"}, status=400)  # 본인이 아닐 경우


# 내가 좋아요한 저널 목록을 가져오는 API 뷰
class LikeJournalsListAPIView(BaseListAPIView):
    def get(self, request, nickname):
        user = self.get_user_nickname(nickname)

        if user == request.user:  # 요청한 사용자가 본인인지 확인
            like_journal = user.journal_likes.select_related('user').all()  # 사용자의 모든 저널 가져오기

            # 페이지네이션
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(like_journal, request)
            if page is not None:
                serializer = JournalSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = JournalLikeSerializer(like_journal, many=True)
            return Response({'내가 좋아요한 저널 글 목록': serializer.data}, status=status.HTTP_200_OK)
        return Response({"error": "다시 시도"}, status=400)  # 본인이 아닐 경우   

# 사용자 정보 조회 API 뷰
class UserInfoView(APIView):
    def get(self, request):
        user = request.user
        return Response({
            'username': user.username,
            'user_id': user.user_id,
            'nickname': user.nickname,
            'email': user.email,
            'grade': user.grade  # grade 필드를 추가
        })

#################################################################################################################
#################################################################################################################

# 카카오 로그인 페이지를 렌더링하는 뷰
def kakaologinpage(request):
    context = {
        'KAKAO_JAVA_SCRIPTS_API_KEY': settings.KAKAO_JAVA_SCRIPTS_API_KEY,  # settings.py에 정의된 설정 값
    }
    return render(request, 'accounts/kakao_login.html', context)  # HTML 파일 경로를 적절하게 수정

# 카카오 로그인 완료 창(실패창은 안나옴)
def index(request):
    return render(request, 'accounts/index.html')

# 소셜로그인(카카오) 추가 가능
class SocialLoginView(APIView):
    def get(self, request, provider):
        if provider == "kakao":
            client_id = settings.KAKAO_REST_API_KEY
            redirect_uri = f"{settings.BASE_URL}/api/accounts/social/callback/{provider}/"
            scope = "account_email, gender, birthday, birthyear"  # 선택 제공 동의를 요청
            auth_url = (
                f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}"
                f"&redirect_uri={redirect_uri}&response_type=code"
                f"&scope={scope}"
            )
        else:
            return Response(
                {"error": "지원되지 않는 소셜 로그인 제공자입니다."}, status=400
            )
        return redirect(auth_url)

# 소셜로그인 callback(카카오) 추가 가능
class SocialCallbackView(APIView):
    def get(self, request, provider):
        code = request.GET.get("code")

        access_token = self.get_token(provider, code)
        user_info = self.get_user_info(provider, access_token)

        # 제공받는 데이터들
        if provider == "kakao":
            username = user_info['kakao_account'].get('name')
            email = user_info['kakao_account'].get('email')
            gender = user_info['kakao_account'].get('gender')
            nickname = user_info["properties"].get("nickname")
            birthday = user_info['kakao_account'].get('birthday')
            birthyear = user_info['kakao_account'].get('birthyear')

        # model에서 birth_date 양식 통일 (0000-00-00)
        if birthyear and birthday:
            birth_date = f"{birthyear}-{birthday[:2]}-{birthday[2:]}"
        else:
            birth_date = None

        user_data = self.get