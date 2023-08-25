import json
import logging

import redis
from typing import Optional
from django_redis import get_redis_connection
from rest_framework.exceptions import NotFound, NotAuthenticated
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin, CreateModelMixin

from apps.account.apps import AccountConfig
from apps.account.models import UserInfo
from apps.chat.apps import ChatConfig
from apps.chat.ser import RecordSerializers, CreateChatRoomSerializers, OnlineSerializers, JoinChatRoomSerializers, \
    ValidRoomSerializers
from apps.chat.serializers.message import MessageRecordSerializer
from apps.chat.serializers.recall import RecallSerializers
from apps.chat.serializers.thumb import ThumbSerializers
from apps.chat.handle.register import handler
from apps.chat.models import GroupRecords, GroupRoom
from apps.chat.typesd.base import BaseRecord, BaseMessage
from consts.errors import ErrorMessageConst
from enums.message import PushTypeEnum
from enums.const import Room2GroupEnum, UserEnum, Record2GroupEnum
from extensions.permissions.IsAuthenticated import CustomIsAuthenticated
from utils.broadcast.main import broadcast
from utils.pagination.pg import RecordPager
from utils.response.response import APIResponse
from utils.tencent.cos import get_temp_credict

channel_conn: redis.Redis = get_redis_connection(ChatConfig.name)
account_conn: redis.Redis = get_redis_connection(AccountConfig.name)

logger = logging.getLogger('chat')


class RecordAPIView(ListModelMixin, GenericAPIView):
    """获取某个房间的聊天记录"""
    serializer_class = RecordSerializers
    queryset = GroupRecords.objects.all()
    pagination_class = RecordPager

    def __init__(self, *args, **kwargs):
        self.room_key = None
        super().__init__(*args, **kwargs)

    def get_page_range(self, page: int) -> Optional[list]:
        """
        判断是从reids读取还是mysql
        :param page:
        :return:
        """
        if page * self.pagination_class.page_size > Room2GroupEnum.ROOM_RECORD_MAX.value:
            return None
        else:
            return [(page - 1) * RecordPager.page_size, page * RecordPager.page_size - 1]

    def get(self, request):
        """
        返回某个房间的聊天记录，进行分页拿取
            0-1000条往redis拿
            1000后往mysql进行加载，
        """

        # 参数校验
        ser = ValidRoomSerializers(data=self.request.GET, context={'request': self.request})
        ser.is_valid(raise_exception=True)
        room = ser.validated_data.get('room')
        page = ser.validated_data.get('page')
        page_range = self.get_page_range(page)
        room_key = Room2GroupEnum.ROOM_RECORDS.value % room
        self.room_key = room_key
        # 在redis查询范围内
        if page_range:
            # 存在用户对象
            if page_range[0] > channel_conn.llen(room_key) and channel_conn.llen(room_key) < page_range[1]:
                return NotFound(ErrorMessageConst.PAGE_NOT_EXIST.value)
            record_list = channel_conn.lrange(room_key, *page_range)
            redis_data = []
            for item in record_list:
                dump_item: BaseRecord = json.loads(item)
                record_key = Record2GroupEnum.RECORD_LIKES.value % dump_item['message']['msgID']
                # 1. 点赞数量
                like_num = channel_conn.zcount(record_key, 0, "+inf")
                # 2. 点赞的人员
                like_members = list(map(int, channel_conn.zrange(record_key, 0, -1)))
                # 3. 构建
                dump_item['message']['messageStatus']['likes'] = like_num
                dump_item['message']['messageStatus']['members'] = like_members
                redis_data.append(dump_item)
            d = {'count': channel_conn.llen(room_key), 'results': redis_data}
        else:
            request.GET._mutable = True
            # 重新计算页码
            request.GET['page'] = page - Room2GroupEnum.ROOM_RECORD_MAX.value / RecordPager.page_size
            logger.info("往mysql读取数据一次")
            d = self.list(request).data
        return APIResponse(d)

    def get_queryset(self):
        """
        redis读完读到低了，往sql读历史记录，sql没有才真正没有
        获取redis队头的msgID，为过滤mysql过滤条件，小于的就是历史记录

        :return:
        """
        # 1. 获取队头（最早加入的元素，处于最顶的
        top = channel_conn.lindex(self.room_key, -1)
        if top is None:
            # redis并没有数据,说明用户是非法的操作,读取了最大的页码,且是当该聊天群根本没有记录的时候
            # 非法操作
            raise NotFound(ErrorMessageConst.PAGE_NOT_EXIST.value)
        j_top: BaseRecord = json.loads(top)
        message: BaseMessage = j_top['message']

        # 2. 返回历史记录
        query = self.queryset.filter(
            id__lt=message['msgID'],
            room__id=j_top['roomID']
        ).order_by('-pk')

        return query


