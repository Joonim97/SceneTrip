from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from django.views.generic import ListView
from rest_framework import status
from rest_framework.views import APIView, View
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Comment, CommentLike, CommunityLike, CommunityDislike, Community, CommunityImage
from .serializers import CommentSerializer, CommunitySerializer, CommunityDetailSerializer

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import CommunityForm  # 커뮤니티 글 작성 폼

class CommentView(APIView): # 커뮤 댓글
    def get(self, request, communityKey):
        comments = Comment.objects.filter(community_id=communityKey)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def post(self, request, communityKey, parent_id=None):
        data = request.data.copy()
        community = get_object_or_404(Community, communityKey=communityKey)
        data['community'] = communityKey
        
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
            
            
class CommunityListView(ListView):
    serializer_class = CommunitySerializer
    model = Community
    template_name = 'communities/community_list.html'  # 사용할 템플릿
    context_object_name = 'communities'  # 템플릿에서 사용할 변수명
    paginate_by = 10  # 페이지당 표시할 글 수

    def get_queryset(self):
        queryset = Community.objects.all().order_by('-created_at')

        # 검색 파라미터 처리
        search_query = self.request.GET.get('search', None)
        filter_by = self.request.GET.get('filter', 'title')  # 기본값: 제목 검색

        if search_query:
            if filter_by == 'title':
                queryset = queryset.filter(title__icontains=search_query)
            elif filter_by == 'content':
                queryset = queryset.filter(content__icontains=search_query)
            elif filter_by == 'author':
                queryset = queryset.filter(author__nickname__icontains=search_query)

        return queryset


class CommunityDetailAPIView(APIView): # 커뮤니티 상세조회,수정,삭제
        
    def get_object(self, communityKey):
            return get_object_or_404(Community, communityKey=communityKey)

    def get(self, request, communityKey): # 커뮤니티 상세조회
        community = self.get_object(communityKey)

        if community.unusables.count() >= 30 : # 3회 이상 신고된 글 접근 불가
            return Response({ "detail": "신고가 누적된 글은 볼 수 없습니다." }, status=status.HTTP_404_NOT_FOUND )

        serializer = CommunityDetailSerializer(community)
        context = {
        'community': serializer.data,
        }
        print(context)
        
        # 템플릿을 렌더링하여 반환
        return render(request, 'communities/community_detail.html', context)

    def put(self, request, communityKey): # 커뮤니티 수정
            permission_classes = [IsAuthenticated] # 로그인권한
            community = self.get_object(communityKey)
            community_images = request.FILES.getlist('images')
            serializer = CommunityDetailSerializer(community, data=request.data, partial=True)
            print(request.user)
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
            
    def delete(self, request, communityKey): # 커뮤니티 삭제
            permission_classes = [IsAuthenticated] # 로그인권한
            community = self.get_object(communityKey)
            
            if community.author != request.user :
                return Response( {"error" : "다른 사용자의 글은 삭제할 수 없습니다"}, status=status.HTTP_403_FORBIDDEN)

            community.delete()
            return Response({'삭제되었습니다'}, status=status.HTTP_204_NO_CONTENT)


class CommunityLikeAPIView(APIView): # 커뮤 좋아요
    permission_classes = [IsAuthenticated]

    def post(self, request, communityKey):
        community = get_object_or_404(Community, communityKey=communityKey)

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

    def post(self, request, communityKey):
        community = get_object_or_404(Community, communityKey=communityKey)

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


    def post(self, request, communityKey):
        user = request.user
        community = get_object_or_404(Community, communityKey=communityKey)

        if user not in community.unusables.all():
            community.unusables.add(user) 
            
            return Response({"신고가 접수되었습니다"},  status=status.HTTP_200_OK)
        
        return Response({"이미 신고되었습니다"},  status=status.HTTP_200_OK) # 신고는 취소 불가


class CommunityWriteView(APIView):

    def get(self, request):
        # 커뮤니티 글 작성 페이지 렌더링
        form = CommunityForm()
        return render(request, 'communities/community_write.html', {'form': form})

    def post(self, request):
        form = CommunityForm(request.POST, request.FILES)
        if form.is_valid():
            community = form.save(commit=False)
            community.author = request.user
            community.save()

            # 이미지 파일 처리
            for image in request.FILES.getlist('community_images'):
                CommunityImage.objects.create(community=community, community_image=image)
            print(community.communityKey)

            # 성공적으로 작성한 경우 JSON 응답 반환
            return JsonResponse({'message': 'Community post created successfully', 'communityKey': community.communityKey}, status=201)

        else:
            # 유효성 검사 실패 시 JSON 응답 반환
            return JsonResponse({'errors': form.errors}, status=400)
        
        
class CommunityEditAPIView(APIView):

    def get_object(self, communityKey):
        return get_object_or_404(Community, communityKey=communityKey)

    def get(self, request, communityKey):  # 커뮤니티 수정 페이지에서 기존 데이터 가져오기
        community = get_object_or_404(Community, communityKey=communityKey)
    
        context = {
            'community': community  # 기존 커뮤니티 데이터를 템플릿에 전달
        }

        return render(request, 'communities/community_write.html', context)  # community_write.html로 렌더링

    def put(self, request, communityKey):  # 커뮤니티 수정
        community = get_object_or_404(Community, communityKey=communityKey)

        if community.author != request.user:
            return Response({"error": "다른 사용자의 글은 수정할 수 없습니다"}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = CommunitySerializer(community, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            
                        # 기존 이미지 삭제 (새 이미지를 저장할 때만 삭제)
            if 'community_images' in request.FILES:
                community.community_images.all().delete()  # 기존 이미지를 모두 삭제

                # 새 이미지 저장
                for image in request.FILES.getlist('community_images'):
                    CommunityImage.objects.create(community=community, community_image=image)
                    
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class CommunityLikeStatusAPIView(APIView):  # 좋아요 상태 확인
    def get(self, request, communityKey):
        community = get_object_or_404(Community, communityKey=communityKey)
        is_liked = community.community_likes.filter(user=request.user).exists()
        return Response({'is_liked': is_liked}, status=status.HTTP_200_OK)

class CommunityDislikeStatusAPIView(APIView):  # 싫어요 상태 확인
    def get(self, request, communityKey):
        community = get_object_or_404(Community, communityKey=communityKey)
        is_disliked = community.community_dislikes.filter(user=request.user).exists()
        return Response({'is_disliked': is_disliked}, status=status.HTTP_200_OK)