from rest_framework import generics
from .models import Questions, Comments
from .serializers import QuestionSerializer, QuestionDetailSerializer, CommentSerializer
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated, AllowAny
import uuid
from django.core.exceptions import ValidationError

# 큐앤에이 전체 목록 조회 & 작성
class QuestionListView(APIView):
    def get(self, request) : # 전체목록
        permission_classes = [AllowAny] 
        queryset = Questions.objects.all().order_by('-created_at')
        serializer = QuestionSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request) : # 작성
        permission_classes = [IsAuthenticated] # 로그인권한
        serializer = QuestionDetailSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            question = serializer.save(author=request.user)  # 현재 로그인한 유저 저장
            question.save()
            serializer=QuestionDetailSerializer(question)
            return Response(serializer.data, status=201)
        else:
            return Response(serializer.errors, status=400)


class QuestionDetailAPIView(APIView): # 큐앤에이 상세조회,수정,삭제

        def get(self, request, key): # 큐앤에이 상세조회
                permission_classes = [IsAuthenticated] # 로그인권한
                question = get_object_or_404(Questions,pk=key)
                serializer = QuestionDetailSerializer(question)
                if question.author != request.user :
                    return Response( {"error" : "다른 사용자의 질문은 조회할 수 없습니다"}, status=status.HTTP_403_FORBIDDEN)
                return Response(serializer.data)

        def put(self, request, key): # 큐앤에이 수정
                permission_classes = [IsAuthenticated] # 로그인권한
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
