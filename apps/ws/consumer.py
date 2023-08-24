import logging

import redis
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django_redis import get_redis_connection

from apps.account.models import UserInfo
from enums.const import ChannelRoomEnum, UserEnum
from apps.chat.typesd.base import BaseRecord
from apps.chat.typesd.push import PushType
from enums.message import PushTypeEnum

channel_conn: redis.Redis = get_redis_connection('channel')
account_conn: redis.Redis = get_redis_connection('account')
logger = logging.getLogger('chat')


class ChatConsumer(AsyncJsonWebsocketConsumer):

    @property
    def get_group(self):
        group: str = self.scope['url_route']['kwargs'].get('group')
        if group and group.isdigit():
            return int(group)
        return 1

    @property
    def user(self) -> UserInfo:
        return self.scope['user']

    async def send_private_message(self, user_channel_name, message):
        channel_layer = self.channel_layer
        await channel_layer.send(user_channel_name, message)

    async def connect(self):
        await self.accept()

        # 2. 加入群聊
        room = ChannelRoomEnum.ROOM.value % self.get_group
        await self.channel_layer.group_add(room, self.channel_name)
        # 1.判断是否存在该群聊
        if not channel_conn.sismember(ChannelRoomEnum.ROOMS.value, self.get_group):
            await self.close()
            return
        # 2.用户是否在群聊里
        if self.user:
            if not account_conn.sismember(UserEnum.JOIN_ROOM.value % self.user.pk, self.get_group):
                await self.close()
                return
            # 4. 放入redis实现当前群聊的在线情况=》set
            self.add_user_to_status()
            # 5. 上线推送
            await self.push(PushTypeEnum.ONLINE_PUSH)
        else:
            if self.get_group != ChannelRoomEnum.DEFAULT_ROOM.value:
                await self.close()
                return

    async def disconnect(self, code):
        room = ChannelRoomEnum.ROOM.value % self.get_group
        # 退出群聊
        await self.channel_layer.group_discard(room, self.channel_name)

        # 下线推送
        if self.user:
            # 退出房间
            self.remove_user_from_status()
            await self.push(PushTypeEnum.LEVEL_PUSH)

    async def handle_message(self, event):

        text: BaseRecord = event['text']
        await self.send_json(text)

    def add_user_to_status(self):
        """
        房间状态统计
        :return:
        """
        # 当前在线人数
        channel_conn.sadd(ChannelRoomEnum.ROOM_ONLINE_MEMBERS.value % self.get_group, self.user.pk)

        channel_conn.sadd(ChannelRoomEnum.ROOM_ONLINE_MEMBERS.value % self.get_group, self.user.pk)
        # 添加到集合历史人数
        channel_conn.sadd(ChannelRoomEnum.ROOM_MEMBERS.value % self.get_group, self.user.pk)

    def remove_user_from_status(self):
        """在线人数-1"""
        channel_conn.srem(ChannelRoomEnum.ROOM_ONLINE_MEMBERS.value % self.get_group, self.user.pk)

    async def push(self, tp: PushTypeEnum):
        """
        加入群聊消息推送
        :param tp: 消息类型
        :return:
        """
        # 3. 上下线推送
        pushMessage: PushType = {'type': tp,
                                 'roomID': self.get_group,
                                 'user': {'userID': self.user.pk, 'username': self.user.name,
                                          'avatar': self.user.avatar, 'isActive': True, }}  # 当前状态改为True
        room = ChannelRoomEnum.ROOM.value % self.get_group
        await self.channel_layer.group_send(
            room,
            {
                'type': 'handle.message',
                'text': pushMessage,
            }
        )
