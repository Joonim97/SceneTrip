from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from .models import Community # 커뮤니티모델 여기
from .serializers import CommunitySerializer, CommunityDetailSerializer # 시리얼라이저 여기
from django.conf import settings


class CommunityListAPIView(ListAPIView): # 전체목록조회, 커뮤니티작성
        queryset = Community.objects.all().order_by('-created_at') # 생성최신순 조회
        serializer_class = CommunitySerializer
        
        # def get(self, request): #전체목록 일단 주석처리리
        #         community = Community.objects.all()
        #         serializer = CommunitySerializer(community))
        #         return Response(community)
        
        def post(self, request): # 커뮤니티 작성               
                serializer = CommunitySerializer(data=request.data)
                if serializer.is_valid(raise_exception=True):
                        serializer.save()
                        return Response(serializer.data, status=201)
                else:
                        return Response(serializer.errors, status=400)


class CommunityDetailAPIView(APIView): # 커뮤니티 상세조회,수정,삭제
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
                return Response({'삭제되었습니다'}, status=204)
        

# class JournalSearchSet(ListAPIView): # 커뮤니티 검색
#         queryset=Community.objects.all()
#         serializer_class=CommunitySerializer

#         filter_backends=[SearchFilter]
#         search_fields=[ 'title'] # 내용, 작성자로 찾기 추가해야 함

