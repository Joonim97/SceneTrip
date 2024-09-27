from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Comment, CommentLike
from .serializers import CommentSerializer, CommentLikeSerializer
from django.shortcuts import get_object_or_404

class CommentView(APIView):
    def get(self, request, community_id):
        comments = Comment.objects.filter(community_id=community_id, parent=None)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    def post(self, request, community_id):
        data = request.data.copy()
        data['community'] = community_id
        
        parent_id = data.get('parent', None)
        
        if parent_id:
            parent_comment = get_object_or_404(Comment, id=parent_id)
            data['parent'] = parent_comment.id
            
        
        serializer = CommentSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save(community_id=community_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, comment_id): 
        comment = Comment.objects.get(id=comment_id)
        serializer = CommentSerializer(comment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, comment_id):
        comment = Comment.objects.get(id=comment_id)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
    
class CommentLikeView(APIView):
    def post(self, request, comment_id, like_type):
        comment = get_object_or_404(Comment, id=comment_id)
        like_instance, created = CommentLike.objects.get_or_create(
            user=request.user,
            comment=comment,
            defaults={'like_type': like_type}
        )
        
        # 이미 좋아요/싫어요가 눌린 상태
        if not created:
            if like_instance.like_type == like_type:
                like_instance.delete()
                return Response({'message': f'{like_type.capitalize()} 취소'}, status=status.HTTP_200_OK)
            else:
                like_instance.like_type = like_type
                like_instance.save()
                return Response({'message': f'{like_type.capitalize()} 변경'}, status=status.HTTP_200_OK)
            
        # 좋아요/싫어요가 눌리지 않은 상태
        return Response({'message': f'{like_instance.capitalize()}!'}, status=status.HTTP_201_CREATED)