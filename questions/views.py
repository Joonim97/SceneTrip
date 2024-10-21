import datetime
from django.http import JsonResponse
from rest_framework import generics
from .models import Questions, Comments, QuestionsImage
from .serializers import QuestionSerializer, QuestionDetailSerializer, CommentSerializer
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

                # 이미지 파일 처리
                for image in request.FILES.getlist('images'):
                    QuestionsImage.objects.create(question=question, question_images=image)

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


class QuestionDetailAPIView(APIView): # 큐앤에이 상세조회,수정,삭제
        permission_classes = [IsAuthenticated] # 로그인권한

        def get(self, request, key): # 큐앤에이 상세조회
                question = get_object_or_404(Questions,pk=key)
                serializer = QuestionDetailSerializer(question)
                if question.author != request.user :
                    return Response( {"error" : "다른 사용자의 질문은 조회할 수 없습니다"}, status=status.HTTP_403_FORBIDDEN)
                            # 쿠키 만료 시간: 자정으로 설정
                tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
                expires = tomorrow.strftime("%a, %d-%b-%Y %H:%M:%S GMT")

                # 조회수 업데이트: 쿠키에 hit 값이 없는 경우
                if request.COOKIES.get('hit_count') is not None:
                    cookies = request.COOKIES.get('hit_count')
                    cookies_list = cookies.split('|')  # '|' 대신 다른 구분자도 사용 가능
                    if str(key) not in cookies_list:
                        question.hit()  # 조회수 증가
                        response = Response(QuestionDetailSerializer(question).data)
                        response.set_cookie('hit_count', cookies + f'|{key}', expires=expires)
                        return response
                else:
                    question.hit()  # 조회수 증가
                    response = Response(QuestionDetailSerializer(question).data)
                    response.set_cookie('hit_count', key, expires=expires)
                    return response

                # hit 쿠키가 이미 있는 경우 조회수는 증가하지 않음
                serializer = QuestionDetailSerializer(question)
                return Response(serializer.data)

        def put(self, request, key): # 큐앤에이 수정
                question = get_object_or_404(Questions,pk=key)
                question_image = request.FILES.getlist('image')
                serializer = QuestionDetailSerializer(question, data=request.data, partial=True)
                
                if question.author != request.user :
                    return Response( {"error" : "다른 사용자의 글은 수정할 수 없습니다"}, status=status.HTTP_403_FORBIDDEN)
                
                if serializer.is_valid(raise_exception=True):
                        serializer.save()

                        if 'image' in request.FILES or not 'image' :
                        # 기존 이미지 삭제
                            question.image.all().delete()
                            # 새로운 이미지 저장
                            
                return Response(serializer.data , status=status.HTTP_200_OK)
                
        def delete(self, request, key): # 큐앤에이 삭제
                permission_classes = [IsAuthenticated] # 로그인권한
                question = get_object_or_404(Questions, pk=key)
                
                if question.author != request.user :
                    return Response( {"error" : "다른 사용자의 글은 삭제할 수 없습니다"}, status=status.HTTP_403_FORBIDDEN)

                question.delete()
                return Response({'삭제되었습니다'}, status=status.HTTP_204_NO_CONTENT)



# 댓글 작성
class CommentCreateView(APIView):
    queryset = Comments.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        question = get_object_or_404(Questions, id=self.kwargs['question_id'])
        # 작성자 또는 관리자 인지 확인
        if request.user == question.author or request.user.is_superuser:
            raise PermissionDenied("작성자 또는 관리자만 작성할 수 있습니다")
        
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, question=question)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 댓글 수정
class CommentUpdateView(APIView):
    queryset = Comments.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        comment = self.get_object()
        if comment.user != self.request.user:
            raise PermissionDenied("You do not have permission to edit this comment.")
        serializer.save()

# 댓글 삭제
class CommentDeleteView(generics.DestroyAPIView):
    queryset = Comments.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to delete this comment.")
        instance.delete()
