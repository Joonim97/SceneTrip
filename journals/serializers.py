from rest_framework import serializers
from .models import Comment, CommentLike, Journal

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
        read_only_fields = ['user', 'created_at', 'like_count', 'dislike_count', 'replies']
        
    def get_like_count(self, comment):
        return CommentLike.objects.filter(comment=comment, like_type='like').count()
    
    def get_dislike_count(self, comment):
        return CommentLike.objects.filter(comment=comment, like_type='dislike').count()
        
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)
    
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
    image = serializers.ImageField(use_url=True, required=False)
    likes= Journal.likes
    likes_count= serializers.IntegerField(source='Journal.likes.count()', read_only=True)
    
    class Meta :
        model=Journal
        fields='__all__'
        read_only_fields = ('id','created_at','updated_at','likes','author','likes_count')


class JournalDetailSerializer(JournalSerializer):
    comments= CommentSerializer(many=True, read_only=True)
    comments_count= serializers.IntegerField(source='comments.count', read_only=True)

