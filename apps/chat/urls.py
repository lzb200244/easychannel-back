from django.urls import path

from apps.chat.views import (
    RecordAPIView, OnlineAPIView, UploadFileAPIView, ReceiveMessageAPIView, RecallMessageAPIView, ThumbMessageAPIView,
    ChatRoomAPIView, JoinRoomAPIView
)

urlpatterns = [
    path('msg/', ReceiveMessageAPIView.as_view()),
    path('record/', RecordAPIView.as_view()),
    path('online/', OnlineAPIView.as_view()),
    path('file/', UploadFileAPIView.as_view()),
    path('recall/', RecallMessageAPIView.as_view()),
    path('thumb/', ThumbMessageAPIView.as_view()),
    path('room/', ChatRoomAPIView.as_view()),
    path('join/', JoinRoomAPIView.as_view()),
]
