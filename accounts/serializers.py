from rest_framework import serializers
from journals.models import Journal
from journals.serializers import JournalSerializer
from locations.models import LocationSave
from locations.serializers import LocationSaveSerializer
from .models import User
from django.db import models
from django.core.paginator import Paginator
from rest_framework.pagination import PageNumberPagination

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'nickname','email', 'user_id', 'birth_date', 'gender']

        
    def validate(self, data):
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("사용 중인 이메일입니다.")
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError("사용 중인 username입니다.")
        return data
    
# 비밀번호 재설정
class PasswordCheckSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)

class EmailCheckSerializer(serializers.Serializer):
    new_email = serializers.EmailField(write_only=True)

# 구독자 이름만 보이게 만듬
class SubUsernameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['nickname']


class MyPageSerializer(serializers.ModelSerializer):
    subscribings = serializers.SerializerMethodField()  # 구독 중인 사용자들
    my_journals = serializers.SerializerMethodField()  # 내가 쓴 글 역참조
    location_save = serializers.SerializerMethodField()  # 저장한 촬영지

    profile_image = serializers.ImageField()

    class Meta:
        model = User
        fields = ['username', 'nickname', 'email', 'birth_date', 'gender', 'subscribings', 'my_journals', 'profile_image', 'location_save']

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