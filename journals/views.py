from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Comment, CommentLike, Journal
from .serializers import (
    CommentSerializer, CommentLikeSerializer, JournalSerializer,
    JournalDetailSerializer )
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import ListAPIView
from django.conf import settings
from django.db.models import Q
from django.utils.dateparse import parse_datetime

class CommentView(APIView): # 저널 댓글
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
    
    
    
class CommentLikeView(APIView): # 저널 댓글좋아요
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


class JournalListAPIView(ListAPIView): # 저널 전체목록조회, 저널작성, 저널검색
        queryset = Journal.objects.all().order_by('-created_at') # 생성최신순
        serializer_class = JournalSerializer
        
        def get_queryset(self): # 저널전체목록조회 & 저널검색 | method는 get | 검색어 아무것도 안 넣으면 전체목록 나옴옴
            permission_classes = [AllowAny]
            queryset = Journal.objects.all().order_by('-created_at')
            
            search_query= self.request.query_params.get('search', None) # 통합검색 | 'search'라는 파라미터로 검색어를 받음
            title_query= self.request.query_params.get('title',None) # 제목 검색
            # content_query= self.request.query_params.get('content',None) # 내용 검색
            # author_query= self.request.query_params.get('author',None) # 작성자 검색
            start_date= self.request.query_params.get('start_date', None) # 기간시작일
            end_date= self.request.query_params.get('end_date', None) # 기간종료일
            # 기간입력 예: ?start_date=2023-01-01T00:00:00Z&end_date=2023-12-31T23:59:59Z
            
            if search_query:
                serializer_class=JournalDetailSerializer()
                queryset=queryset.filter(
                    Q(title__icontains=search_query) | Q(content__icontains=search_query) | Q(author__icontains=search_query)
                )
            if title_query :
                queryset=queryset.filter( Q(title__icontains=title_query) )
            # if content_query :
            #     queryset=queryset.filter( Q(content__icontains=title_query) )
            # if author_query :
            #     queryset=queryset.filter( Q(author__icontains=title_query) )
            if start_date or end_date:
                start_date_parsed = parse_datetime(start_date)
                end_date_parsed = parse_datetime(end_date)
                if start_date_parsed or end_date_parsed:
                    queryset = queryset.filter(created_at__range=(start_date_parsed, end_date_parsed))

            return queryset
            
        def post(self, request): #  작성 
                permission_classes = [IsAuthenticated] # 로그인권한
        
                serializer = JournalDetailSerializer(data=request.data)
                if serializer.is_valid(raise_exception=True):
                        serializer.save(author=request.user)
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
                permission_classes = [IsAuthenticated] # 로그인권한

                journal = self.get_object(pk)
                serializer = JournalDetailSerializer(journal, data=request.data, partial=True)
                if serializer.is_valid(raise_exception=True):
                        serializer.save()
                        return Response(serializer.data)
                
        def delete(self, request, pk): # 저널 삭제
                permission_classes = [IsAuthenticated] # 로그인권한

                journal = self.get_object(pk)
                journal.delete()
                return Response({'삭제되었습니다'}, status=status.HTTP_204_NO_CONTENT)
        

class JournalSearchSet(ListAPIView): # 저널 검색
        queryset=Journal.objects.all()
        serializer_class=JournalSerializer

        filter_backends=[SearchFilter]
        search_fields=[ 'title'] # 내용, 작성자로 찾기 추가해야 함


class JournalLikeAPIView(APIView): # 저널 좋아요/좋아요취소 
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        journal = get_object_or_404(Journal, pk=pk)
    
        if request.user in journal.likes.all():
            journal.likes.remove(request.user) # 좋아요 이미 되어있으면
            return Response({"좋아요 취소"},   status=status.HTTP_200_OK )
        else:
            journal.likes.add(request.user) # 좋아요 되어있지 않으면
            return Response({'좋아요 +1'},  status=status.HTTP_200_OK)