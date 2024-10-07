from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import Location, LocationSave
from .serializers import LocationSerializer
from django.conf import settings
import re
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import requests


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
        sorted_location_data = sorted(location_data, key=lambda x: custom_sort_key(x['title']))
        
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


class RecommendAPIView(APIView):
        # AI 여행 플래닝 서비스
        permission_classes = [IsAuthenticated]

        def get_place_details(place_name):
        # Google Maps API를 이용하여 장소 정보 검색
            api_key = "YOUR_GOOGLE_MAPS_API_KEY"
            url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={place_name}&key={api_key}"
            response = requests.get(url)
            data = response.json()
            # 검색 결과에서 필요한 정보 추출 (예: 장소 이름, 주소, 사진 등)

            return data

        def post(self, request):
            llm = ChatOpenAI(model="gpt-4o-mini", api_key=settings.API_KEY)
            query_params = request.query_params
            place_name = query_params.get("place_name")
            n = query_params.get("n", 0)
            m = query_params.get("m", 0)
            preference = query_params.get("preference", None)

            if not place_name:
                return Response({"방문하고자 하는 촬영지를 입력해주세요. 해당 촬영지를 포함한 여행 계획을 세워드립니다."}, status=status.HTTP_200_OK)

            template = "{place_name} 방문을 포함한 "
            if preference and len(preference)<=50:
                template += f"{preference}한 여행취향의 "
                if n and m: 
                    # n, m 입력 받음.
                    template += f"{n}박 {m}일 동안의 여행 계획을 자세히 알려줘."
                else: 
                    # n, m을 입력받지 않는 경우. (당일치기 여행계획 버튼을 따로 만들기.)
                    template += "당일치기 여행 계획을 자세히 알려줘."
            elif preference and len(preference)>50: 
                # 선호하는 여행 스타일은 50자 이내로 입력해야 함.
                return Response({"여행 취향을 50자 이내로 적어주세요."})
            else:
                if n and m: 
                    template += f"{n}박 {m}일 동안의 여행 계획을 자세히 알려줘."
                else:
                    template += "당일치기 여행 계획을 자세히 알려줘."


            prompt = PromptTemplate(template=template, input_variables=["place_name", "preference"])
            llm_chain = LLMChain(prompt=prompt, llm=llm)

            response = llm_chain.run(place_name=place_name)
            return Response(response)
        