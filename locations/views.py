from django.shortcuts import render
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from urllib.parse import urlencode
from requests.exceptions import RequestException
import requests



class OpenApiView(APIView):
    def get(self, request, *args, **kwargs):
        base_url = f"https://api.odcloud.kr/api/15111405/v1/uddi:d8741b9c-f484-4ea8-8f54-bd21ab62de14"

        params = {
            "page": "int",  # 페이지 인덱스
            "perPage": "int",  # 세션당 요청레코드수
            "returnType": "JSON",
        }
        query_string = urlencode(params)

        full_url = f"{base_url}?{query_string}&serviceKey={settings.SERVICE_KEY}"

        response = requests.get(full_url)
        return Response(response.json(), status=status.HTTP_200_OK)


class LocationListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        base_url = f"https://api.odcloud.kr/api/15111405/v1/uddi:d8741b9c-f484-4ea8-8f54-bd21ab62de14"

        page = request.query_params.get("page")
        perPage = request.query_params.get("perPage")

        params = {
            "page": page,  # 페이지 인덱스
            "perPage": perPage,  # 세션당 요청레코드수
            "returnType": "JSON",
        }
        query_string = urlencode(params)

        full_url = f"{base_url}?{query_string}&serviceKey={settings.SERVICE_KEY}"

        response = requests.get(full_url)
        return Response(response.json(), status=status.HTTP_200_OK)


class LocationSearchAPIView(APIView):
    def get(self, request, *args, **kwargs):
        base_url = "https://api.odcloud.kr/api/15111405/v1/uddi:d8741b9c-f484-4ea8-8f54-bd21ab62de14"
        service_key = settings.SERVICE_KEY

        page = 1
        per_page = 1000  # 한 번에 1000개씩 요청
        keyword = request.query_params.get("keyword", "").lower()

        all_data = []

        while True:
            params = {
                "page": page,
                "perPage": per_page,
                "returnType": "JSON",
            }
            query_string = urlencode(params)
            full_url = f"{base_url}?{query_string}&serviceKey={service_key}"

            try:
                response = requests.get(full_url, timeout=10)  # 10초 타임아웃 설정
                response.raise_for_status()  # HTTP 에러 발생 시 예외 발생
                data = response.json()
            except RequestException as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            if not data['data']:
                break

            all_data.extend(data['data'])
            page += 1

        # Filter the data based on the keyword
        if keyword:
            filtered_data = [
                item for item in all_data 
                if keyword in item['제목'].lower() 
                or keyword in item['장소설명'].lower()
                or keyword in item['장소명'].lower()
                or keyword in item['미디어타입'].lower()
                or keyword in item['장소타입'].lower()
                or keyword in item['주소'].lower()
            ]
        else:
            filtered_data = all_data

        return Response(filtered_data)
