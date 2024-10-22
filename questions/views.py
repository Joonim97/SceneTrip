import datetime
from django.http import JsonResponse
from rest_framework import generics
from .models import Questions, Comments, QuestionsImage
from .serializers import QuestionImageSerializer, QuestionSerializer, QuestionDetailSerializer, CommentSerializer
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated, AllowAny
import uuid
from django.core.exceptions import ValidationError
from django.views.generic import ListView
from .forms import QuestionForm
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

# 큐엔에이 페이지

from django.shortcuts import render, redirect
from .models import Questions

class QnaListView(ListView):
    model = Questions
    template_name = 'questions/qna_list.html'  # 사용할 템플릿
    context_object_name = 'questions'  # 템플릿에서 사용할 변수명
    paginate_by = 10  # 한 페이지에 개수

    def get_queryset(self):
        return Questions.objects.all().order_by('-created_at')  # 최신 순으로 정렬

class QnaWriteView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request):
        # 저널 작성 페이지 렌더링
        form = QuestionForm()
        return render(request, 'questions/qna_write.html', {'form': form})

    def post(self, request):
            form = QuestionForm(request.POST, request.FILES)
            if form.is_valid():
                question = form.save(commit=False)
                question.author = request.user  # 작성자를 현재 로그인한 사용자로 설정
                question.save()
                question_images = request.FILES.getlist('images')
                for question_image in question_images:
                    QuestionsImage.objects.create(question=question, question_images=question_image)

                # 성공적으로 작성한 경우 JSON 응답 반환
                return JsonResponse({'message': 'Question created successfully', 'id': question.questionKey}, status=201)
            else:
                # 유효성 검사 실패 시 JSON 응답 반환
                return JsonResponse({'errors': form.errors}, status=400)

# 큐앤에이 전체 목록 조회 & 작성
class QuestionListView(APIView):
    def get(self, request) : # 전체목록
        permission_classes = [AllowAny] 
        queryset = Questions.objects.all().order_by('-created_at')
        serializer = QuestionSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        permission_classes = [IsAuthenticated]
        serializer = QuestionDetailSerializer(data=request.data)
        # 데이터 유효성 검사
        if serializer.is_valid(raise_exception=True):
            # 질문 저장 및 로그인한 사용자 저장
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        # 유효하지 않은 데이터인 경우 오류 응답 반환
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class QuestionDetailAPIView(APIView):  # 큐앤에이 상세조회, 수정, 삭제
    permission_classes = [IsAuthenticated]  # 로그인 권한

    def get(self, request, key=None):
        question = get_object_or_404(Questions, pk=key)

        images = question.images.all()
        image_serializer = QuestionImageSerializer(images, many=True)

        # 쿠키 만료 시간: 자정으로 설정
        tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
        expires = tomorrow.strftime("%a, %d-%b-%Y %H:%M:%S GMT")

        # 조회수 업데이트: 쿠키에 hit 값이 없는 경우
        hit_count_cookie = request.COOKIES.get('hit_count')
        if hit_count_cookie is not None:
            cookies_list = hit_count_cookie.split('|')  # '|' 구분자 사용
            if str(key) not in cookies_list:
                question.hit()  # 조회수 증가
                # 질문 직렬화
                serializer = QuestionDetailSerializer(question)
                context = {
                'question': serializer.data,
                'images': image_serializer.data
                }

            # JSON 응답 대신 HTML 템플릿을 렌더링
                response = render(request, 'questions/qna_detail.html', context)
                response.set_cookie('hit_count', hit_count_cookie + f'|{key}', expires=expires)
                return response
        else:
            question.hit()  # 조회수 증가
            # 질문 직렬화
            serializer = QuestionDetailSerializer(question)
            response = Response(serializer.data)
            response.set_cookie('hit_count', str(key), expires=expires)
            return response

        # hit 쿠키가 이미 있는 경우 조회수는 증가하지 않음
        serializer = QuestionDetailSerializer(question)
        context = {
            'question' : serializer.data,
            'images': images
        }
        print(context)
        return render(request,'questions/qna_detail.html', context)

    def put(self, request, key):  # 큐앤에이 수정
        permission_classes = [IsAuthenticated]
        question = get_object_or_404(Questions, pk=key)
        serializer = QuestionDetailSerializer(question, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

            # 삭제할 이미지 ID 리스트를 받음
            delete_image_ids = request.data.getlist('delete_images')  # 삭제할 이미지 ID를 리스트로 받음
            print("삭제할 이미지 ID들:", delete_image_ids)  # 로그로 출력
            if delete_image_ids:
            # 선택된 이미지 삭제
                QuestionsImage.objects.filter(id__in=delete_image_ids, question=question).delete()

            question_images = request.FILES.getlist('images')  # 새로운 이미지 리스트 가져오기
            if question_images:  # 새로운 이미지가 전송된 경우에만 처리

                # 새로운 이미지 저장
                for question_image in question_images:
                    QuestionsImage.objects.create(question=question, question_images=question_image)

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request, key):  # 큐앤에이 삭제
        permission_classes = [IsAuthenticated]
        question = get_object_or_404(Questions, pk=key)
        if question.author != request.user:
            return Response({"error": "다른 사용자의 글은 삭제할 수 없습니다"}, status=status.HTTP_403_FORBIDDEN)

        question.delete()
        return Response({'message': '삭제되었습니다'}, status=status.HTTP_204_NO_CONTENT)

class CommentView(APIView):

    # 댓글 조회
    def get(self, request, key):
        comments = Comments.objects.filter(questionKey=key)
        serializer = CommentSerializer(comments, many=True)
        context = {
            'comments': serializer.data
        }
        return render(request, 'questions/qna_detail.html', context)

    # 댓글 작성
    def post(self, request, key, parent_id=None):
        permission_classes = [IsAuthenticated]
        data = request.data.copy()  # 요청 데이터를 복사하여 수정 가능하게 처리
        question = get_object_or_404(Questions, questionKey=key)
        data['question'] = question.id  # 질문 ID를 데이터에 추가

        if parent_id:
            parent_comment = get_object_or_404(Comments, CommentKey=parent_id)
            data['parent'] = parent_comment.CommentKey

        serializer = CommentSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user, question=question)  # 작성자 추가
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 댓글 수정
    def put(self, request, key):
        permission_classes = [IsAuthenticated]
        comment = get_object_or_404(Comments, CommentKey=key)

        if comment.user != request.user:
            raise PermissionDenied("수정 권한이 없습니다.")

        serializer = CommentSerializer(comment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 댓글 삭제
    def delete(self, request, key):
        permission_classes = [IsAuthenticated]
        comment = get_object_or_404(Comments, CommentKey=key)

        if comment.user != request.user:
            raise PermissionDenied("삭제 권한이 없습니다.")

        comment.delete()
        return Response({"message": "댓글이 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)



