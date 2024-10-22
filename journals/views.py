from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render, get_object_or_404
from django.db import models
from django.db.models import Q
from django.http import JsonResponse
from django.utils.dateparse import parse_date
from django.views.generic import ListView
from rest_framework import status
from rest_framework.views import View, APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.generics import ListAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from .forms import JournalForm
from .models import Comment, CommentLike, Journal, JournalImage, JournalLike
from .serializers import CommentSerializer, JournalSerializer,JournalDetailSerializer
import datetime




class JournalListAPIView(ListAPIView): # 저널 전체목록조회, 저널작성, 저널검색
    serializer_class = JournalSerializer
    parser_classes = (MultiPartParser, FormParser)
        
    def get_queryset(self):
        permission_classes = [AllowAny]
        queryset = Journal.objects.all().order_by('-created_at')

        # 검색 쿼리 파라미터
        search_query = self.request.query_params.get('search', None)
        filter_by = self.request.query_params.get('filter', 'title')  # 기본값: 제목 검색
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)

        # 검색어가 있을 경우 필터링
        if search_query:
            if filter_by == 'title':
                queryset = queryset.filter(Q(title__icontains=search_query))
            elif filter_by == 'content':
                queryset = queryset.filter(Q(content__icontains=search_query))
            elif filter_by == 'author':
                queryset = queryset.filter(Q(author__nickname__icontains=search_query))

        # 날짜 필터링
        if start_date:
            start_date_parsed = parse_date(start_date)
            if start_date_parsed:
                queryset = queryset.filter(created_at__gte=start_date_parsed)

        if end_date:
            end_date_parsed = parse_date(end_date)
            if end_date_parsed:
                queryset = queryset.filter(created_at__lte=end_date_parsed)

        return queryset

    def post(self, request): # 작성
        permission_classes = [IsAuthenticated] # 로그인권한
        serializer = JournalSerializer(data=request.data)

        if request.user.grade != 'author' :
            return Response( {"error" : "저널리스트 회원이 아닙니다"}, status=status.HTTP_403_FORBIDDEN)

        if serializer.is_valid(raise_exception=True):
            journal = serializer.save(author=request.user)  # 현재 로그인한 유저 저장
            journal_images = request.FILES.getlist('images')
            for journal_image in journal_images:
                JournalImage.objects.create(journal=journal, journal_image=journal_image)

            return Response(serializer.data, status=201)
        else:
            return Response(serializer.errors, status=400)
            
#             # 쿠키 만료 시간: 자정으로 설정
#             tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
#             expires = tomorrow.strftime("%a, %d-%b-%Y %H:%M:%S GMT")

#             # 조회수 업데이트: 쿠키에 hit 값이 없는 경우
#             if request.COOKIES.get('hit_count') is not None:
#                 cookies = request.COOKIES.get('hit_count')
#                 cookies_list = cookies.split('|')  # '|' 대신 다른 구분자도 사용 가능
#                 if str(pk) not in cookies_list:
#                     journal.hit()  # 조회수 증가
#                     response = Response(JournalDetailSerializer(journal).data)
#                     response.set_cookie('hit_count', cookies + f'|{pk}', expires=expires)
#                     return response
#             else:
#                 journal.hit()  # 조회수 증가
#                 response = Response(JournalDetailSerializer(journal).data)
#                 response.set_cookie('hit_count', pk, expires=expires)
#                 return response

#             # hit 쿠키가 이미 있는 경우 조회수는 증가하지 않음
#             serializer = JournalDetailSerializer(journal)
#             return Response(serializer.data)

#         def put(self, request, pk):  # 저널 수정
#             journal = self.get_object(pk)
#             journal_images = request.FILES.getlist('images')
#             serializer = JournalDetailSerializer(journal, data=request.data, partial=True)
            
class JournalListView(ListView):
    model = Journal
    template_name = 'journals/journal_list.html'  # 사용할 템플릿
    context_object_name = 'journals'  # 템플릿에서 사용할 변수명
    paginate_by = 12  # 한 페이지에 표시할 저널 수

    def get_queryset(self):
        queryset = Journal.objects.all().order_by('-created_at')

        # request.GET을 사용하여 검색 파라미터 가져오기
        search_query = self.request.GET.get('search', None)
        filter_by = self.request.GET.get('filter', 'title')  # 기본값: 제목 검색
        start_date = self.request.GET.get('start_date', None)
        end_date = self.request.GET.get('end_date', None)

        # 검색어가 있을 경우 필터링
        if search_query:
            if filter_by == 'title':
                queryset = queryset.filter(Q(title__icontains=search_query))
            elif filter_by == 'content':
                queryset = queryset.filter(Q(content__icontains=search_query))
            elif filter_by == 'author':
                queryset = queryset.filter(Q(author__nickname__icontains=search_query))

        # 날짜 필터링
        if start_date:
            start_date_parsed = parse_date(start_date)
            if start_date_parsed:
                queryset = queryset.filter(created_at__gte=start_date_parsed)

        if end_date:
            end_date_parsed = parse_date(end_date)
            if end_date_parsed:
                queryset = queryset.filter(created_at__lte=end_date_parsed)

        return queryset