class OnlineAPIView(ListModelMixin, GenericAPIView):
    """获取群聊在线人数情况"""
    serializer_class = OnlineSerializers

    def get(self, request):
        online_user = []  # 在线
        offline_user = []  # 离线

        data = self.list(request).data

        for item in data:
            if item['user']['isActive']:
                online_user.append(item)
            else:
                offline_user.append(item)

        return APIResponse({
            'online': online_user,
            'offline': offline_user
        })

    def get_queryset(self):
        ser = ValidRoomSerializers(
            data=self.request.GET,
            context={'request': self.request}
        )
        ser.is_valid(raise_exception=True)
        room_id = ser.validated_data.get('room')
        member_key = Room2GroupEnum.ROOM_MEMBERS.value % room_id
        all_members = channel_conn.smembers(member_key)
        return UserInfo.objects.filter(id__in=all_members)

    def get_serializer_context(self):
        room_id = self.request.GET.get("room")
        online_key = Room2GroupEnum.ROOM_ONLINE_MEMBERS.value % room_id
        online_members = channel_conn.smembers(online_key)
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'online_members': online_members,
            'view': self
        }


class UploadFileAPIView(GenericAPIView):
    # permission_classes = [CustomIsAuthenticated]

    def get(self, request):
        policy = request.GET.get("policy")
        return APIResponse(data=get_temp_credict(policy))


class ReceiveMessageAPIView(GenericAPIView):
    """
        发送消息
        代替websocket减少负担，同时对消息的校验与过滤
    """

    permission_classes = [CustomIsAuthenticated]
    serializer_class = MessageRecordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        # 1. 调用is_valid()进行校验
        serializer.is_valid(raise_exception=True)
        # 2. 校验通过，可以在这里进行其他逻辑操作
        validated = serializer.validated_data
        cont = handler.handle_message(int(validated['type']), request.user, request.data)
        # 3. 派发给群内所有人（广播
        broadcast(Room2GroupEnum.ROOM.value % validated['roomID'], cont)

        return APIResponse(cont)


class ChatRoomAPIView(CreateModelMixin, ListModelMixin, GenericAPIView):
    """创建群聊/获取群聊"""
    serializer_class = CreateChatRoomSerializers
    queryset = GroupRoom.objects.all()
    permission_classes = [CustomIsAuthenticated]

    def post(self, request):
        return APIResponse(self.create(request).data)

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return super().get_permissions()

    def get_serializer(self, *args, **kwargs):
        if self.request.method == "POST":
            return self.serializer_class(data=self.request.data, context={"request": self.request})
        elif self.request.method == "GET":
            ser = ValidRoomSerializers(data=self.request.GET, context={'request': self.request})
            ser.is_valid(raise_exception=True)
            query = self.queryset.get(pk=ser.validated_data.get('room'))
            return self.serializer_class(query, many=False)

    def get(self, request):
        return APIResponse(self.list(request).data)


class JoinRoomAPIView(CreateModelMixin, ListModelMixin, GenericAPIView):
    """加入群聊/获取我加入的群聊"""
    serializer_class = JoinChatRoomSerializers
    queryset = GroupRoom.objects.all()
    permission_classes = [CustomIsAuthenticated]
    pagination_class = RecordPager

    def get_queryset(self):
        # 返回用户未加入的群，且群类型是群聊
        all_room = channel_conn.smembers(Room2GroupEnum.ROOMS.value)
        user_join_room = account_conn.smembers(UserEnum.JOIN_GROUP.value % self.request.user.pk)
        # 获取差集
        diff = set(all_room).difference(user_join_room)

        return self.queryset.filter(id__in=diff, type=2)

    def get(self, request):
        if not self.request.user:
            raise NotAuthenticated(ErrorMessageConst.USER_NOT_LOGIN.value)
        return APIResponse(self.list(request).data)

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return super().get_permissions()

    def post(self, request):
        return APIResponse(self.create(request).data)


class RecallMessageAPIView(GenericAPIView):
    """消息撤回"""
    permission_classes = [CustomIsAuthenticated]
    serializer_class = RecallSerializers

    def post(self, request):
        ser_obj = self.serializer_class(data=request.data, context={'request': request})
        ser_obj.is_valid(raise_exception=True)
        validate = ser_obj.validated_data
        cont = handler.handle_message(PushTypeEnum.RECALL_PUSH, request.user, request.data)
        broadcast(Room2GroupEnum.ROOM.value % validate['roomID'], cont)
        return APIResponse('ok')


class ThumbMessageAPIView(GenericAPIView):
    """处理用户点赞与踩"""
    permission_classes = [CustomIsAuthenticated]
    serializer_class = ThumbSerializers

    def post(self, request):
        ser_obj = self.serializer_class(data=request.data, context={'request': request})
        ser_obj.is_valid(raise_exception=True)
        validated = ser_obj.validated_data
        handler.handle_message(PushTypeEnum.THUMB_PUSH, request.user, validated)
        # 不进行推送
        # broadcast(Room2GroupEnum.ROOM.value % validated["roomID"], ser_obj.validated_data)

        return APIResponse('ok')
