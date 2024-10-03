from rest_framework import serializers
from .models import Comment, CommentLike, Journal, JournalImage, User

class RecursiveSerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.__class__(value, context=self.context)
        return serializer.data

class CommentSerializer(serializers.ModelSerializer):
    like_count = serializers.SerializerMethodField()
    dislike_count = serializers.SerializerMethodField()
    replies = RecursiveSerializer(many=True, read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'journal', 'user', 'content', 'parent', 'created_at', 'like_count', 'dislike_count', 'replies']
        read_only_fields = ['journal', 'user', 'created_at', 'like_count', 'dislike_count', 'replies']
        
    def get_like_count(self, comment):
        return CommentLike.objects.filter(comment=comment, like_type='like').count()
    
    def get_dislike_count(self, comment):
        return CommentLike.objects.filter(comment=comment, like_type='dislike').count()
        
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # journal 필드는 수정할 필요가 없으므로 validated_data에서 제거
        validated_data.pop('journal', None)
        return super().update(instance, validated_data)
    
class CommentLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentLike
        fields = ['id', 'user', 'comment', 'like_type']
        read_only_fields = ['user']
        
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)


class JournalSerializer(serializers.ModelSerializer) :
    # author = serializers.ReadOnlyField(source='author.username')
    likes= Journal.likes
    likes_count= serializers.IntegerField(source='Journal.likes.count()', read_only=True)
    user_nickname = serializers.ReadOnlyField(source='user.nickname')  # 사용자 닉네임 읽기 전용 필드
    journal_images = JournalImageSerializer(many=True, read_only=True)  # 다중 이미지 시리얼라이저
    
    class Meta :
        model=Journal
        fields='__all__'
        read_only_fields = ('id','created_at','updated_at','likes','author','likes_count', 'hit_count')
        
        
class JournalImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalImage
        fields = ['id', 'image']  # 이미지 필드만 포함


class JournalDetailSerializer(JournalSerializer):
    comments= CommentSerializer(many=True, read_only=True)
    comments_count= serializers.IntegerField(source='comments.count', read_only=True)

