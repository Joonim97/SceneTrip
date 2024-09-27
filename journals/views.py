from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from .models import Journal # 저널모델 여기
from .serializers import JournalSerializer,JournalDetailSerializer # 시리얼라이저 여기
from django.conf import settings


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
                        return Response(serializer.data, status=201)
                else:
                        return Response(serializer.errors, status=400)


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
                return Response({'삭제되었습니다'}, status=204)
        

class JournalSearchSet(ListAPIView): # 저널 검색
        queryset=Journal.objects.all()
        serializer_class=JournalSerializer

        filter_backends=[SearchFilter]
        search_fields=[ 'title'] # 내용, 작성자로 찾기 추가해야 함