class JournalDetailAPIView(APIView):  # 저널 상세조회, 수정, 삭제
    
    def get_object(self, journalKey):
        # journalKey로 저널을 찾음
        return get_object_or_404(Journal, journalKey=journalKey)
    
    def get(self, request, journalKey):
        journal = self.get_object(journalKey)
        journal.hit()  # 조회수 증가

        # 로그인한 경우에만 좋아요 여부 확인
        is_liked = request.user.is_authenticated and journal.journal_likes.filter(user=request.user).exists()

        # 시리얼라이저를 이용하여 저널 데이터를 반환
        serializer = JournalDetailSerializer(journal)
        context = {
            'journal': serializer.data,
            'is_liked': is_liked,  # 좋아요 상태 추가
        }
        print(context)
        
        return render(request, 'journals/journal_detail.html', context)
      
        # # 내가 입력한 images에서 이미지가 있거나 없을때
        # if 'images' in request.FILES or not journal_images:
        #     # 기존 이미지 삭제
        #     journal.journal_images.all().delete()
        #     # 새로운 이미지 저장
        #     for journal_image in journal_images:
        #         JournalImage.objects.create(journal=journal, journal_image=journal_image)


    def put(self, request, journalKey):  # 저널 수정
        journal = self.get_object(journalKey)
        journal_images = request.FILES.getlist('images')
        serializer = JournalDetailSerializer(journal, data=request.data, partial=True)
        
        if journal.author != request.user :
                return Response( {"error" : "다른 사용자의 글은 수정할 수 없습니다"}, status=status.HTTP_403_FORBIDDEN)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

            # 만약 새로운 이미지가 있다면, 기존 이미지를 삭제하고 새로운 이미지를 추가
            if 'images' in request.FILES or not journal_images:
                # 기존 이미지 삭제
                journal.journal_images.all().delete()
                # 새로운 이미지 저장
                for journal_image in journal_images:
                    JournalImage.objects.create(journal=journal, journal_image=journal_image)

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            
    def delete(self, request, journalKey): # 저널 삭제
        permission_classes = [IsAuthenticated] # 로그인권한
        journal = self.get_object(journalKey)
        
        if journal.author != request.user :
            return Response( {"error" : "다른 사용자의 글은 삭제할 수 없습니다"}, status=status.HTTP_403_FORBIDDEN)

        journal.delete()
        return Response({'삭제되었습니다'}, status=status.HTTP_204_NO_CONTENT)     


class JournalLikeAPIView(APIView): # 저널 좋아요/좋아요취소 
    permission_classes = [IsAuthenticated]

    def post(self, request, journalKey):
        journal = get_object_or_404(Journal, pk=journalKey)
        journal_like, created = JournalLike.objects.get_or_create(journal=journal, user=request.user)

        if not created:  # 이미 좋아요를 눌렀다면 좋아요 취소
            journal_like.delete()
            is_liked = False
        else:
            is_liked = True

        return Response({'is_liked': is_liked}, status=status.HTTP_200_OK)
    

class CommentView(APIView): # 저널 댓글
    def get(self, request, journalKey):
        comments = Comment.objects.filter(journal_id=journalKey)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def post(self, request, journalKey, parent_id=None):
        data = request.data.copy()
        journal = get_object_or_404(Journal, journalKey=journalKey)
        data['journal'] = journalKey
        
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
        return Response({"댓글이 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)


class CommentLikeView(APIView): # 저널 댓글좋아요
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
        
        # 좋아요와 싫어요 수 계산
        like_count = CommentLike.objects.filter(comment=comment, like_type='like').count()
        dislike_count = CommentLike.objects.filter(comment=comment, like_type='dislike').count()
        
        return Response({
            'message': message,
            'like_count': like_count,
            'dislike_count': dislike_count
        }, status=status.HTTP_200_OK)
    

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


class JournalWriteView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request):
        # 저널 작성 페이지 렌더링
        form = JournalForm()
        return render(request, 'journals/journal_write.html', {'form': form})

    def post(self, request):
            form = JournalForm(request.POST, request.FILES)
            if form.is_valid():
                journal = form.save(commit=False)
                journal.author = request.user  # 작성자를 현재 로그인한 사용자로 설정
                journal.save()

                # 이미지 파일 처리
                for image in request.FILES.getlist('images'):
                    JournalImage.objects.create(journal=journal, journal_image=image)

                # 성공적으로 작성한 경우 JSON 응답 반환
                return JsonResponse({'message': 'Journal created successfully', 'journalKey': journal.journalKey}, status=201)
            else:
                # 유효성 검사 실패 시 JSON 응답 반환
                return JsonResponse({'errors': form.errors}, status=400)
            

class JournalLikeStatusAPIView(APIView):

    def get(self, request, journalKey):
        journal = get_object_or_404(Journal, journalKey=journalKey)
        # 사용자가 이 저널을 좋아요 했는지 여부 확인
        is_liked = journal.journal_likes.filter(user=request.user).exists()
        return Response({'is_liked': is_liked}, status=status.HTTP_200_OK)
    
    
class JournalEditView(APIView):

    def get(self, request, journalKey):
        journal = get_object_or_404(Journal, journalKey=journalKey)

        context = {
            'journal': journal,
            'is_edit': True  # 수정 상태 표시를 위한 변수
        }
        return render(request, 'journals/journal_write.html', context)

    def put(self, request, journalKey):
        journal = get_object_or_404(Journal, journalKey=journalKey)

        if journal.author != request.user:
            return Response({"detail": "수정 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

        serializer = JournalSerializer(journal, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            # 기존 이미지 삭제 (새 이미지를 저장할 때만 삭제)
            if 'images' in request.FILES:
                journal.journal_images.all().delete()  # 기존 이미지를 모두 삭제

                # 새 이미지 저장
                for image in request.FILES.getlist('images'):
                    JournalImage.objects.create(journal=journal, journal_image=image)

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)