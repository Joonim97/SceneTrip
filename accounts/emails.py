from django.core.mail import send_mail
from django.conf import settings

# 회원가입 정보가 맞으면 이 메세지 출력
def send_verification_email(user):
    subject = '이메일 인증을 완료해주세요'
    message = f'안녕하세요 {user.username}님, 아래 링크를 클릭하여 이메일 인증을 완료해주세요.\n\n http://127.0.0.1:8000/api/accounts/verify/{user.verification_token}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email]
    send_mail(subject, message, email_from, recipient_list)

    if user.grade == 'aj':
        new_journal_subject = '새 journalist 신청이 들어왔습니다. 관리자는 인증을 완료해주세요.'
        new_journal_message = f'새로운 {user.nickname}님의 journalist 신청이 들어왔습니다.'
        recipient_list = [settings.MANAGER_EMAIL]
        send_mail(new_journal_subject, new_journal_message, email_from, recipient_list)
        # print(f'관리자 이메일 전송됨: {settings.MANAGER_EMAIL}')


def send_verification_email_reset(user):
    subject = '이메일 변경을 위한 인증을 완료해주세요'
    message = f'안녕하세요 {user.username}님, 아래 링크를 클릭하여 이메일 변경을 위한 인증을 완료해주세요.\n\n http://127.0.0.1:8000/api/accounts/emailchange/verify/{user.verification_token}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.new_email]
    send_mail(subject, message, email_from, recipient_list)

def send_verification_password_reset(user):
    subject = '비밀번호 변경을 위한 이메일인증을 완료해주세요'
    message = f'안녕하세요 {user.username}님, 아래 링크를 클릭하여 비밀번호 변경을 위한 인증을 완료해주세요.\n\n http://127.0.0.1:8000/api/accounts/passwordchange/verify/{user.verification_token}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email]
    send_mail(subject, message, email_from, recipient_list)