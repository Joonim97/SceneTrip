from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.generics import ListAPIView
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from SceneTrip import settings
from accounts.forms import CheckPasswordForm
from communities.serializers import CommunitySerializer
from journals.serializers import JournalSerializer, JournalLikeSerializer
from locations.serializers import LocationSaveSerializer
from .serializers import PasswordCheckSerializer, SubUsernameSerializer, UserSerializer, MyPageSerializer
from .emails import send_verification_email, send_verification_email_reset, send_verification_password_reset
import requests
import uuid

User = get_user_model() # 필수 지우면 안됨

#################################################################################################################
#################################################################################################################

# Custom JWTAuthentication
class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        access_token = request.COOKIES.get('access_token')

        if access_token is None:
            return None
        
        validated_token = self.get_validated_token(access_token)

        return self.get_user(validated_token), validated_token

# Parents Class 모음
# 커스텀 페이지네이션 // 마이페이지에 들어가는 내용들 페이지네이션
class CustomPagination(PageNumberPagination):
        page_size = 5
        page_size_query_param = 'page_size'
        max_page_size = 100

# parents class // 마이페이지 전용
class BaseListAPIView(generics.ListAPIView):
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]

    def get_user_nickname(self, nickname):
        return get_object_or_404(User, nickname=nickname) # 닉네임으로 사용자 조회

# APIView를 사용하는 parents class // 로그인이 필요한 경우에 사용
class PermissionAPIView(APIView):
    permission_classes = [IsAuthenticated]

#################################################################################################################
#################################################################################################################

# 회원가입
class SignupAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return render(request, 'accounts/signup.html')  # 회원가입 HTML 렌더링
    
    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                email = serializer.validated_data['email']
            else:
                email = request.data.get('email')
            existing_user = User.objects.filter(email=email).first()
            # 유저가 있지만 is_active = False
            if existing_user:
                if not existing_user.is_active:
                    existing_user.delete()
                    serializer = UserSerializer(data=request.data)
                    if serializer.is_valid():
                        user = serializer.save()
                        user.set_password(request.data.get('password'))
                        user.verification_token = str(uuid.uuid4())
                        user.author_verification_token = str(uuid.uuid4()) # 토큰 생성
                        user.is_active = False
                        user.save()
                        
                        send_verification_email(user)  # 이메일 전송
                        messages.success(request, "이메일을 전송하였습니다! 이메일을 확인해주세요.")
                        # return Response({"message": "이메일을 전송하였습니다. 이메일을 확인해주세요."}, status=status.HTTP_201_CREATED)
                        return redirect('accounts:login_page')  # 메시지를 팝업으로 보여주기 위해 리디렉션

                else:
                    messages.error(request, "이미 존재하는 사용자입니다.")
                    # return Response({"error": "회원가입에 실패했습니다. 이미 존재하는 사용자입니다."}, status=status.HTTP_400_BAD_REQUEST)
                    return redirect('accounts:signup')  

            else:
                if serializer.is_valid():
                    user = serializer.save()
                    user.set_password(request.data.get('password')) 
                    user.verification_token = str(uuid.uuid4())
                    user.author_verification_token = str(uuid.uuid4()) # 토큰 생성
                    user.is_active = False
                    user.save()

                    send_verification_email(user)
                    messages.success(request, "이메일을 전송하였습니다! 이메일을 확인해주세요.")
                    return redirect('accounts:login_page')  # 메시지를 팝업으로 보여주기 위해 리디렉션
                else:
                    messages.error(request, "회원가입에 실패했습니다.")
                    # return Response(
                    #     {"error": "회원가입에 실패했습니다.", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                    return redirect('accounts:signup')  
        except Exception as e:
            messages.error(request, "오류가 발생했습니다.")
            # return Response(
            #     {"error": "오류가 발생했습니다."}, status=status.HTTP_400_BAD_REQUEST)
            return redirect('accounts:signup')  



