from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import UserSerializer
from .emails import send_verification_email
import uuid
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

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
            return HttpResponse({'message':'회원가입이 완료되었습니다.'}, status=status.HTTP_200_OK)
        except:
            return HttpResponse({'error':'회원가입이 정상적으로 처리되지 않으셨습니다.'}, status=status.HTTP_400_BAD_REQUEST)