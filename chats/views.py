from rest_framework import generics, serializers, status
from rest_framework.response import Response
from .models import ChatRoom, Message, ShopUser, VisitorUser
from .serializers import ChatRoomSerializer, MessageSerializer
from rest_framework.exceptions import ValidationError
from django.http import Http404
from rest_framework.permissions import IsAuthenticated

# 사용자 정의 예외 클래스
class ImmediateResponseException(Exception):
    def __init__(self, response):
        self.response = response

# 채팅방 목록 조회 및 생성을 위한 뷰 클래스
class ChatRoomListCreateView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatRoomSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request  # request 객체를 컨텍스트에 추가
        return context

    def get(self, request):
        user_email = request.query_params.get('email', None)
        if not user_email:
            raise ValidationError('Email 파라미터가 필요합니다.')

        chat_rooms = ChatRoom.objects.filter(
            shop_user__shop_user_email=user_email
        ) | ChatRoom.objects.filter(
            visitor_user__visitor_user_email=user_email
        )

        serializer = self.get_serializer(chat_rooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        shop_user_email = request.data.get('shop_user_email')
        visitor_user_email = request.data.get('visitor_user_email')

        shop_user, _ = ShopUser.objects.get_or_create(shop_user_email=shop_user_email)
        visitor_user, _ = VisitorUser.objects.get_or_create(visitor_user_email=visitor_user_email)

        existing_chatroom = ChatRoom.objects.filter(
            shop_user=shop_user,
            visitor_user=visitor_user
        ).first()

        if existing_chatroom:
            existing_serializer = ChatRoomSerializer(existing_chatroom, context=self.get_serializer_context())
            return Response(existing_serializer.data, status=status.HTTP_200_OK)

        serializer.save(shop_user=shop_user, visitor_user=visitor_user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# 특정 채팅방의 메시지 목록을 조회하고 메시지를 생성하는 뷰 클래스
class MessageListCreateView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request  # request 객체를 컨텍스트에 추가
        return context

    def get(self, request, id):
        queryset = Message.objects.filter(room_id=id)
        if not queryset.exists():
            raise Http404('해당 room_id로 메시지를 찾을 수 없습니다.')

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, id):
        room = ChatRoom.objects.filter(id=id).first()
        if not room:
            raise ValidationError('해당 room_id에 대한 채팅방이 존재하지 않습니다.')

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(room=room, sender_email=request.user.email)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
