from rest_framework import serializers
from .models import Comment, CommentLike, Journal
from django.shortcuts import get_object_or_404

class RecursiveSerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.__class__(value, context=self.context)
        return serializer.data

class CommentSerializer(serializers.ModelSerializer): # 저널댓글 시리얼라이저
    replies = RecursiveSerializer(many=True, read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'journal', 'user', 'content', 'created_at', 'replies']
        read_only_fields = ['user', 'created_at', 'replies']
        
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)
    
class CommentLikeSerializer(serializers.ModelSerializer): # 저널 댓글좋아요 시리얼라이저
    class Meta:
        model = CommentLike
        fields = ['id', 'user', 'comment', 'like_type']
        read_only_fields = ['user']
        
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)



# class JournalImageSerializer(serializers.ModelSerializer): # 저널이미지
#     class Meta :
#         model= JournalImage
#         fields=['id','image']


class JournalSerializer(serializers.ModelSerializer) : # 저널
    # image = serializers.ImageField(use_url=True, required=False)
    likes_count= serializers.SerializerMethodField() # likes 카운트 계산
    author = serializers.CharField(source='author.nickname', read_only=True)

    class Meta :
        model=Journal
        fields= [  'id','title','author','created_at', 'likes_count' ]
        read_only_fields = ('id','author','created_at','updated_at','likes',
                            'likes_count')

    def get_likes_count(self, journal_id):
        return journal_id.likes.count()

class JournalDetailSerializer(JournalSerializer): # 저널디테일
    image = serializers.ImageField(use_url=True, required=False)
    
    likes_count= serializers.SerializerMethodField() # likes 카운트 계산
    author = serializers.CharField(source='author.nickname', read_only=True)

    class Meta :
        model=Journal
        fields= [  'id','title','author','created_at','updated_at','image','content','likes_count']
        read_only_fields = ('id','author','created_at','updated_at','likes',
                            'likes_count')

    def get_likes_count(self, journal_id):
        return journal_id.likes.count()
    # comments= CommentSerializer(many=True, read_only=True)
    # comments_count= serializers.IntegerField(source='comments.count', read_only=True)
