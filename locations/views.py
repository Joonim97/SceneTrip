from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from django.urls import reverse
from django.db.models import Q, Count, Value
from django.conf import settings
from django.db.models.functions import Replace
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from journals.models import Journal
from communities.models import Community
from .models import Location, LocationSave
from .serializers import LocationSerializer
import re
import urllib
import json



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
    
class LocationListView(ListView):
    model = Location
    template_name = 'locations/location_list.html'
    context_object_name = 'locations'
    paginate_by = 12  # 한 페이지에 표시할 촬영지 수
    
    def get_queryset(self):
        queryset = super().get_queryset()
        keyword = self.request.GET.get('keyword', None)
        filter_by = self.request.GET.get('filter', 'title')  # 기본값: 제목 검색

        # 검색어가 있을 경우 분류에 따라 필터링
        if keyword:
            if filter_by == 'title':
                queryset = queryset.filter(Q(title__icontains=keyword))
            elif filter_by == 'address':
                queryset = queryset.filter(Q(address__icontains=keyword))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_obj = context['page_obj']

        # 현재 페이지와 페이지 그룹을 계산
        current_page = page_obj.number
        current_group = (current_page - 1) // 5 + 1
        start_page = (current_group - 1) * 5 + 1
        end_page = start_page + 4

        # 총 페이지 수를 넘지 않도록 조정
        if end_page > page_obj.paginator.num_pages:
            end_page = page_obj.paginator.num_pages

        # 템플릿으로 start_page와 end_page 전달
        context['page_range'] = range(start_page, end_page + 1)
        return context
    

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


