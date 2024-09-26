from rest_framework import serializers
from .models import User
from django.db import models

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
    
# 구독자 이름만 보이게 만듬
class SubUsernameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['nickname']

class MyPageSerializer(UserSerializer):
    subscribings = SubUsernameSerializer(many=True, read_only=True)  # 구독 중인 사용자들

    class Meta(UserSerializer.Meta):
        model = User
        # 마이페이지에서 필요한 필드만 선택
        fields = ['username', 'nickname', 'email', 'birth_date', 'gender', 'subscribings']
    