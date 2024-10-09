from django.db import models
from django.contrib.auth import get_user_model
import uuid


User = get_user_model()

class Journal(models.Model): # 저널
    # id=models.IntegerField(primary_key=True) # 주석 안 하면 생성했을 때 id:null로 뜸
    journalKey = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) # UUID 통한 고유번호필드
    title = models.CharField(max_length=40)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_journals', null=True) 
    hit_count = models.IntegerField(default=0)

    def hit(self):
        self.hit_count += 1
        self.save()

    def __str__(self):
        return self.title


class JournalImage(models.Model): # 다중이미지용
    journal = models.ForeignKey(Journal, on_delete=models.CASCADE, related_name='journal_images')  # 저널과의 관계
    journal_image = models.ImageField(upload_to="journal_images/")


class JournalLike(models.Model):
    journal = models.ForeignKey(Journal, on_delete=models.CASCADE, related_name='journal_likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_likes')
    liked_at = models.DateTimeField(auto_now_add=True)
    journalLikeKey = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) # UUID 통한 고유번호필드
    
    class Meta:
        unique_together = ('journal', 'user') # 한 저널에 좋아요 여러번 누르지 못하게 함


class Comment(models.Model): # 저널댓글
    CommentKey = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) # UUID 통한 고유번호필드
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='journal_comments')
    journal = models.ForeignKey('Journal', on_delete=models.CASCADE, related_name='journal_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='journal_replies')
    
    def __str__(self):
        return f'Comment by {self.user.username} on {self.journal.title}'
    
    class Meta:
        ordering = ['-created_at']


class CommentLike(models.Model): # 저널 댓글좋아요
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='journal_comment_likes')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='journal_comment_likes')
    like_type = models.CharField(max_length=10, choices=[('like', 'Like'), ('dislike', 'Dislike')])
    
    class Meta:
        unique_together = ('user', 'comment')