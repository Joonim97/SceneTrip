from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.contrib.auth.decorators import login_required
from django.db import models
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import ListAPIView
from .models import Comment, CommentLike, Journal
from .serializers import CommentSerializer, CommentLikeSerializer, JournalSerializer,JournalDetailSerializer


from django.conf import settings

class CommentView(APIView):
    def get(self, request, journal_id):
        comments = Comment.objects.filter(journal_id=journal_id)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def post(self, request, journal_id, parent_id=None):
        data = request.data.copy()
        journal = get_object_or_404(Journal, id=journal_id)
        data['journal'] = journal_id
        
        if parent_id:
            parent_comment = get_object_or_404(Comment, id=parent_id)
            data['parent'] = parent_comment.id
            
        
        serializer = CommentSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save(journal=journal)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, comment_id): 
        comment = Comment.objects.get(id=comment_id)
        
        if comment.user != request.user:
            raise PermissionDenied("수정 권한이 없습니다.")
        
        serializer = CommentSerializer(comment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, comment_id):
        comment = Comment.objects.get(id=comment_id)
        
        if comment.user != request.user:
            raise PermissionDenied("삭제 권한이 없습니다.")
        
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class DislikedCommentsView(APIView):
    def get(self, request, min_dislikes):
        # 일정 수 이상의 싫어요를 받은 댓글을 필터링
        disliked_comments = Comment.objects.filter(
            id__in=CommentLike.objects.filter(like_type='dislike')
                                      .values('comment')
                                      .annotate(dislike_count=models.Count('comment'))
                                      .filter(dislike_count__gte=min_dislikes)
                                      .values('comment')
        )

        # 필터링된 댓글을 직렬화
        serializer = CommentSerializer(disliked_comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    
class CommentLikeView(APIView):
    permission_classes = [IsAuthenticated]
    
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
                message = f'{like_type.capitalize()} 취소'
            else:
                like_instance.like_type = like_type
                like_instance.save()
                message = f'{like_type.capitalize()} 변경됨'
        else:
            message = f'{like_type.capitalize()}!'
        
        # 싫어요가 3개 이상일 경우 댓글 삭제
        dislike_count = CommentLike.objects.filter(comment=comment, like_type='dislike').count()
        if dislike_count >= 3:
            comment.delete()
            return Response({'message': '댓글이 삭제되었습니다.'}, status=status.HTTP_201_CREATED)
        
        return Response({'message': message}, status=status.HTTP_200_OK)


class JournalListAPIView(ListAPIView): # 전체목록조회, 저널작성
        queryset = Journal.objects.all().order_by('-created_at') # 생성최신순
        serializer_class = JournalSerializer
        
        # def get(self, request): #전체목록 일단 주석처리리
        #         journal = Journal.objects.all()
        #         serializer = JournalSerializer(journal)
        #         return Response(journal)
        
        def post(self, request): #  작성               
                serializer = JournalSerializer(data=request.data)
                if serializer.is_valid(raise_exception=True):
                        serializer.save()
                        return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST )


class JournalDetailAPIView(APIView): # 저널 상세조회,수정,삭제
        def get_object(self, pk):
                return get_object_or_404(Journal, pk=pk)

        def get(self, request, pk): # 저널 상세조회
                journal = self.get_object(pk)
                serializer = JournalDetailSerializer(journal)
                return Response(serializer.data)

        def put(self, request, pk): # 저널 수정
                journal = self.get_object(pk)
                serializer = JournalDetailSerializer(journal, data=request.data, partial=True)
                if serializer.is_valid(raise_exception=True):
                        serializer.save()
                        return Response(serializer.data)
                
        def delete(self, request, pk): # 저널 삭제
                journal = self.get_object(pk)
                journal.delete()
                return Response({'삭제되었습니다'}, status=status.HTTP_204_NO_CONTENT)
        

class JournalSearchSet(ListAPIView): # 저널 검색
        queryset=Journal.objects.all()
        serializer_class=JournalSerializer

        filter_backends=[SearchFilter]
        search_fields=[ 'title'] # 내용, 작성자로 찾기 추가해야 함


class JournalLikeAPIView(APIView): # 저널 좋아요/좋취 
    permission_classes = [IsAuthenticated]
    def post(self, request, pk):
        journal = get_object_or_404(Journal, pk=pk)

        if request.user in journal.likes.all():
            journal.likes.remove(request.user) # 좋아요 이미 되어있으면
            return Response("좋아요 취소", status=status.HTTP_200_OK)
        else:
            journal.likes.add(request.user) # 좋아요 되어있지 않으면
            return Response("좋아요 +1",  status=status.HTTP_200_OK)