from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Comment, CommentLike, Community
from .serializers import CommentSerializer, CommentLikeSerializer, CommunitySerializer, CommunityDetailSerializer
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from django.conf import settings

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


class CommunityListAPIView(ListAPIView): # 전체목록조회, 커뮤니티작성
        queryset = Community.objects.all().order_by('-created_at') # 생성최신순 조회
        serializer_class = CommunitySerializer
        
        # def get(self, request): #전체목록 일단 주석처리리
        #         community = Community.objects.all()
        #         serializer = CommunitySerializer(community))
        #         return Response(community)
        
        def post(self, request): # 커뮤니티 작성      
                permission_classes = [IsAuthenticated] # 로그인권한

                serializer = CommunitySerializer(data=request.data)
                if serializer.is_valid(raise_exception=True):
                        serializer.save()
                        return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommunityDetailAPIView(APIView): # 커뮤니티 상세조회,수정,삭제
        permission_classes = [IsAuthenticated] # 로그인권한
        
        def get_object(self, pk):
                return get_object_or_404(Community, pk=pk)

        def get(self, request, pk): # 커뮤니티 상세조회
                community = self.get_object(pk)
                serializer = CommunityDetailSerializer(community)
                return Response(serializer.data)

        def put(self, request, pk): # 커뮤니티 수정
                community = self.get_object(pk)
                serializer = CommunityDetailSerializer(community, data=request.data, partial=True)
                if serializer.is_valid(raise_exception=True):
                        serializer.save()
                        return Response(serializer.data)
                
        def delete(self, request, pk): # 커뮤니티 삭제
                community = self.get_object(pk)
                community.delete()
                return Response({'삭제되었습니다'}, status=status.HTTP_204_NO_CONTENT)
        

# class JournalSearchSet(ListAPIView): # 커뮤니티 검색
#         queryset=Community.objects.all()
#         serializer_class=CommunitySerializer

#         filter_backends=[SearchFilter]
#         search_fields=[ 'title'] # 내용, 작성자로 찾기 추가해야 함



class CommunityUnusableAPIView(APIView): # 커뮤글 신고
    permission_classes = [IsAuthenticated]


    def post(self, request, pk):
        user = request.user
        community = get_object_or_404(Community, pk=pk)

        if user not in community.unusable.all():
            community.unusable.add(user) 
            
            return Response({"신고가 접수되었습니다"},  status=status.HTTP_200_OK)
        
        return Response({"이미 신고되었습니다"},  status=status.HTTP_200_OK)
