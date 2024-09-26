from rest_framework import serializers
from .models import Journal


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
        fields=['title','content']


class JournalDetailSerializer(JournalSerializer):
    pass