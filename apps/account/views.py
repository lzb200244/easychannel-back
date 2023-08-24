import logging

import redis
from django.contrib.auth import authenticate
from django_redis import get_redis_connection
from rest_framework.exceptions import NotAuthenticated, AuthenticationFailed
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin, ListModelMixin

from apps.account.apps import AccountConfig
from apps.account.models import UserInfo, Medal
from apps.account.serializer import (AccountSerializers, UserInfoSerializers, MedalSerializers, LoginSerializers,
                                     JoinRoomSerializers)
from apps.chat.apps import ChatConfig
from apps.chat.models import GroupRoom
from consts.errors import ErrorMessageConst
from enums.const import UserEnum
from extensions.permissions.IsAuthenticated import CustomIsAuthenticated
from utils.response.response import APIResponse
from utils.tencent.cos import get_temp_avatar_credict

logger = logging.getLogger("account")
channel_conn: redis.Redis = get_redis_connection(ChatConfig.name)
account_conn: redis.Redis = get_redis_connection(AccountConfig.name)

class RegisterAPIView(CreateModelMixin, GenericAPIView):
    queryset = UserInfo.objects.all()
    serializer_class = AccountSerializers

    authentication_classes = []

    def post(self, request, *args, **kwargs):
        """用户注册"""
        return APIResponse(self.create(request).data)


class LoginAPIView(ListModelMixin, GenericAPIView):
    serializer_class = LoginSerializers
    queryset = UserInfo.objects.all()
    authentication_classes = []

    def get_serializer(self, *args, **kwargs):
        # 校验账号密码是否为空

        ser_obj = self.serializer_class(data=self.request.data)
        ser_obj.is_valid(raise_exception=True)
        user = authenticate(**ser_obj.validated_data)
        # 用户不存在，用户或密码错误
        if user is None:
            logger.warning(f"{ser_obj.validated_data['username']}：用户不存在或密码错误")
            raise AuthenticationFailed(ErrorMessageConst.USERNAME_OR_PASSWORD_ERROR.value)
        # 生成凭证

        return self.serializer_class(user, many=False)

    def post(self, request):
        """
        登录的接口
        :param request: username，password
        :return:
        """
        return APIResponse(self.list(request).data)


class ProfileUserInfoAPIView(ListModelMixin, UpdateModelMixin, GenericAPIView):
    serializer_class = UserInfoSerializers
    queryset = UserInfo.objects.all()
    permission_classes = [CustomIsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer(self, *args, **kwargs):
        if self.request.method == "GET":
            # 未认证的用户无法获取用户信息
            if self.request.user is None:
                raise NotAuthenticated(ErrorMessageConst.USER_NOT_LOGIN.value)
            return self.serializer_class(self.request.user, many=False, )
        return self.serializer_class(self.request.user, self.request.data, partial=True, many=False)

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return super().get_permissions()

    def put(self, request):
        """更新用户信息"""
        return APIResponse(self.update(request, partial=True).data)

    def get(self, request):
        """获取用户信息"""
        return APIResponse(self.list(request).data)


class UploadAvatarAPIView(GenericAPIView):
    permission_classes = [CustomIsAuthenticated]

    def get(self, request):
        """获取凭证"""
        return APIResponse(data=get_temp_avatar_credict())


class MedalsAPIView(ListModelMixin, GenericAPIView):
    serializer_class = MedalSerializers
    queryset = Medal.objects.all()
    permission_classes = [CustomIsAuthenticated]

    def get(self, request):
        return APIResponse(self.list(request).data)


class UserJoinRoomAPIView(GenericAPIView):
    serializer_class = JoinRoomSerializers

    def get_queryset(self):
        user_id = self.request.user.pk
        join_rooms = account_conn.smembers(UserEnum.JOIN_GROUP.value % user_id)
        return GroupRoom.objects.filter(id__in=join_rooms)

    def get(self, request, *args, **kwargs):
        """
        :return: 返回用户加入的群聊和私聊
        """
        if not self.request.user:
            raise NotAuthenticated(ErrorMessageConst.USER_NOT_LOGIN.value)
        queryset = self.get_queryset()
        serialized_data = self.serializer_class(queryset, many=True).data
        private_rooms = []
        group_rooms = []
        for room_data in serialized_data:
            if room_data['type'] == 1:  # 私聊类型
                private_rooms.append(room_data)
            elif room_data['type'] == 2:  # 群聊类型
                group_rooms.append(room_data)
        data = {
            'private_rooms': private_rooms,
            'group_rooms': group_rooms
        }

        return APIResponse(data)
