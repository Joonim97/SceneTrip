from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
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
        location_data = Location.objects.values('id', 'title', 'place_name')
        sorted_location_data = sorted(location_data, key=lambda x: custom_sort_key(x['title']))

        return Response(sorted_location_data)
    

class LocationDetailAPIView(APIView):
    # 촬영지 상세조회
    def get(self, request, pk):
        location = get_object_or_404(Location, pk=pk)
        serializer = LocationSerializer(location)
        return Response(serializer.data)
    pass


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

        location_data = Location.objects.filter(filters)
        sorted_location_data = sorted(
            location_data, key=lambda x: custom_sort_key(x.title)
        )
        serializer = LocationSerializer(sorted_location_data, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

