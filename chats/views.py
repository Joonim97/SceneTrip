from django.shortcuts import render, redirect
from django.http import JsonResponse

def index(request):
    if request.method == 'POST':
        return redirect('index')
    else:
        # GET 요청 처리
        return render(request, 'chat/index.html')

def room(request, room_name):
    if request.method == 'POST':
        return JsonResponse({'status': 'Message sent', 'room_name': room_name})  # 예시
    else:
        # GET 요청 처리
        return render(request, 'chat/room.html', {
            'room_name': room_name
        })
