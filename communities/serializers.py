from rest_framework import serializers
from .models import Comment, CommentLike, Community
from django.shortcuts import get_object_or_404


class RecursiveSerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.__class__(value, context=self.context)
        return serializer.data

class CommentSerializer(serializers.ModelSerializer): # 커뮤 댓글 시리얼라이저
    like_count = serializers.SerializerMethodField()
    dislike_count = serializers.SerializerMethodField()
    replies = RecursiveSerializer(many=True, read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'community', 'user', 'content', 'parent', 'created_at', 'like_count', 'dislike_count', 'replies']
        read_only_fields = ['community', 'user', 'created_at', 'like_count', 'dislike_count', 'replies']
        
    def get_like_count(self, comment):
        return CommentLike.objects.filter(comment=comment, like_type='like').count()
    
    def get_dislike_count(self, comment):
        return CommentLike.objects.filter(comment=comment, like_type='dislike').count()
        
    def create(self, validated_data):
        request = self.contex.get('request')
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


class CommunitySerializer(serializers.ModelSerializer) : # 커뮤니티
    unusables_count= serializers.SerializerMethodField() # 신고수 카운트
    author = serializers.CharField(source='author.nickname', read_only=True)
    comments_count= serializers.SerializerMethodField() # 댓글 수

    class Meta :
        model=Community
        fields=[ 'id','title','author','created_at', 'comments_count','unusables_count' ]
        read_only_fields = ('id','author','created_at','updated_at'
                            'unusables_count','comments_count')

    def get_unusables_count(self, community_id) :
        return community_id.unusables.count()
    
    def get_comments_count(self, community_id):
        return community_id.community_comments.count()



class CommunityDetailSerializer(CommunitySerializer): #커뮤니티 디테일
    image = serializers.ImageField(use_url=True, required=False)
    unusables_count= serializers.SerializerMethodField() # 신고수 카운트
    author = serializers.CharField(source='author.nickname', read_only=True)
    comments= CommentSerializer(many=True, read_only=True, source='community_comments')
    comments_count= serializers.SerializerMethodField() # 댓글 수

    class Meta :
        model=Community
        fields=[ 'id','title','author','created_at','updated_at',
                'image','content', 'unusables_count','comments_count','comments' ]
        read_only_fields = ('id','author','created_at','updated_at',
                            'unusables','unusables_count','comments_count','comments')

    def get_unusables_count(self, community_id) :
        return community_id.unusables.count()
    
    def get_comments_count(self, community_id):
        return community_id.community_comments.count()