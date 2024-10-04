from rest_framework import serializers
from communities.serializers import CommunitySerializer
from journals.models import Journal
from journals.serializers import JournalSerializer
from locations.models import LocationSave
from locations.serializers import LocationSaveSerializer
from .models import User
from django.db import models
from django.core.paginator import Paginator
from rest_framework.pagination import PageNumberPagination
import re

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'nickname','email', 'user_id', 'birth_date', 'gender', 'grade']

        
    def validate(self, data):
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("사용 중인 이메일입니다.")
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError("사용 중인 username입니다.")
        
        # 닉네임 유효성 검사
        if len(data['nickname']) > 20 and len(data['nickname']) >= 3:
            raise serializers.ValidationError("닉네임은 3자 이상 20자 이하여야 합니다.")
        if User.objects.filter(username=data['nickname']).exists():
            raise serializers.ValidationError("사용 중인 닉네임 입니다.")
        
        # 비밀번호 유효성 검사
        if not re.search(r"[a-zA-Z]", data['password']):
            raise serializers.ValidationError("비밀번호는 하나 이상의 영문이 포함되어야 합니다.")
        if not re.search(r"\d", data['password']):
            raise serializers.ValidationError("비밀번호는 하나 이상의 숫자가 포함되어야 합니다.")
        if not re.search(r"[!@#$%^&*()]", data['password']):
            raise serializers.ValidationError("비밀번호는 하나 이상의 특수문자(!@#$%^&*())가 포함되어야 합니다.")
        
        # 아이디 유효성 검사
        if not re.search(r"[a-zA-Z]", data['user_id']):
            raise serializers.ValidationError("아이디는 하나 이상의 영문이 포함되어야 합니다.")
        if not re.search(r"\d", data['user_id']):
            raise serializers.ValidationError("아이디는 하나 이상의 숫자가 포함되어야 합니다.")
        if not re.search(r"[!@#$%^&*()]", data['user_id']):
            raise serializers.ValidationError("아이디는 하나 이상의 특수문자(!@#$%^&*())가 포함되어야 합니다.")
        return data


# 비밀번호 재설정
class PasswordCheckSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)

# 이메일 재설정
class EmailCheckSerializer(serializers.Serializer):
    new_email = serializers.EmailField(write_only=True)

# 구독자 이름만 보이게 만듬
class SubUsernameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['nickname']

# 마이페이지 
class MyPageSerializer(serializers.ModelSerializer):
    subscribings = serializers.SerializerMethodField()  # 구독 중인 사용자들
    my_journals = serializers.SerializerMethodField()  # 저널에 내가 쓴 글 역참조
    location_save = serializers.SerializerMethodField()  # 저장한 촬영지
    profile_image = serializers.ImageField() # 프로필 이미지
    communities_author = serializers.SerializerMethodField() # 커뮤니티에 내가 쓴 글

    class Meta:
        model = User
        fields = ['username', 'nickname', 'email', 'birth_date', 'gender', 'subscribings', 'my_journals', 'profile_image', 'location_save','communities_author']

    def get_subscribings(self, obj):
        # 구독 중인 사용자 중 최대 5명 반환
        subscriptions = obj.subscribings.all()[:5]  # 가장 최근 구독된 5명만 가져오기
        return SubUsernameSerializer(subscriptions, many=True).data

    def get_my_journals(self, obj):
        # 작성한 저널 중 최대 5개 반환
        journals = obj.my_journals.all()[:5]  # 가장 최근 저널 5개만 가져오기
        return JournalSerializer(journals, many=True).data

    def get_location_save(self, obj):
        # 저장한 촬영지 중 최대 5개 반환
        saved_locations = obj.location_save.all()[:5]  # 가장 최근 저장된 5개만 가져오기
        return LocationSaveSerializer(saved_locations, many=True).data
    
    def get_communities_author(self, obj):
        # 저장한 촬영지 중 최대 5개 반환
        communities_author = obj.communities_author.all()[:5]  # 가장 최근 커뮤니티 내가 쓴글 5개만 가져오기
        return CommunitySerializer(communities_author, many=True).data