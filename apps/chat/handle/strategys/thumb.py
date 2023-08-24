import time
from typing import Union, NoReturn

import redis
from django.db.models import F
from django_redis import get_redis_connection

from apps.account.models import UserInfo
from apps.chat.apps import ChatConfig
from apps.chat.models import GroupRecords
from apps.chat.typesd.base import BaseRecord
from apps.chat.typesd.request.thumb import ThumbType, ThumbItem
from enums.const import Record2GroupEnum, UserEnum, MedalEnum
from apps.chat.handle.strategy import Strategy

channel_conn: redis.Redis = get_redis_connection(ChatConfig.name)
class ThumbStrategy(Strategy):
    """点赞策略"""

    # 对应的码

    def execute(self, user: UserInfo, content: BaseRecord):
        room_id = content['roomID']
        self.save_text_to_mysql(room_id, user, content)
        # 存储到redis
        self.save_to_redis(room_id, user, content)
        return content

    def save_text_to_mysql(self, group: Union[int, str], user: UserInfo, content: BaseRecord):
        """
        保存到数据库
        """
        # 1. 该条消息记录进行+1操作
        # print(message['msgID'])
        message = content['message']
        GroupRecords.objects.filter(pk=message['msgID']).update(likes=F('likes') + 1)

    def save_to_redis(self, group: Union[int, str], user: UserInfo,
                      content: BaseRecord) -> NoReturn:
        """
        保存到redis,该条记录进行记录该用户是否点赞过

        """
        message = content['message']
        key = Record2GroupEnum.RECORD_LIKES.value % message['msgID']

        has_liked = channel_conn.zscore(key, user.pk)
        # 点赞
        if not has_liked:
            current_time = int(time.time() * 1000)
            channel_conn.zadd(key, {user.pk: current_time})
            # 更新用户的活跃状态
            key = UserEnum.USER_CHAT_STATUS.value % user.pk
            self.conn.hincrby(key, MedalEnum.THUMB.value, 1)
        # 取消
        else:
            channel_conn.zrem(key, user.pk)
