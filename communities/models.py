from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
import uuid


User = get_user_model()

class Community(models.Model): # 커뮤니티
    categories = [
        ( '정보', '정보' ), # 카테고리 선택
        ( '잡담', '잡담' ),
        ( '잡담', '홍보' )
    ]
    
    # id=models.IntegerField(primary_key=True)
    communityKey = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) # UUID 통한 고유번호필드
    category = models.CharField(max_length=2, choices=categories, default='정보')  # 카테고리 필드 추가
    title = models.CharField(max_length=40)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='communities_author',null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    unusables=models.ManyToManyField(User, related_name='community_unusable') #글신고    

    def __str__(self):
        return self.title
    

class CommunityImage(models.Model): # 커뮤니티 이미지
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='community_images')  # 저널과의 관계
    community_image = models.ImageField(upload_to="community_images/")

class Comment(models.Model): # 커뮤 댓글
    CommentKey = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) # UUID 통한 고유번호필드
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
    

class CommentLike(models.Model): # 커뮤 댓글좋아요
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_comment_likes')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='community_likes')
    like_type = models.CharField(max_length=10, choices=[('like', 'Like'), ('dislike', 'Dislike')])
    
    class Meta:
        unique_together = ('user', 'comment')


class CommunityLike(models.Model):  # 커뮤좋아요 모델
    communityLikeKey = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) # UUID 통한 고유번호필드
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='community_likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_communities')
    liked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('community', 'user')  # 한 유저가 하나의 커뮤니티에 좋아요 한 번만 가능


class CommunityDislike(models.Model):  # 커뮤싫어요 모델
    communityDislikeKey = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) # UUID 통한 고유번호필드
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='community_dislikes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='disliked_communities')
    disliked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('community', 'user')  # 한 유저가 하나의 커뮤니티에 싫어요 한 번만 가능

