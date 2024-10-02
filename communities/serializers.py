from rest_framework import serializers
from .models import Comment, CommentLike, Community

class RecursiveSerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.__class__(value, context=self.context)
        return serializer.data

class CommentSerializer(serializers.ModelSerializer): # 커뮤 댓글 시리얼라이저
    replies = RecursiveSerializer(many=True, read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'community', 'user', 'content', 'created_at', 'replies']
        read_only_fields = ['user', 'created_at', 'replies']
        
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


class CommunitySerializer(serializers.ModelSerializer) : # 커뮤
    unusables_count= serializers.SerializerMethodField() # 신고수 카운트
    author = serializers.CharField(source='author.username', read_only=True)

    class Meta :
        model=Community
        fields=[ 'id','title','author','created_at', 'unusables_count' ]
        read_only_fields = ('id','author','created_at','updated_at','unusables','unusables_count')

    def get_unusables_count(self, community_id) :
        return community_id.unusables.count()



class CommunityDetailSerializer(CommunitySerializer): #커뮤 디테일
    image = serializers.ImageField(use_url=True, required=False)
    unusables_count= serializers.SerializerMethodField() # 신고수 카운트
    author = serializers.CharField(source='author.username', read_only=True)
    
    class Meta :
        model=Community
        fields=[ 'id','title','author','created_at','updated_at','image','content', 'unusables_count' ]
        read_only_fields = ('id','author','created_at','updated_at','unusables','unusables_count')

    def get_unusables_count(self, community_id) :
        return community_id.unusables.count()
    
    # 댓글 보이게 해야 돼 ⬇️
    # comments= CommentSerializer(many=True, read_only=True)
    # comments_count = serializers.IntegerField(source='comments.count', read_only=True)