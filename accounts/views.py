from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

from journals.serializers import JournalSerializer
from locations.serializers import LocationSaveSerializer
from .serializers import EmailCheckSerializer, PasswordCheckSerializer, SubUsernameSerializer, UserSerializer, MyPageSerializer
from .emails import send_verification_email, send_verification_email_reset
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
            user.grade = 1
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

            refresh_token = request.data.get("refresh") 
            if not refresh_token: # refresh token 이 없을경우
                return Response({"message": "리프레시 토큰이 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                refresh_token = RefreshToken(refresh_token)
                refresh_token.blacklist()
                return Response({"로그아웃 완료되었습니다"}, status=status.HTTP_200_OK)
            except:
                return Response({"message":"로그아웃을 실패하였습니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"로그인을 해주시길 바랍니다"}, status=status.HTTP_400_BAD_REQUEST)

# 마이페이지
class Mypage(ListAPIView): # 마이 페이지
    permission_classes = [IsAuthenticated]
    
    def get(self, request, nickname):
        try: # 사용자가 맞는지 아닌지에 대한 예외처리
            my_page = get_object_or_404(User, nickname=nickname)
        except:
            return Response({"message": "해당 유저를 찾을 수 없습니다."}, status=404)
        if my_page == request.user:
            serializer = MyPageSerializer(my_page)
            return Response({'내 정보':serializer.data},status=200)
        return Response({"message": "다시 유저의 마이페이지는 볼 수 없습니다."}, status=400)
    
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

    




# 이메일 리셋 로직
class EmailResetRequestView(APIView):
    permission_classes = [IsAuthenticated]  # 로그인된 사용자만 가능

    def post(self, request):
        user = request.user
        new_email = request.data.get("new_email")

        # 중복 이메일 확인
        if User.objects.filter(email=new_email).exists():
            return Response({"message": "이미 사용 중인 이메일입니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 새로운 이메일에 대한 인증 토큰 생성
        user.verification_token = str(uuid.uuid4())
        user.new_email = new_email  # 새로운 이메일 필드 추가 필요
        user.save()

        # 이메일 전송
        send_verification_email_reset(user)  # 새로운 이메일로 인증 메일 전송
        return Response({"message": "이메일 변경 확인을 위한 이메일을 전송했습니다."}, status=status.HTTP_200_OK)


# 이메일 인증 메일이 날아올 경우
class EamilResetConfirmView(APIView):
    def get(self, request, token):
        # 예외처리 해서 만약 안될경우 서버 안터지게
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


# 내가 쓴 글
class MyJournalsListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, nickname):
        user = get_object_or_404(User, nickname=nickname)  # 닉네임으로 사용자 조회
        if user == request.user:  # 요청한 사용자가 본인인지 확인
            journals = user.my_journals.all()  # 사용자의 모든 저널 가져오기
            serializer = JournalSerializer(journals, many=True)
            return Response({'내가 쓴 글': serializer.data}, status=200)
        
        return Response({"message": "다시 시도"}, status=400)  # 본인이 아닐 경우
    
# 촬영지 저장 전체목록
class SavedLocationsListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, nickname):
        user = get_object_or_404(User, nickname=nickname)  # 닉네임으로 사용자 조회
        if user == request.user:  # 요청한 사용자가 본인인지 확인
            saved_locations = user.location_save.all()  # 사용자의 모든 저장된 촬영지 가져오기
            serializer = LocationSaveSerializer(saved_locations, many=True)
            return Response({'저장된 촬영지': serializer.data}, status=200)

        return Response({"message": "다시 시도"}, status=400)  # 본인이 아닐 경우
    
# 구독자 전체목록
class SubscribingsListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, nickname):
        user = get_object_or_404(User, nickname=nickname)  # 닉네임으로 사용자 조회
        if user == request.user:  # 요청한 사용자가 본인인지 확인
            subscribings = user.subscribings.all()  # 사용자의 모든 구독 가져오기
            serializer = SubUsernameSerializer(subscribings, many=True)
            return Response({'구독 중인 사용자들': serializer.data}, status=200)

        return Response({"message": "다시 시도"}, status=400)  # 본인이 아닐 경우
    
# 구독자 글
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
    

class MyCommunityListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, nickname):
        user = get_object_or_404(User, nickname=nickname)  # 닉네임으로 사용자 조회
        if user == request.user:  # 요청한 사용자가 본인인지 확인
            journals = user.communities_author.all()  # 사용자의 모든 커뮤니티 가져오기
            serializer = JournalSerializer(journals, many=True)
            return Response({'커뮤니티 내가 쓴 글': serializer.data}, status=200)
        
        return Response({"message": "다시 시도"}, status=400)  # 본인이 아닐 경우
