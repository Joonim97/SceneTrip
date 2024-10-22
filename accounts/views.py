from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import ListAPIView
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from communities.serializers import CommunitySerializer
from journals.serializers import JournalSerializer, JournalLikeSerializer
from locations.serializers import LocationSaveSerializer
from .serializers import PasswordCheckSerializer, SubUsernameSerializer, UserSerializer, MyPageSerializer
from .emails import send_verification_email, send_verification_email_reset, send_verification_password_reset
import uuid


User = get_user_model() # 필수 지우면 안됨

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

#########################################################


# 회원가입
class SignupAPIView(APIView):
    
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
            if existing_user:
                if not existing_user.is_active:
                    # 비활성화된 사용자라면 기존 사용자 삭제
                    existing_user.delete()
                    serializer = UserSerializer(data=request.data)

                    if serializer.is_valid():
                        # email = serializer.validated_data['email']
                        user = serializer.save()
                        user.set_password(request.data.get('password'))
                        user.verification_token = str(uuid.uuid4())
                        user.is_active = False
                        user.save()
                        
                        send_verification_email(user)  # 이메일 전송
                        return Response({"message": "이메일을 전송하였습니다. 이메일을 확인해주세요."}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"error": "회원가입에 실패했습니다. 이미 존재하는 사용자입니다."}, status=status.HTTP_400_BAD_REQUEST)

            else:
                user = serializer.save()
                user.set_password(request.data.get('password'))
                user.verification_token = str(uuid.uuid4())
                user.author_verification_token = str(uuid.uuid4()) # 토큰 생성
                user.is_active = False
                user.save()
                send_verification_email(user)
                messages.success(request, "이메일을 전송하였습니다! 이메일을 확인해주세요.")
                return redirect('accounts:signup')  # 메시지를 팝업으로 보여주기 위해 리디렉션
        except Exception as e:
            return Response({"error": "오류가 발생했습니다.", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# 이메일 인증 메일이 날아올 경우
class VerifyEmailAPIView(APIView):
    def get(self, request, token):
        try:
            user = get_object_or_404(User, verification_token=token)
            user.verification_token = ''
            user.grade = User.NORMAL
            user.is_active = True
            user.save()
            return HttpResponse('회원가입이 완료되었습니다.', status=status.HTTP_200_OK)
        except:
            return HttpResponse({'error':'회원가입이 정상적으로 처리되지 않으셨습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
     
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


class DeleteAPIView(APIView):  # 회원탈퇴
    permission_classes = [IsAuthenticated]

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

# 회원탈퇴
class DeleteAPIView(PermissionAPIView):
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


            

# 커스텀 페이지네이션
class CustomPagination(PageNumberPagination):
        page_size = 5
        page_size_query_param = 'page_size'
        max_page_size = 100
        
        
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
    # permission_classes = [IsAuthenticated]

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