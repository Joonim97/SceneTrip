from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import UserSerializer, MyPageSerializer
from .emails import send_verification_email
import uuid
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import ListAPIView

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
        

# 로그인
class SigninAPIView(APIView):
    permission_classes = [AllowAny] # 로그인 인증 미진행 

    def post(self, request):
        # 유저 정보에 있는 user_id, password 가져오기
        user_id = request.data.get("user_id")
        password = request.data.get("password")
        try:
            user = User.objects.get(user_id=user_id) # 가져온 user_id 와 맞는 지 확인 아니면 예외처리
            if user.check_password(password):  # 해쉬 비밀번호 확인 후 맞으면 로그인 처리
                serializer = UserSerializer(user)
                res_data = serializer.data

                refresh = RefreshToken.for_user(user)
                refresh_token = str(refresh)
                access_token = str(refresh.access_token)

                res_data["access_token"] = access_token
                res_data["refresh_token"] = refresh_token

                return Response({"message": f"로그인 성공하셨습니다. 환영합니다 {user_id} 님", "data" : res_data}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "비밀번호가 올바르지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"message": "해당 user_id에 대한 계정을 찾을 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)


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
    

class Mypage(ListAPIView): # 마이 페이지
    permission_classes = [IsAuthenticated]

    # def get_queryset(self): # 내가 쓴 글 역참조 로직
    #     return User.objects.none()

    def get(self, request, nickname):
        my_page = get_object_or_404(User, nickname=nickname)
        if my_page == request.user:
            serializer = MyPageSerializer(my_page)
            return Response({'내 정보':serializer.data},status=200)
        return Response({"message": "다시 시도"}, status=400)

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
            