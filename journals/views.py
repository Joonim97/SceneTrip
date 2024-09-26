from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from .models import Journal # 저널모델 여기
from .serializers import JournalSerializer,JournalDetailSerializer # 시리얼라이저 여기
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.prompts import PromptTemplate
# from langchain.chains import LLMChain
from rest_framework.pagination import PageNumberPagination
from django.conf import settings


class JournalListAPIView(ListAPIView): # 전체목록조회, 저널작성
        queryset = Journal.objects.all().order_by('-created_at') # 생성최신순
        serializer_class = JournalSerializer
        # get_objects=que

        # def get(self, request): #전체목록
        #         journal = Journal.objects.all()
        #         serializer = JournalSerializer(journal)
        #         return Response(journal)
        
        def post(self, request): #  작성               
                serializer = JournalSerializer(data=request.data)
                if serializer.is_valid(raise_exception=True):
                        serializer.save()
                        return Response(serializer.data, status=201)
                else:
                        return Response(serializer.errors, status=400)


class JournalDetailAPIView(APIView): # 저널 조회,수정,삭제
        def get_object(self, pk):
                return get_object_or_404(Journal, pk=pk)

        def get(self, request, pk):
                journal = self.get_object(pk)
                serializer = JournalDetailSerializer(journal)
                return Response(serializer.data)

        def put(self, request, pk): # 글 수정
                if request.user.is_authenticated: 
                        journal = self.get_object(pk)
                        if journal.author.username == request.user.username:
                                journal.image.delete()
                                serializer = JournalDetailSerializer(
                                journal, data=request.data, partial=True)
                                if serializer.is_valid(raise_exception=True):
                                        serializer.save()
                                return Response(serializer.data)
                        return Response({'작성자만 수정 ㄱㄴ'}, status=403)
                return Response({'로그인 후 이용 가능합니다'}, status=400)
                
        def delete(self, request, pk): 
                if request.user.is_authenticated: 
                        journal = self.get_object(pk)
                        if journal.author.username == request.user.username:
                                journal.delete()
                                return Response({'삭제되었습니다'}, status=204)
                        return Response({'작성자가 아닙니다'}, status=403)
                return Response({'로그인 후 이용 가능합니다'}, status=400)