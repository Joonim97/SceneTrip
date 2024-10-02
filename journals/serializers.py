from rest_framework import serializers
from .models import Comment, CommentLike, Journal, JournalImage, User

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


# class CommentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Comment
#         fields = '__all__'
#         read_only_fields = ('article',)

#     def to_representation(self, instance):
#         ret = super().to_representation(instance)
#         ret.pop('article')
#         return ret

class JournalImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalImage
        fields = ['id', 'image']  # 이미지 필드만 포함

class JournalSerializer(serializers.ModelSerializer):
    user_nickname = serializers.ReadOnlyField(source='user.nickname')  # 사용자 닉네임 읽기 전용 필드
    journal_images = JournalImageSerializer(many=True, read_only=True)  # 다중 이미지 시리얼라이저

    class Meta:
        model = Journal
        fields = '__all__'  # 모든 필드 포함
        read_only_fields = ('user_nickname', 'user', 'created_at', 'updated_at', 'hit_count')  # 읽기 전용 필드




class JournalDetailSerializer(JournalSerializer):
    True # 댓글 보이게 추가해야 함
