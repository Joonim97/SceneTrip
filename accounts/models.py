import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
# 커스텀 유저 
class User(AbstractUser):
    # 성, 이름은 username 으로 대체
    # first_name = models.CharField(max_length=150, blank=False) # 성
    # last_name = models.CharField(max_length=150, blank=False) # 이름
    user_id = models.CharField(max_length=150, unique=True) # 아이디
    email = models.EmailField(unique=True, blank=False) # 이메일
    birth_date = models.DateField(blank=False) # 생년월일
    gender = models.CharField(max_length=10, null=True, blank=True) # 성별
    verification_token = models.CharField(max_length=255, blank=True, null=True) # 인증토큰
    nickname = models.CharField(max_length=20, unique=True)
    subscribings = models.ManyToManyField('self', symmetrical=False, related_name='subscribes') # 구독
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  # UUID 필드, 고유번호 필드 추가
    new_email = models.EmailField(null=True, blank=True) # 새 이메일
    new_password = models.CharField(max_length=20, null=True, blank=True) # 새 비밀번호
    
    # 저널리스트(AUTHOR) 이나 일반(NOMAL) 선택 필드
    AUTHOR= 'author'
    NOMAL = 'normal'
    GRADE = [
        (AUTHOR, 'author'),
        (NOMAL, 'normal'),
    ]
    grade = models.CharField(max_length=6, choices=GRADE, default=0)
    


    USERNAME_FIELD = 'user_id'  # 사용자 이름으로 사용할 필드
    REQUIRED_FIELDS = ['email']  # 필수로 입력해야 할 필드
