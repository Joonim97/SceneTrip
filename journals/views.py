from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Comment
from .serializers import CommentSerializer
from django.shortcuts import get_object_or_404

class CommentView(APIView):
    def get(self, request, journal_id):
        comments = Comment.objects.filter(journal_id=journal_id, parent=None)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    def post(self, request, journal_id):
        data = request.data.copy()
        data['journal'] = journal_id
        
        parent_id = data.get('parent', None)
        
        if parent_id:
            parent_comment = get_object_or_404(Comment, id=parent_id)
            data['parent'] = parent_comment.id
            
        
        serializer = CommentSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save(journal_id=journal_id)
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