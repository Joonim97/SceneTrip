from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

from journals.serializers import JournalSerializer
from locations.serializers import LocationSaveSerializer
from .serializers import EmailCheckSerializer, PasswordCheckSerializer, SubUsernameSerializer, UserSerializer, MyPageSerializer
from .emails import send_verification_email
import uuid
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import ListAPIView
from rest_framework import generics, status
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings

from rest_framework.pagination import PageNumberPagination
User = get_user_model() # 필수 지우면 안됨

# 회원가입
class SignupAPIView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(user.password) # 비밀번호 해시
            user.verification_token = str(uuid.uuid4()) # 토큰생성
            user.is_active = False # 비활성화
            user.save()
            # 이메일 전송, 내용은 emails.py 에 적혀있는 내용들 전달
            send_verification_email(user)
            return Response({"message":"이메일을 전송하였습니다!!, 이메일을 확인해주세요"}, status=status.HTTP_201_CREATED)
        return Response(
            {"message": "회원가입에 실패했습니다.", "errors": serializer.errors}, 
            status=status.HTTP_400_BAD_REQUEST)

# 이메일 인증 메일이 날아올 경우
class VerifyEmailAPIView(APIView):
    def get(self, request, token):
        # 예외처리 해서 만약 안될경우 서버 안터지게
        try:
            user = get_object_or_404(User, verification_token=token)
            user.verification_token = ''
            user.is_active = True # 활성화
            user.save()
            return HttpResponse('회원가입이 완료되었습니다.', status=status.HTTP_200_OK)
        except:
            return HttpResponse({'error':'회원가입이 정상적으로 처리되지 않으셨습니다.'}, status=status.HTTP_400_BAD_REQUEST)

# 로그아웃
class LogoutAPIView(APIView):
	# login한 user에 대한 확인 필요.
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user: # 사용자가 맞으면
            refresh_token_str = request.data.get("refresh_token")
            refresh_token = RefreshToken(refresh_token_str)
            refresh_token.blacklist()

            return Response({"로그아웃 완료되었습니다"}, status=status.HTTP_200_OK)
        return Response({"message":"로그아웃을 실패하였습니다."}, status=status.HTTP_400_BAD_REQUEST)

