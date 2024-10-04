from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import Location, LocationSave
from .serializers import LocationSerializer
import re


def custom_sort_key(value):
    # 한글, 알파벳, 숫자, 특수기호 순으로 정렬
    if re.match(r"^[가-힣]", value):
        return (0, value)
    elif re.match(r"^[a-zA-Z]", value):
        return (1, value)
    elif re.match(r"^[0-9]", value):
        return (2, value)
    else:
        return (3, value)


class LocationListAPIView(APIView):
    # 촬영지 목록 조회
    def get(self, request):
        sort_by = request.query_params.get('sort_by', 'title') # parameter로 sort_by를 따로 지정해주지 않으면 title이 default.
        location_data = Location.objects.values('id', 'title', 'place_name', 'save_count')
        
        if sort_by == 'title':
            # 제목으로 정렬. 위의 custom_sort_key에 따라 정렬.
            sorted_location_data = sorted(location_data, key=lambda x: custom_sort_key(x['title']))
        elif sort_by == 'popularity':
            # 저장수에 따라 정렬. 많이 저장된 촬영지 == 인기 촬영지.
            sorted_location_data = sorted(location_data, key=lambda x: x['save_count'], reverse=True)
        else:
            return Response({"error": "Invalid sort_by parameter"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(sorted_location_data)
    

class LocationRegionAPIView(APIView):
    # 촬영지 지역별 조회
    def get(self, request, region, *args, **kwargs):
        regions = [
            '경기도', '서울특별시', '인천광역시', '강원도', '경상남도', '경상북도', 
            '광주광역시', '대구광역시', '대전광역시', '울산광역시', '부산', # 부산광역시의 경우 '부산'으로만 기록되어 있는 데이터도 있어서.
            '전라남도', '전라북도', '제주특별자치도', '충청남도', '충청북도', '세종특별자치시'
        ]

        if region not in regions:
            return Response({"error": "Invalid region"}, status=400)
        
        region_data = {}
        location_data = Location.objects.filter(address__contains=region).values('id', 'title', 'place_name', 'save_count')

        sort_by = request.query_params.get('sort_by', 'title') # parameter로 sort_by를 따로 지정해주지 않으면 title이 default.
        
        if sort_by == 'title':
            # 제목으로 정렬. 위의 custom_sort_key에 따라 정렬.
            sorted_data = sorted(location_data, key=lambda x: custom_sort_key(x['title']))
        elif sort_by == 'popularity':
            # 저장수에 따라 정렬. 많이 저장된 촬영지 == 인기 촬영지.
            sorted_data = sorted(location_data, key=lambda x: x['save_count'], reverse=True)
        else:
            return Response({"error": "Invalid sort_by parameter"}, status=status.HTTP_400_BAD_REQUEST)
        
        region_data[region] = sorted_data

        return Response(region_data)


class LocationDetailAPIView(APIView):
    # 촬영지 상세조회
    def get(self, request, pk):
        location = get_object_or_404(Location, pk=pk)
        serializer = LocationSerializer(location)
        return Response(serializer.data)


class LocationSearchAPIView(APIView):
    # 촬영지 검색
    def get(self, request, *args, **kwargs):
        query_params = request.query_params
        search_value = query_params.get("keyword", None) # 검색 keyword
        filter_fields = ["media_type", "title", "place_name", "place_type", "place_description", "address"]

        filters = Q()
        if search_value:
            for field in filter_fields:
                filters |= Q(**{f"{field}__icontains": search_value})

        location_data = Location.objects.filter(filters).values('id', 'title', 'place_name', 'save_count')
        sorted_location_data = sorted(
            location_data, key=lambda x: custom_sort_key(x['title'])
        )
        
        # 키워드에 해당하는 검색결과가 없을 때.
        if not location_data or search_value.strip() == "":
            return Response({"message": "검색 결과가 없습니다"}, status=status.HTTP_200_OK)

        return Response(sorted_location_data, status=status.HTTP_200_OK)


class LocationSaveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        user = request.user
        location = get_object_or_404(Location, id=id)
        location_save, created = LocationSave.objects.get_or_create(user=user, location=location)

        if created:
            location.save_count += 1
            location.save()
            location_save.save()
            return Response({"message": "촬영지 정보가 저장되었습니다."}, status=status.HTTP_201_CREATED)
        else:
            location.save_count -= 1
            location.save()
            location_save.delete()
            return Response({"message": "촬영지 정보가 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)