from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_comments')
    community = models.ForeignKey('Community', on_delete=models.CASCADE, related_name='community_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='community_replies')
    
    def __str__(self):
        return f'Comment by {self.user.username} on {self.community.title}'
    
    class Meta:
        ordering = [ '-created_at']
    

class CommentLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_comment_likes')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='community_likes')
    like_type = models.CharField(max_length=10, choices=[('like', 'Like'), ('dislike', 'Dislike')])
    
    class Meta:
        unique_together = ('user', 'comment')


class Community(models.Model):
    # id=models.IntegerField(primary_key=True)
    title = models.CharField(max_length=40)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(null=True, blank=True)
    unusables=models.ManyToManyField(User, related_name='community_unusable') #글신고
    # author = models.ForeignKey(User, on_delete=models.CASCADE)

