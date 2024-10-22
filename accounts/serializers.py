from rest_framework import serializers
from communities.serializers import CommunitySerializer
from journals.serializers import JournalSerializer
from locations.serializers import LocationSaveSerializer
from .models import User
import re

# 회원가입
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'birth_date', 'nickname','email', 'user_id', 'gender', 'grade']

    def validate(self, data):
        # 이메일 중복 체크
        if User.objects.filter(email=data['email'], is_active=True).exists():
            raise serializers.ValidationError("사용 중인 이메일입니다.")

        # username 중복 체크
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError("사용 중인 username입니다.")
        
        # 닉네임 유효성 검사 (3자 이상 20자 이하)
        if not (3 <= len(data['nickname']) <= 20):
            raise serializers.ValidationError("닉네임은 3자 이상 20자 이하여야 합니다.")
        if User.objects.filter(nickname=data['nickname']).exists():
            raise serializers.ValidationError("사용 중인 닉네임입니다.")
        
        # 비밀번호 유효성 검사
        if not re.search(r"[a-zA-Z]", data['password']):
            raise serializers.ValidationError("비밀번호는 하나 이상의 영문이 포함되어야 합니다.")
        if not re.search(r"\d", data['password']):
            raise serializers.ValidationError("비밀번호는 하나 이상의 숫자가 포함되어야 합니다.")
        if not re.search(r"[!@#$%^&*()]", data['password']):
            raise serializers.ValidationError("비밀번호는 하나 이상의 특수문자(!@#$%^&*())가 포함되어야 합니다.")
        if not (10 <= len(data['password']) <= 20):
            raise serializers.ValidationError("비밀번호는 10글자 이상 20글자 이하여야 합니다.")
        
        # 아이디 유효성 검사
        if User.objects.filter(user_id=data['user_id'], is_active=True).exists():
            raise serializers.ValidationError("사용 중인 이메일입니다.")
        if not re.search(r"[a-zA-Z]", data['user_id']):
            raise serializers.ValidationError("아이디는 하나 이상의 영문이 포함되어야 합니다.")
        if not re.search(r"\d", data['user_id']):
            raise serializers.ValidationError("아이디는 하나 이상의 숫자가 포함되어야 합니다.")
        if len(data['user_id']) == 0:
            raise serializers.ValidationError("아이디를 입력해주십시오.")
        if not (4 <= len(data['user_id']) <= 20):
            raise serializers.ValidationError("아이디는 4글자 이상 20글자 이하여야 합니다.")
        
        return data


# 비밀번호 관련
class PasswordCheckSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True)

    def validate_password(self, value):
        if not re.search(r"[a-zA-Z]", value):
            raise serializers.ValidationError("비밀번호는 하나 이상의 영문이 포함되어야 합니다.")
        if not re.search(r"\d", value):
            raise serializers.ValidationError("비밀번호는 하나 이상의 숫자가 포함되어야 합니다.")
        if not re.search(r"[!@#$%^&*()]", value):
            raise serializers.ValidationError("비밀번호는 하나 이상의 특수문자(!@#$%^&*())가 포함되어야 합니다.")
        if len(value) < 10 or len(value) > 20:
            raise serializers.ValidationError("비밀번호는 10글자 이상 20글자 이하여야 합니다.")
        if len(value) == 0:
            raise serializers.ValidationError("비밀번호를 입력해주십시오.")
        
        return value

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
    journal_likes = serializers.SerializerMethodField() # 내가 좋아요한 저널 글 목록 

    class Meta:
        model = User
        fields = ['uuid','username', 'nickname', 'email', 'birth_date', 'gender', 'subscribings',
                'my_journals', 'profile_image', 'location_save','communities_author', 'journal_likes']

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
        # 내가 쓴 커뮤니티 글
        communities_author = obj.communities_author.all()[:5]  # 가장 최근 커뮤니티 내가 쓴글 5개만 가져오기
        return CommunitySerializer(communities_author, many=True).data
    
    def get_journal_likes(self, obj):
        # 내가 좋아요한 저널 글
        journal_likes = obj.user_likes.all()[:5]  # 가장 최근 좋아요한 저널 글 5개만 가져오기
        journals = [like.journal for like in journal_likes]
        return JournalSerializer(journals, many=True).data