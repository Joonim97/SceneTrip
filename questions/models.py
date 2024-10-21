from django.db import models
from django.contrib.auth import get_user_model
import uuid


User = get_user_model()

class Questions(models.Model): # 큐앤에이 모델
    questionKey = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, unique=False) # 고유번호필드
    title = models.CharField(max_length=40)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_questions') 

    def hit(self):
        self.hit_count += 1
        self.save()
        
    def __str__(self):
        return self.title
    
class QuestionsImage(models.Model): # 다중이미지용
    question = models.ForeignKey(Questions, on_delete=models.CASCADE, related_name='question_images')  # 저널과의 관계
    question_images = models.ImageField(upload_to="question_images/")


class Comments(models.Model): # 큐앤에이 댓글
    CommentKey = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True,unique=True) # UUID 통한 고유번호필드
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions_comments')
    question = models.ForeignKey('Questions', on_delete=models.CASCADE, related_name='questions_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image= models.ImageField(upload_to='questions_images', blank=True, null=True)
        
    class Meta:
        ordering = ['-created_at']
