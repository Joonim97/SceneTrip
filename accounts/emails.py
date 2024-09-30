from django.core.mail import send_mail
from django.conf import settings

# 회원가입 정보가 맞으면 이 메세지 출력
def send_verification_email(user):
    subject = '이메일 인증을 완료해주세요'
    message = f'안녕하세요 {user.username}님, 아래 링크를 클릭하여 이메일 인증을 완료해주세요.\n\n http://127.0.0.1:8000/api/accounts/verify/{user.verification_token}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email]
    send_mail(subject, message, email_from, recipient_list)