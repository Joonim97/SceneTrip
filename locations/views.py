from django.shortcuts import render
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from urllib.parse import urlencode
import requests


class OpenApiView(APIView):
    def get(self, request, *args, **kwargs):
        base_url = f'https://api.odcloud.kr/api/15111405/v1/uddi:d8741b9c-f484-4ea8-8f54-bd21ab62de14'
        
        params = {
            "page": 'int',  # 페이지 인덱스
            "perPage": 'int',  # 세션당 요청레코드수
            "returnType": "JSON",
        }
        query_string = urlencode(params)

        full_url = f"{base_url}?{query_string}&serviceKey={settings.SERVICE_KEY}"

        response = requests.get(full_url)
        return Response(response.json(), status=200)


class LocationListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        base_url = f'https://api.odcloud.kr/api/15111405/v1/uddi:d8741b9c-f484-4ea8-8f54-bd21ab62de14'
        
        params = {
            "page": 1,  # 페이지 인덱스
            "perPage": 10,  # 세션당 요청레코드수
            "returnType": "JSON",
        }
        query_string = urlencode(params)

        full_url = f"{base_url}?{query_string}&serviceKey={settings.SERVICE_KEY}"

        response = requests.get(full_url)
        return Response(response.json(), status=200)
        

class LocationSearchAPIView(APIView):
    def get(self, request, *args, **kwargs):
        base_url = f'https://api.odcloud.kr/api/15111405/v1/uddi:d8741b9c-f484-4ea8-8f54-bd21ab62de14'
        keyword = request.query_params.get('keyword', '').lower()

        params = {
            "page": request.query_params.get('page', 1),  # 페이지 인덱스
            "perPage": 10,  # 세션당 요청레코드수
            "returnType": "JSON",
        }
        query_string = urlencode(params)

        full_url = f"{base_url}?{query_string}&serviceKey={settings.SERVICE_KEY}"

        response = requests.get(full_url)

        if response.status_code == 200:
            data = response.json()
            filtered_data = [item for item in data.get('data', []) if keyword in item.get('제목', '').lower()]
            return Response(filtered_data, status=200)
        else:
            return Response({"error": "Failed to fetch data from API"}, status=response.status_code)