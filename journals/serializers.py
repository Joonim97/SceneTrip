from rest_framework import serializers
from .models import Comment, CommentLike, Journal

class RecursiveSerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.__class__(value, context=self.context)
        return serializer.data

class CommentSerializer(serializers.ModelSerializer):
    replies = RecursiveSerializer(many=True, read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'journal', 'user', 'content', 'created_at', 'replies']
        read_only_fields = ['user', 'created_at', 'replies']
        
    def create(self, validated_data):
        request = self.contex.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)
    
class CommentLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentLike
        fields = ['id', 'user', 'comment', 'like_type']
        read_only-fields = ['user']
        
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)

# class CommentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Comment
#         fields = '__all__'
#         read_only_fields = ('article',)

#     def to_representation(self, instance):
#         ret = super().to_representation(instance)
#         ret.pop('article')
#         return ret

class JournalSerializer(serializers.ModelSerializer) :
    # author = serializers.ReadOnlyField(source='author.username')
    # image = serializers.ImageField(use_url=True, required=False)

    class Meta :
        model=Journal
        # fields=['id','title','content','created_at','updated_at']
        fields='__all__'
        read_only_fields = ('id','created_at','updated_at')



class JournalDetailSerializer(JournalSerializer):
    True # 댓글 보이게 추가해야 함