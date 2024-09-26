from rest_framework import serializers
from .models import User

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
    