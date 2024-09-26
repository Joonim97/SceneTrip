from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    journal = models.ForeignKey('Journal', on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    
    def __str__(self):
        return f'Comment by {self.user.username} on {self.post.title}'
    
    class Meta:
        orderig = [ '-created_at']
    