def get_nearby_place(place_name):
        client_id = settings.NAVER_CLIENT_ID
        client_secret = settings.NAVER_SECRET_KEY
        
        if not place_name:
            return Response({"error": "place_name is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        place_name_for_search = ''.join(place_name.strip().split())
        
        try:
            location = Location.objects.annotate(place_name_no_spaces=Replace('place_name', Value(' '), Value(''))).filter(place_name_no_spaces__icontains=place_name_for_search).first()
            if not location:
                return Response({"error": f"No location found for place_name '{place_name}'"}, status=status.HTTP_404_NOT_FOUND)
            address = location.address
            print(address)
            short_address = " ".join(address.split()[:2])
        except Exception as e:
            return Response({"error": f"Error retrieving address: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        nearby_places = []
        categories = ["식당", "관광지", "숙소"]
    
        for category in categories:
            query = f"{short_address} 근처 {category}"
            encText = urllib.parse.quote(query)
            url = f"https://openapi.naver.com/v1/search/local.json?query={encText}&display=5&start=1&sort=comment"
            
            try:
                req = urllib.request.Request(url)
                req.add_header("X-Naver-Client-Id", client_id)
                req.add_header("X-Naver-Client-Secret", client_secret)
                response = urllib.request.urlopen(req)
                rescode = response.getcode()
                
                if rescode == 200:
                    response_body = response.read()
                    result = json.loads(response_body)
                    if 'items' in result and result['items']:
                        for item in result['items']:
                            nearby_places.append({
                                "title": item['title'], # 업체명, 기관명
                                "link": item.get('link'), # 업체, 기관의 상세정보(URL)
                                "category": item.get('category'), # 업체, 기관의 분류 정보
                                "roadaddress": item.get('roadAddress'), # 도로명 주소
                                "address": item.get('address') # 지번 주소
                            })
                else:
                    return {"error": f"Error Code: {rescode}"}
                    
            except urllib.error.URLError as e:
                return {"error": f"Error occurred: {str(e)}"}
    
        return nearby_places


class AiPlanningAPIView(APIView):
        def get(self, request):
            return render(request, 'locations/plan.html')
        
        def post(self, request):
            llm = ChatOpenAI(model="gpt-4o-mini", api_key=settings.API_KEY)
            query_params = request.query_params
            place_name = query_params.get("place_name")
            n = query_params.get("n", 0)
            m = query_params.get("m", 1)
            preference = query_params.get("preference", None)

            if not place_name:
                return Response({"방문하고자 하는 촬영지를 입력해주세요. 해당 촬영지를 방문하는 여행 계획을 추천해드립니다."}, status=status.HTTP_200_OK)
            
            nearby_places = get_nearby_place(place_name)
            if isinstance(nearby_places, Response):
                return nearby_places 

            nearby_places_formatted = [
            f"제목: {place['title']}, 카테고리: {place['category']}, Link: {place['link']}, 도로명 주소: {place['roadaddress']}, 지번 주소: {place['address']}"
            for place in nearby_places
            ]
            nearby_places_str = "\n".join(nearby_places_formatted)

            template = f"""{place_name}에 방문하는 일정을 포함한 여행 계획을 세워줘. 나는 한국에 살고있어. 
                    반드시 {nearby_places_str} 중에서 장소를 추천해줘. 다음의 내용을 담아 계획을 세워줘.
                    매일의 일정: 오전, 오후, 저녁별로 어떤 활동을 할 지. 날짜 예시는 들지 않아도 돼.
                    매일 식사는 아침, 점심, 저녁을 먹을거야.
                    반드시 특정 식당, 장소명을 포함한 답변을 줘. 같은 장소를 두번 방문하지 않도록 해. 그리고 링크가 있다면 포함시켜줘."""
            
            if preference and len(preference)<=50:
                template += f"{preference}한 스타일의 여행을 원해."
                if n and m:  # n, m 입력 받음.
                    template += f"{n}박 {m}일 동안의 여행을 갈거야."
                else:  # n, m을 입력받지 않는 경우. (당일치기 여행계획 버튼을 따로 만들기.)
                    template += "당일치기 여행을 갈거야."
                    m = 1
            elif preference and len(preference)>50:  # 선호하는 여행 스타일은 50자 이내로 입력해야 함.
                return Response({"여행 취향을 50자 이내로 적어주세요."})
            else:
                if n and m: 
                    template += f"{n}박 {m}일 동안의 여행을 갈거야."
                else:
                    template += "당일치기 여행을 갈거야. 숙소는 추천하지 마."

            prompt = PromptTemplate(template=template, input_variables=["place_name", "preference", "nearby_places"])
            llm_chain = LLMChain(prompt=prompt, llm=llm)

            try:
                response = llm_chain.run(place_name=place_name, preference=preference, nearby_places=nearby_places)
                request.session['travel_plan'] = response  # Store the travel plan in the session
                return render(request, 'locations/plan.html', {"travel_plan": response})
                # return redirect(reverse('plan_result'))
            except Exception as e:
                return Response({"message": "죄송합니다. 여행플래닝 서비스 제공에 실패했습니다. 다시 시도해주세요.", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PlanResultView(APIView):
    def get(self, request):
        travel_plan = request.session.get('travel_plan')
        if travel_plan:
            return render(request, 'locations/plan_result.html', {"travel_plan": travel_plan})
        else:
            # return Response({"error": "No travel plan found"}, status=404)
            return render(request, 'locations/plan_result.html')
        

def location_detail(request, pk):
    # 촬영지 상세 정보를 가져와 템플릿에 렌더링
    location = get_object_or_404(Location, pk=pk)
    return render(request, 'locations/location_detail.html', {'location': location})


def index(request):
    latest_journals = Journal.objects.order_by('-created_at')[:3]  # 최신 저널 3개 가져오기
    popular_locations = Location.objects.order_by('-save_count')[:4]  # 인기 촬영지 3개 가져오기
    popular_community_posts = Community.objects.annotate(likes_count=Count('community_likes')).order_by('-likes_count')[:3]

    context = {
        'popular_locations': popular_locations,
        'latest_journals': latest_journals,
        'popular_community_posts': popular_community_posts,  # 인기 커뮤니티 글 추가
    }
    
    return render(request, 'journals/index.html', context)