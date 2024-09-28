from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Location
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
        location_data = Location.objects.all()
        sorted_location_data = sorted(
            location_data, key=lambda x: custom_sort_key(x.제목)
        )
        serializer = LocationSerializer(sorted_location_data, many=True)

        return Response(serializer.data)


class LocationSearchAPIView(APIView):
    # 촬영지 검색
    def get(self, request, *args, **kwargs):
        query_params = request.query_params
        search_value = query_params.get("keyword", None)
        filter_fields = ["미디어타입", "제목", "장소명", "장소타입", "장소설명", "주소"]

        filters = Q()
        if search_value:
            for field in filter_fields:
                filters |= Q(**{f"{field}__icontains": search_value})

        location_data = Location.objects.filter(filters)
        sorted_location_data = sorted(
            location_data, key=lambda x: custom_sort_key(x.제목)
        )
        serializer = LocationSerializer(sorted_location_data, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
