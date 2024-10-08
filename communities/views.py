from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Comment, CommentLike, CommunityLike, CommunityDislike, Community, CommunityImage
from .serializers import CommentSerializer, CommunitySerializer, CommunityDetailSerializer

class CommentView(APIView): # 커뮤 댓글
    def get(self, request, community_id):
        comments = Comment.objects.filter(community_id=community_id)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def post(self, request, community_id, parent_id=None):
        data = request.data.copy()
        community = get_object_or_404(Community, id=community_id)
        data['community'] = community_id
        
        if parent_id:
            parent_comment = get_object_or_404(Comment, id=parent_id)
            data['parent'] = parent_comment.id
            
        
        serializer = CommentSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save(community=community)
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
        return Response({"댓글이 삭제되었습니다."},status=status.HTTP_204_NO_CONTENT)
    
    
class CommentLikeView(APIView): # 커뮤 댓글좋아요
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
        
        # 싫어요가 100개 이상일 경우 댓글 삭제
        dislike_count = CommentLike.objects.filter(comment=comment, like_type='dislike').count()
        if dislike_count >= 100:
            comment.delete()
            return Response({'message': '댓글이 삭제되었습니다.'}, status=status.HTTP_201_CREATED)
        
        return Response({'message': message}, status=status.HTTP_200_OK)

class CommunityListAPIView(ListAPIView): # 커뮤 전체목록조회, 커뮤니티작성
        queryset = Community.objects.all().order_by('-created_at') # 전체조회
        serializer_class = CommunitySerializer

        
        def post(self, request): # 작성
            permission_classes = [IsAuthenticated] # 로그인권한
            serializer = CommunityDetailSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):

                community = serializer.save(author=request.user)  # 현재 로그인한 유저 저장
                community_images = request.FILES.getlist('images')
                for community_image in community_images:
                    CommunityImage.objects.create(community=community, community_image=community_image)

                return Response(serializer.data, status=201)
            else:
                return Response(serializer.errors, status=400)


class CommunityDetailAPIView(APIView): # 커뮤니티 상세조회,수정,삭제
        
        def get_object(self, pk):
                return get_object_or_404(Community, pk=pk)

        def get(self, request, pk): # 커뮤니티 상세조회
                community = self.get_object(pk)

                if community.unusables.count() >= 30 : # 3회 이상 신고된 글 접근 불가
                    return Response({ "detail": "신고가 누적된 글은 볼 수 없습니다." }, status=status.HTTP_404_NOT_FOUND )

                serializer = CommunityDetailSerializer(community)
                return Response(serializer.data)

        def put(self, request, pk): # 커뮤니티 수정
                permission_classes = [IsAuthenticated] # 로그인권한
                community = self.get_object(pk)
                community_images = request.FILES.getlist('images')
                serializer = CommunityDetailSerializer(community, data=request.data, partial=True)
                
                if community.author != request.user :
                    return Response( {"error" : "다른 사용자의 글은 수정할 수 없습니다"}, status=status.HTTP_403_FORBIDDEN)
                
                if serializer.is_valid(raise_exception=True):
                        serializer.save()

                        if 'images' in request.FILES or not community_images:
                        # 기존 이미지 삭제
                            community.community_images.all().delete()
                            # 새로운 이미지 저장
                            for community_image in community_images:
                                CommunityImage.objects.create(community=community, community_image=community_image)
                                return Response(serializer.data)
                        return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        def delete(self, request, pk): # 커뮤니티 삭제
                permission_classes = [IsAuthenticated] # 로그인권한
                community = self.get_object(pk)
                
                if community.author != request.user :
                    return Response( {"error" : "다른 사용자의 글은 삭제할 수 없습니다"}, status=status.HTTP_403_FORBIDDEN)

                community.delete()
                return Response({'삭제되었습니다'}, status=status.HTTP_204_NO_CONTENT)


class CommunityLikeAPIView(APIView): # 커뮤 좋아요
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        community = get_object_or_404(Community, pk=pk)

        if CommunityLike.objects.filter(community=community, user=request.user).exists(): # 좋아요 두번 누르면
            CommunityLike.objects.filter(community=community, user=request.user).delete()
            return Response({"좋아요 취소"}, status=status.HTTP_200_OK)
        
        elif CommunityDislike.objects.filter(community=community, user=request.user).exists(): # 싫어요 누르고 좋아요 누르면
            CommunityDislike.objects.filter(community=community, user=request.user).delete()
            CommunityLike.objects.create(community=community, user=request.user)
            return Response({'좋아요 +1 | 싫어요 -1'}, status=status.HTTP_200_OK)
        
        else:
            CommunityLike.objects.create(community=community, user=request.user) # 좋아요 처음 누르면
            return Response({'좋아요 +1'}, status=status.HTTP_200_OK)

class CommunityDislikeAPIView(APIView): # 커뮤 싫어요
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        community = get_object_or_404(Community, pk=pk)

        if CommunityDislike.objects.filter(community=community, user=request.user).exists(): # 싫어요 두번 누르면
            CommunityDislike.objects.filter(community=community, user=request.user).delete()
            return Response({"싫어요 취소"}, status=status.HTTP_200_OK)
        
        elif CommunityLike.objects.filter(community=community, user=request.user).exists(): # 좋아요 누르고 싫어요 누르면
            CommunityLike.objects.filter(community=community, user=request.user).delete()
            CommunityDislike.objects.create(community=community, user=request.user)
            return Response({'좋아요 -1 | 싫어요 +1'}, status=status.HTTP_200_OK)
        
        else:
            CommunityDislike.objects.create(community=community, user=request.user) # 싫어요 처음 누르면
            return Response({'싫어요 +1'}, status=status.HTTP_200_OK)

class CommunityUnusableAPIView(APIView): # 커뮤글 신고
    permission_classes = [IsAuthenticated]


    def post(self, request, pk):
        user = request.user
        community = get_object_or_404(Community, pk=pk)

        if user not in community.unusables.all():
            community.unusables.add(user) 
            
            return Response({"신고가 접수되었습니다"},  status=status.HTTP_200_OK)
        
        return Response({"이미 신고되었습니다"},  status=status.HTTP_200_OK) # 신고는 취소 불가