# 마이페이지
class Mypage(ListAPIView): # 마이 페이지
    permission_classes = [IsAuthenticated]
    
    def get(self, request, nickname):
        my_page = get_object_or_404(User, nickname=nickname)
        if my_page == request.user:
            serializer = MyPageSerializer(my_page)
            return Response({'내 정보':serializer.data},status=200)
        return Response({"message": "다시 시도"}, status=400)
    
    def put(self, request, nickname):
        user = get_object_or_404(User, nickname=nickname)
        if user != request.user:
            return Response({"message": "수정할 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        
        if 'profile_image' in request.FILES:
            profile_image = request.FILES['profile_image']
            user.profile_image = profile_image 
        elif 'profile_image' in request.data and not request.data['profile_image']:
            # profile_image가 비어 있는 경우 (이미지 제거 요청)
            user.profile_image = None

        user.save()  # 변경 사항 저장
        return Response({"message": "프로필 정보가 업데이트되었습니다."}, status=status.HTTP_200_OK)

class SubscribeView(APIView):  # 구독 기능
    permission_classes = [IsAuthenticated]
    def post(self, request, nickname):
        # 구독 대상 사용자 조회
        user = get_object_or_404(User, nickname=nickname)
        me = request.user
        if me in user.subscribes.all(): # 내가 대상 사용자를 이미 구독하고 있는지 확인
            user.subscribes.remove(me)
            return Response("구독취소를 했습니다.", status=status.HTTP_200_OK)
        else:
            if nickname != me.nickname:
                user.subscribes.add(me)
                return Response("구독했습니다.", status=status.HTTP_200_OK)
            else:
                return Response("자신의 계정은 구독할 수 없습니다.", status=status.HTTP_200_OK)

# password 리셋
class PasswordResetRequestView(APIView):
    def post(self, request):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = f"{request.scheme}://{request.get_host()}/reset/{uid}/{token}/"
            # message = f"안녕하세요 {user.username}님,\n\n비밀번호 재설정을 위해 아래 링크를 클릭하세요:\n{reset_url}\n\n감사합니다."
            message = f'uid: {uid}  |  token: {token}'
            send_mail(
                '비밀번호 변경 요청',
                message,
                'noreply@gmail.com',
                [user.email],
                fail_silently=False,
            )
        return Response({"message": "해당 이메일을 사용하는 계정이 있는 경우, 비밀번호 재설정 메일을 전송합니다."}, status=status.HTTP_200_OK)
    
# password 재설정
class PasswordResetConfirmView(APIView):
    def post(self, request, uidb64, token):
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        if not default_token_generator.check_token(user, token):
            return Response({"message": "Invalid token or user ID."}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = PasswordCheckSerializer(data=request.data)
        if serializer.is_valid():
            # 유효성 검사를 통과한 데이터에서 비밀번호를 가져오기
            new_password = serializer.validated_data['new_password']
            user.set_password(new_password)
            user.save()
            return Response({"message": "비밀번호가 변경되었습니다."}, status=status.HTTP_200_OK)
        else:
            # 유효성 검사를 통과하지 못하면 오류 반환
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    

# Eamil 리셋
class EmailResetRequestView(APIView):
    def post(self, request):
        username = request.data.get('username')
        user = User.objects.filter(username=username).first()
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = f"{request.scheme}://{request.get_host()}/reset/{uid}/{token}/"
            # message = f"안녕하세요 {user.username}님,\n\n비밀번호 재설정을 위해 아래 링크를 클릭하세요:\n{reset_url}\n\n감사합니다."
            message = f'uid: {uid}  |  token: {token}'
            send_mail(
                '이메일 변경 요청',
                message,
                'noreply@gmail.com',
                [user.email],
                fail_silently=False,
            )
        return Response({"message": "해당 유저을 사용하는 계정이 있는 경우, 이메일 재설정 메일을 전송합니다."}, status=status.HTTP_200_OK)
    
# Email 재설정
class EamilResetConfirmView(APIView):
    def post(self, request, uidb64, token):
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        if not default_token_generator.check_token(user, token):
                    return Response({"message": "토큰 또는 아이디 값이 맞지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)
                
        serializer = EmailCheckSerializer(data=request.data)
        if serializer.is_valid():
            # 유효성 검사를 통과한 데이터에서 이메일을 가져오기
            new_email = serializer.validated_data['new_email']
            user.email = new_email
            user.save()
            return Response({"message": "이메일이 변경되었습니다."}, status=status.HTTP_200_OK)
        else:
            # 유효성 검사를 통과하지 못하면 오류 반환
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class MyJournalsListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, nickname):
        user = get_object_or_404(User, nickname=nickname)  # 닉네임으로 사용자 조회
        if user == request.user:  # 요청한 사용자가 본인인지 확인
            journals = user.my_journals.all()  # 사용자의 모든 저널 가져오기
            serializer = JournalSerializer(journals, many=True)
            return Response({'내가 쓴 글': serializer.data}, status=200)
        
        return Response({"message": "다시 시도"}, status=400)  # 본인이 아닐 경우
    
class SavedLocationsListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, nickname):
        user = get_object_or_404(User, nickname=nickname)  # 닉네임으로 사용자 조회
        if user == request.user:  # 요청한 사용자가 본인인지 확인
            saved_locations = user.location_save.all()  # 사용자의 모든 저장된 촬영지 가져오기
            serializer = LocationSaveSerializer(saved_locations, many=True)
            return Response({'저장된 촬영지': serializer.data}, status=200)

        return Response({"message": "다시 시도"}, status=400)  # 본인이 아닐 경우
    
class SubscribingsListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, nickname):
        user = get_object_or_404(User, nickname=nickname)  # 닉네임으로 사용자 조회
        if user == request.user:  # 요청한 사용자가 본인인지 확인
            subscribings = user.subscribings.all()  # 사용자의 모든 구독 가져오기
            serializer = SubUsernameSerializer(subscribings, many=True)
            return Response({'구독 중인 사용자들': serializer.data}, status=200)

        return Response({"message": "다시 시도"}, status=400)  # 본인이 아닐 경우
    
class SubsribingsjournalAPI(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, nickname, sub_nickname):
        user = get_object_or_404(User, nickname=nickname) # 닉네임으로 사용자 조회
        sub_user = get_object_or_404(User, nickname=sub_nickname) # 구독한 사용자를 조회

        if user.subscribings.filter(nickname=sub_nickname).exists():
        # 구독한 사용자가 작성한 저널들 가져오기
            journals = sub_user.my_journals.all() # my_journals = 역참조한 글들
            serializer = JournalSerializer(journals, many=True)
            return Response({'구독한 사용자의 글': serializer.data}, status=200)
    
        return Response({"message": "구독한 사용자가 아닙니다."}, status=403)