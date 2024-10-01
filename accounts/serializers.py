from rest_framework import serializers
from .models import User
from django.db import models
from journals.serializers import JournalSerializer
from locations.serializers import LocationSaveSerializer

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

class MyPageSerializer(UserSerializer):
    subscribings = SubUsernameSerializer(many=True, read_only=True)  # 구독 중인 사용자들
    my_journals = JournalSerializer(many=True, read_only=True)  # 내가 쓴 글 역참조
    location_save = LocationSaveSerializer(many=True, read_only=True)

    class Meta(UserSerializer.Meta):
        model = User
        fields = ['username', 'nickname', 'email', 'birth_date', 'gender', 'subscribings', 'my_journals', 'profile_image', 'location_save']