# 이메일 인증 
class VerifyEmailAPIView(APIView):
    def get(self, request, token):
        try:
            # 토큰으로 사용자를 조회
            user = get_object_or_404(User, verification_token=token)
            # 이메일 인증 후 상태 업데이트
            if not user.is_active:  # 만약 사용자 비활성화 상태라면
                user.verification_token = ''  # 토큰 초기화
                user.is_active = True  # 사용자 활성화
                
                # 유저 등급 업데이트
                if user.grade == 'author':
                    user.grade = 'no_author'  # 이메일 인증 후 NORMAL로 설정
                user.save()  # 변경 사항 저장
                return Response('회원가입이 완료되었습니다.', status=status.HTTP_200_OK)
            else:
                return Response('이메일이 이미 인증되었습니다.', status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': '정상적으로 처리되지 않으셨습니다.', 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)    
        

class LoginView(APIView):
    def get(self, request):
        return render(request, 'accounts/login.html')  # login.html 템플릿 렌더링

# 회원가입시 grade가 journal, 관리자가 해당 link를 누른경우
class VerifyjJournalEmailAPIView(APIView):
    def get(self, request, token):
        try:
            if request.user: # 사용자가 맞으면
                refresh_token = request.data.get("refresh") 
                if not refresh_token: # refresh token 이 없을경우
                    return Response({"error": "리프레시 토큰이 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    refresh_token = RefreshToken(refresh_token)
                    refresh_token.blacklist()
                    return Response({"로그아웃 완료되었습니다"}, status=status.HTTP_200_OK)
                except:
                    return Response({"error":"로그아웃을 실패하였습니다."}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({"error":"로그인을 해주시길 바랍니다"}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'error':'오류가 발생하였습니다.'}, status=status.HTTP_400_BAD_REQUEST)


class DeleteAPIView(APIView):
    def get(self, request, nickname):
        serializer = PasswordCheckSerializer(data=request.data)
        context ={
            "nickname":nickname,
        }
        print(context)
        return render(request, 'accounts/signout.html', context)
    
    def delete(self, request, nickname):
        user = request.user
        deleted_user = get_object_or_404(User, nickname=nickname)

        if user != deleted_user:
            return Response({"error": "본인계정만 탈퇴하실수 있습니다"}, status=400)  # 본인이 아닐 경우

        serializer = PasswordCheckSerializer(data=request.data)
        if serializer.is_valid():
            password = serializer.validated_data['password']  # 수정된 부분

            # 비밀번호 확인
            if user.check_password(password):
                user.is_active = False  
                user.save()
                return Response({"message": "탈퇴 완료하였습니다"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "비밀번호가 올바르지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 유효성 검사를 통과하지 못한 경우
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 마이페이지
class Mypage(ListAPIView):  # 마이 페이지
    serializer_class = MyPageSerializer

    def get(self, request, nickname):
        my_page = get_object_or_404(User, nickname=nickname)
        
        # 요청한 사용자가 본인인지 확인
        serializer = MyPageSerializer(my_page)

        # 'edit' 파라미터가 있으면 회원정보 수정 페이지 렌더링
        if request.GET.get('edit'):
            return render(request, 'accounts/edit_profile.html', {'user': my_page})
        else:
            return render(request, 'accounts/mypage.html', {'user': serializer.data})

    def put(self, request, nickname):
        user = get_object_or_404(User, nickname=nickname)
        if user != request.user:
            return Response({"error": "사용자만 수정 가능합니다."}, status=status.HTTP_403_FORBIDDEN)

        user.nickname = request.data.get('nickname', user.nickname)
        user.email = request.data.get('email', user.email)
        user.birth_date = request.data.get('birth_date', user.birth_date)
        user.gender = request.data.get('gender', user.gender)

        if 'profile_image' in request.FILES:
            user.profile_image = request.FILES['profile_image']
        elif 'profile_image' in request.data and not request.data['profile_image']:
            user.profile_image = None

        user.save()  # 변경 사항 저장
        return Response({"message": "프로필 정보가 업데이트되었습니다."}, status=status.HTTP_200_OK)
    

def mypage(request, nickname):
    # 닉네임을 기준으로 해당 사용자를 가져옵니다.
    user = get_object_or_404(User, nickname=nickname)
    serializer = MyPageSerializer(user)
    print(request.user)
    print(request.headers)
    
    # 사용자 정보와 관련된 데이터를 렌더링합니다.
    context = {
        'user': serializer.data,
    }
    
    return render(request, 'accounts/mypage.html', context)


# 비밀번호 리셋 로직
class PasswordResetRequestView(PermissionAPIView):
    def post(self, request):
        try:
            user = request.user
            # 이메일, 새 비밀번호 입력
            email = request.data.get("email")
            new_password = request.data.get("new_password")

            # 이메일을 안썼을 경우
            if not email:
                    return Response({"error": "이메일을 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)
            # 새 비밀번호를 입력 안썻을 경우
            if not new_password:
                    return Response({"error": "새 비밀번호를 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)
            
            # 비밀번호 유효성검사
            password_serializer = PasswordCheckSerializer(data={'password': new_password})
            if not password_serializer.is_valid():
                return Response(password_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # 인증 토큰 생성
            user.verification_token = str(uuid.uuid4())
            user.set_password(new_password)  # 새 비밀번호 설정
            user.save()

            # 이메일 전송
            send_verification_password_reset(user)  # 새로운 이메일로 인증 메일 전송
            return Response({"message": "비밀번호 변경 확인을 위한 이메일을 전송했습니다."}, status=status.HTTP_200_OK)
        
        except:
            return Response({"error": "사용자를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)


# 비밀번호 리셋 이메일 인증 메일이 날아올 경우
class PasswordResetConfirmView(APIView):
    def get(self, request, token):
        try:
            user = get_object_or_404(User, verification_token=token)
            user.password = user.new_password
            user.new_password = ''
            user.verification_token = ''
            user.is_active = True # 활성화
            user.save()
            return HttpResponse('비밀번호 변경이 완료되었습니다.', status=status.HTTP_200_OK)
        except:
            return HttpResponse({'error':'비밀번호 변경이 정상적으로 처리되지 않으셨습니다.'}, status=status.HTTP_400_BAD_REQUEST)    


# 이메일 초기화
class EmailResetRequestView(PermissionAPIView):
    def post(self, request):
        try:
            user = request.user
            new_email = request.data.get("new_email")

            # 이메일을 안썼을 경우
            if not new_email:
                    return Response({"error": "새 이메일을 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)

            # 중복 이메일 확인
            if User.objects.filter(email=new_email).exists():
                return Response({"error": "이미 사용 중인 이메일입니다."}, status=status.HTTP_400_BAD_REQUEST)

            # 새로운 이메일에 대한 인증 토큰 생성
            user.verification_token = str(uuid.uuid4())
            user.new_email = new_email  # 새로운 이메일 필드 추가 필요
            user.save()

            # 이메일 전송
            send_verification_email_reset(user)  # 새로운 이메일로 인증 메일 전송
            return Response({"message": "이메일 변경 확인을 위한 이메일을 전송했습니다."}, status=status.HTTP_200_OK)
        
        except:
            return Response({"error": "사용자를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)


# 이메일 인증 메일이 날아올 경우
class EamilResetConfirmView(APIView):
    def get(self, request, token):
        try:
            user = get_object_or_404(User, verification_token=token)
            user.email = user.new_email
            user.new_email = ''
            user.verification_token = ''
            user.is_active = True # 활성화
            user.save()
            return HttpResponse('이메일 변경이 완료되었습니다.', status=status.HTTP_200_OK)
        except:
            return HttpResponse({'error':'이메일 변경이 정상적으로 처리되지 않으셨습니다.'}, status=status.HTTP_400_BAD_REQUEST)


# 로그아웃
class LogoutAPIView(PermissionAPIView):
    def post(self, request):
        try:
            if request.user:
                refresh_token = request.data.get("refresh") 
                if not refresh_token: # refresh token 이 없을경우
                    return Response({"error": "리프레시 토큰이 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    refresh_token = RefreshToken(refresh_token)
                    refresh_token.blacklist()
                    return Response({"로그아웃 완료되었습니다"}, status=status.HTTP_200_OK)
                except:
                    return Response({"error":"로그아웃을 실패하였습니다."}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({"error":"로그인을 해주시길 바랍니다"}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'error':'오류가 발생하였습니다.'}, status=status.HTTP_400_BAD_REQUEST)

        
        
# 구독 기능
class SubscribeView(PermissionAPIView):

    def post(self, request, nickname):
        user = get_object_or_404(User, nickname=nickname)
        me = request.user
        
        if me in user.subscribes.all():  # 이미 구독한 경우
            user.subscribes.remove(me)
            return Response({"message": "구독 취소했습니다."}, status=status.HTTP_200_OK)
        else:  # 구독하지 않은 경우
            if nickname != me.nickname:
                user.subscribes.add(me)
                return Response({"message": "구독했습니다."}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "자신을 구독할 수 없습니다."}, status=status.HTTP_200_OK)


# 내가 쓴 글
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


# 촬영지 저장 전체목록
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


# 구독자 전체목록
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


# 구독자 글
class SubsribingsjournalAPI(BaseListAPIView):
    def get(self, request, nickname, sub_nickname):
        user = self.get_user_nickname(nickname)
        sub_user = get_object_or_404(User, nickname=sub_nickname) # 구독한 사용자를 조회
        
        if user.subscribings.filter(nickname=sub_nickname).exists(): 
            journals = sub_user.my_journals.select_related('author').all() # 구독한 사용자가 작성한 저널들 가져오기

            # 페이지네이션
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(journals, request)
            if page is not None:
                serializer = JournalSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = JournalSerializer(journals, many=True)
            return Response({'구독한 사용자의 글': serializer.data}, status=status.HTTP_200_OK)
        return Response({"error": "구독한 사용자가 아닙니다."}, status=400)


# 내가 작성한 커뮤니티 목록
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


# 내가 좋아요한 저널 글 목록
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


class UserInfoView(APIView):
    def get(self, request):
        user = request.user
        return Response({
            'username' : user.username,
            'user_id' : user.user_id,
            'nickname': user.nickname,
            'email': user.email,
            'grade': user.grade  # grade 필드를 추가
        })
        
        
class EditProfileView(APIView):

    def get(self, request, nickname):
        user = get_object_or_404(User, nickname=nickname)

        return render(request, 'accounts/edit_profile.html', {'user': user})

    def put(self, request, nickname):

        user = get_object_or_404(User, nickname=nickname)

        if user != request.user:
            return Response({"error": "사용자만 수정 가능합니다."}, status=status.HTTP_403_FORBIDDEN)
        
        # 사용자 입력 정보 업데이트
        user.nickname = request.data.get('nickname', user.nickname)
        user.email = request.data.get('email', user.email)
        user.birth_date = request.data.get('birth_date', user.birth_date)
        user.gender = request.data.get('gender', user.gender)

        # 프로필 이미지 업데이트
        if 'profile_image' in request.FILES:
            user.profile_image = request.FILES['profile_image']

        user.save()  # 변경사항 저장
        return Response({"message": "프로필 정보가 업데이트되었습니다."}, status=status.HTTP_200_OK)

#################################################################################################################
#################################################################################################################

# 카카오 로그인 페이지를 렌더링하는 뷰
def kakaologinpage(request):
    context = {
        'KAKAO_JAVA_SCRIPTS_API_KEY': settings.KAKAO_JAVA_SCRIPTS_API_KEY,  # settings.py에 정의된 설정 값
    }
    return render(request, 'accounts/kakao_login.html', context)  # HTML 파일 경로를 적절하게 수정

# 카카오 로그인 완료 창(실패창은 안나옴)
# def index(request):
#     return render(request, 'accounts/index.html')

# 소셜로그인(카카오,) 추가가능
class SocialLoginView(APIView):
    def get(self, request, provider):
        if provider == "kakao":
            client_id = settings.KAKAO_REST_API_KEY
            redirect_uri = f"{settings.BASE_URL}/api/accounts/social/callback/{provider}/"
            scope = "gender, birthday, birthyear" # 선택 제공 동의를 요청
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

# 소셜로그인 callback(카카오,) 추가가능
class SocialCallbackView(APIView):
    def get(self, request, provider):
        try:
            code = request.GET.get("code")
            access_token = self.get_token(provider, code)

            if access_token:
                user_info = self.get_user_info(provider, access_token)

                # 제공받는 데이터들
                if provider == "kakao":
                    username = user_info['kakao_account'].get('name')
                    email = user_info['kakao_account'].get('email')
                    gender = user_info['kakao_account'].get('gender')
                    birthday = user_info['kakao_account'].get('birthday')
                    birthyear = user_info['kakao_account'].get('birthyear')
                    user_id = email

                # model 에서 birth_date 양식 통일 (0000-00-00)
                if birthyear and birthday:
                    birth_date = f"{birthyear}-{birthday[:2]}-{birthday[2:]}"
                else:
                    birth_date = None

                user_data, created = self.get_or_create_user(provider, email, username, gender, birth_date, user_id)

                if created:
                    refresh = RefreshToken.for_user(user_data)
                    access = str(refresh.access_token)
                    response = redirect(f'/api/accounts/set_nickname/')
                    response.set_cookie('access_token', access)
                    response.set_cookie('refresh_token', str(refresh))
                    return response
                #     tokens = {
                #         "access": str(refresh.access_token),
                #         "refresh": str(refresh)
                #     }
                #     # return redirect(f'/api/accounts/set_nickname/?refresh={tokens["refresh"]}&access={tokens["access"]}')
                # else:
                #     tokens = self.create_jwt_token(user_data)
                
                # response_data = {
                #     "access_token": tokens["access"],
                #     "refresh_token": tokens["refresh"],
                #     "email": email,
                #     "gender": gender,
                #     "username": username,
                #     "birth_date": birth_date,
                #     "user_id": user_id,
                #     "is_new_user": created
                # }
                refresh = RefreshToken.for_user(user_data)
                access = str(refresh.access_token)
                response = redirect('/')
                response.set_cookie('access_token', access)
                response.set_cookie('refresh_token', str(refresh))
                return response
            
                # return Response(response_data,  status=status.HTTP_200_OK)
            else:
                return Response("Error retrieving access token", status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # 토큰
    def get_token(self, provider, code):
        if provider == "kakao":
            token_url = "https://kauth.kakao.com/oauth/token"
            client_id = settings.KAKAO_REST_API_KEY
        else:
            raise ValueError("지원되지 않는 소셜 로그인 제공자입니다.")
        
        redirect_uri = f"{settings.BASE_URL}/api/accounts/social/callback/{provider}/"
        data = {
            "grant_type": "authorization_code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "code": code,
        }
        response = requests.post(token_url, data=data)
        return response.json().get("access_token")
    
    def get_user_info(self, provider, access_token):
        if provider == "kakao":
            user_info_url = "https://kapi.kakao.com/v2/user/me"
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get(user_info_url, headers=headers)
            return response.json()
        else:
            raise ValueError("지원되지 않는 소셜 로그인 제공자입니다.")

        # headers = {"Authorization": f"Bearer {access_token}"}
        # response = requests.get(user_info_url, headers=headers)
        # return response.json()

    def get_or_create_user(self, provider, email, username, gender, birth_date, user_id):
        user, created = User.objects.get_or_create(
            email=email,
            gender=gender,
            birth_date=birth_date,
            defaults={
                # "nickname": nickname,
                "username": username,
                "user_id": user_id
            },
        )
        if created:
            user.set_unusable_password()
            user.save()

        return user, created

    # 토큰에 담을 내용
    def create_jwt_token(self, user_data):
        if isinstance(user_data, dict):
            email = user_data.get("email")
            # nickname = user_data.get("nickname")
            username = user_data.get("username")
            gender = user_data.get("gender")
            birth_date = user_data.get("birth_date")
            user_id = email
            user = User.objects.get(email=email, username=username, gender=gender, birth_date=birth_date, user_id = user_id)
        else:
            user = user_data

        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
    
    def create_jwt_token(self, user_data):
        if isinstance(user_data, dict):
            email = user_data.get("email")
            username = user_data.get("username")
            gender = user_data.get("gender")
            birth_date = user_data.get("birth_date")
            user_id = email
            user = User.objects.get(email=email, username=username, gender=gender, birth_date=birth_date, user_id=user_id)
        else:
            user = user_data

        refresh = RefreshToken.for_user(user)
        
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

class SetNicknameView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        nickname = request.data.get('nickname')
        if nickname:
            if User.objects.filter(nickname=nickname).exists():  # 이미 존재하는 닉네임을 입력한 경우
                return Response({'available': False}, status=200)
            else:
                user = request.user
                user.nickname = nickname
                user.save()  # 저장
                return Response({'available': True}, status=200)
        return Response({'error': 'Nickname is required.'}, status=400)

    def get(self, request):
        refresh = request.COOKIES.get('refresh_token')
        access = request.COOKIES.get('access_token')

        return render(request, 'accounts/set_nickname.html', {
            'refresh_token': refresh,
            'access_token': access
        })