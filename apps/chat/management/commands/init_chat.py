# -*- coding: utf-8 -*-
"""
    @Time：2023/8/20
    @Author：斑斑砖
    Description：
        初始化chat和敏感词
"""
import logging

import redis
from django.core.management import BaseCommand
from django_redis import get_redis_connection

from apps.account.apps import AccountConfig
from apps.account.models import UserInfo
from apps.chat.apps import ChatConfig
from apps.chat.models import GroupRoom, Sensitive
from enums.const import UserEnum, Room2GroupEnum
from utils.mq.gpt.create import init_create
from utils.sensitive.tree_plus.prefix import Tree

logger = logging.getLogger('account')
channel_conn: redis.Redis = get_redis_connection(ChatConfig.name)
account_conn: redis.Redis = get_redis_connection(AccountConfig.name)


class Command(BaseCommand):
    # 帮助文本, 一般备注命令的用途及如何使用。
    help = 'init ai'

    # 核心业务逻辑
    def handle(self, *args, **options):

        # 1. 初始化房间
        if not GroupRoom.objects.filter(id=1).exists():
            instance = GroupRoom.objects.create(
                id=1,
                name='畅聊',
                desc='一起来聊天吧！！！',
                type=2,
                isPublic=True,
                creator=UserInfo.objects.get(username='admin'),
            )

            # 1. 群聊进行注册
            channel_conn.sadd(Room2GroupEnum.ROOMS.value, instance.pk)
            # 2. 创建者加入自己创建的群聊
            channel_conn.sadd(Room2GroupEnum.ROOM_MEMBERS.value % instance.pk, instance.creator_id)
            account_conn.sadd(UserEnum.JOIN_GROUP.value % instance.creator_id, instance.pk)
            # 智能ai加入群聊
            channel_conn.sadd(Room2GroupEnum.ROOM_MEMBERS.value % instance.pk, UserEnum.GPT_ID.value)
            channel_conn.sadd(Room2GroupEnum.ROOM_ONLINE_MEMBERS.value % instance.pk, UserEnum.GPT_ID.value)

        # 2.进行构建敏感词前缀树
        tree_prefix = Tree(Sensitive)
        sensitive_words = []
        with open(r"sensitives.txt", "r", encoding="utf-8") as f:
            for line in f:
                sensitive_words.append(line.strip())
        tree_prefix.write_sensitive_to_mysql(sensitive_words)

        # 3. 初始化mq
        init_create()
