from rest_framework import serializers
from .models import Questions, Comments, QuestionsImage


class CommentSerializer(serializers.ModelSerializer): # 큐앤에이 댓글 시리얼라이저
    
    class Meta:
        model = Comments
        fields ='__all__'
        read_only_fields = [ 'user', 'created_at', 'replies']
        
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)
    

class QuestionImageSerializer(serializers.ModelSerializer):  # 저널이미지 시리얼라이저
    class Meta:
        model = QuestionsImage
        fields = ["id", "question_images"]  # 이미지 필드만 포함

class QuestionSerializer(serializers.ModelSerializer) : # 큐앤에이 시리얼라이저
    author = serializers.CharField(source='author.nickname', read_only=True)
    comments_count= serializers.SerializerMethodField() # 댓글 수
    images = QuestionImageSerializer(
    many=True, read_only=True
    )

    class Meta :
        model=Questions
        fields=['questionKey','title','author','content','images','created_at','comments_count','hit_count']
        read_only_fields = ('questionKey','author','created_at','updated_at', 'comments_count', 'hit_count')

    def get_comments_count(self, question_id): # 댓글수
        return question_id.questions_comments.count()



class QuestionDetailSerializer(QuestionSerializer): # 큐앤에이 디테일 시리얼라이저
    comments= CommentSerializer(many=True, read_only=True, source='questions_comments')

    class Meta(QuestionSerializer.Meta) :
        fields= QuestionSerializer.Meta.fields + ['comments']

        read_only_fields = ('questionKey','author','created_at','updated_at',
                            'comments_count','comments',)
        
