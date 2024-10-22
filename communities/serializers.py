from rest_framework import serializers
from .models import Comment, CommentLike, Community, CommunityLike, CommunityDislike, CommunityImage
from django.shortcuts import get_object_or_404

class RecursiveSerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.__class__(value, context=self.context)
        return serializer.data

class CommentSerializer(serializers.ModelSerializer): # 커뮤 댓글 시리얼라이저
    like_count = serializers.SerializerMethodField()
    dislike_count = serializers.SerializerMethodField()
    replies = RecursiveSerializer(many=True, read_only=True)
    user_nickname = serializers.CharField(source='user.nickname', read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'community', 'user', 'content', 'parent', 'created_at', 'like_count', 'dislike_count', 'replies', 'user_nickname']
        read_only_fields = ['community', 'user', 'created_at', 'like_count', 'dislike_count', 'replies']
        
    def get_like_count(self, comment):
        return CommentLike.objects.filter(comment=comment, like_type='like').count()
    
    def get_dislike_count(self, comment):
        return CommentLike.objects.filter(comment=comment, like_type='dislike').count()
        
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)
    
class CommentLikeSerializer(serializers.ModelSerializer): # 커뮤 댓글좋아요 시리얼라이저
    class Meta:
        model = CommentLike
        fields = ['id', 'user', 'comment', 'like_type']
        read_only_fields = ['user']
        
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)

class CommunityLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityLike
        fields = ['communityLikeKey', 'user', 'liked_at']

class CommunityDislikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityDislike
        fields = ['communityDislikeKey', 'user', 'disliked_at']

class CommunityImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityImage
        fields = ['community_image']  # 이미지 필드만 포함

class CommunitySerializer(serializers.ModelSerializer) : # 커뮤니티
    unusables_count= serializers.SerializerMethodField() # 신고수 카운트
    author = serializers.CharField(source='author.nickname', read_only=True)
    comments_count= serializers.SerializerMethodField() # 댓글 수

    likes_count= serializers.SerializerMethodField() # 좋아요수
    dislikes_count= serializers.SerializerMethodField() # 싫어요수
    likes = CommunityLikeSerializer(source='community_likes', many=True, read_only=True)
    dislikes = CommunityDislikeSerializer(source='community_dislikes', many=True, read_only=True)
    community_images = CommunityImageSerializer(many=True, read_only=True)

    class Meta :
        model=Community
        fields=['communityKey','category','title','content','community_images','author','created_at', 'comments_count','unusables_count' ,'likes_count','dislikes_count','likes','dislikes']
        read_only_fields = ('communityKey','author','created_at','updated_at',
                            'unusables_count','comments_count','likes_count','dislikes_count','likes','dislikes')

    def get_unusables_count(self, communityKey) : # 신고수
        return communityKey.unusables.count()
    
    def get_comments_count(self, communityKey): # 댓글수
        return communityKey.community_comments.count()
    
    def get_likes_count(self, communityKey): # 좋아요수
        return communityKey.community_likes.count()
    
    def get_dislikes_count(self, communityKey): # 싫어요수
        return communityKey.community_dislikes.count()


class CommunityDetailSerializer(CommunitySerializer): #커뮤니티 디테일
    comments= CommentSerializer(many=True, read_only=True, source='community_comments')
    comments_count= serializers.SerializerMethodField() # 댓글 수
    community_images = CommunityImageSerializer(many=True, read_only=True)

    class Meta(CommunitySerializer.Meta) :

        fields= CommunitySerializer.Meta.fields + ['comments_count','comments' ]

        read_only_fields = ('communityKey','author','created_at','updated_at',
                            'unusables','unusables_count','comments_count','comments','likes_count','dislikes_count','likes','dislikes')
  
    def get_comments_count(self, communityKey): # 댓글수
        return communityKey.community_comments.count()