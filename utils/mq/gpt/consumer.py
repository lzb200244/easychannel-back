# -*- coding: utf-8 -*-
"""
    @Time：2023/8/20
    @Author：斑斑砖
    Description：
        后台进行消费gpt，返回到对应房间
"""

import json
import logging

import redis

from django_redis import get_redis_connection

from apps.chat.apps import ChatConfig
from apps.chat.models import GroupRecords
from enums.const import UserEnum, Room2GroupEnum, MQEnum
from enums.message import MessageTypeEnum, PushTypeEnum
from utils.broadcast.main import broadcast
from utils.gpt.single import GPT
from utils.mq.conn.conn import channel
from utils.mq.gpt.product import GPTReplay
from utils.mq.tasks.base import BackgroundTask, RegisterTask

channel_conn: redis.Redis = get_redis_connection(ChatConfig.name)

logger = logging.getLogger('chat')


def callback(ch, method, properties, body: bytes):
    try:
        message: GPTReplay = json.loads(body.decode('utf-8'))
        print(message)
        # 多轮调用
        if message['mul']:
            results = GPT.chat_mul(message['content'], message['question'])
        # 单轮调用
        else:
            # 1. 调用gpt
            results = GPT.chat(message['content'])
        # 2. 存储到mysql
        msgObj = GroupRecords.objects.create(
            type=MessageTypeEnum.TEXT.value,
            content=results.get('result'),
            user_id=UserEnum.GPT_ID.value,
            room_id=message.get('roomID'),
            replay_id=message.get('msgID')  # 回复的消息
        )
        # 3. 构建存储到redis
        content = {
            "type": PushTypeEnum.REPLAY_PUSH.value,
            "user": {
                "userID": UserEnum.GPT_ID.value
            },
            "roomID": message.get('roomID'),
            "message": {
                "content": results.get('result'),
                "time": msgObj.create_time.timestamp() * 1000,
                "msgID": msgObj.pk,
                "type": MessageTypeEnum.GPT.value,
                "messageStatus": {
                    "likes": 0,
                    "drop": "",
                    'members': [],
                    "isDrop": False
                },
                "replay": {
                    "type": MessageTypeEnum.TEXT.value,
                    "content": message.get('content'),
                    "userID": message.get('userID'),
                    "username": message.get('username'),
                }
            }
        }
        # 存储到redis
        key = Room2GroupEnum.ROOM_RECORDS.value % message.get('roomID')
        value = json.dumps(content)
        channel_conn.eval(Room2GroupEnum.APPEND_POP_LUA.value, 1, key, Room2GroupEnum.ROOM_RECORD_MAX.value, value)
        # 4. 进行广播
        room = Room2GroupEnum.ROOM.value % message.get('roomID')

        broadcast(room, content)
        # 5. 手动回复ack
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        logger.warning(f'处理后台任务失败：{e}')


class ConsumerGpt(BackgroundTask):
    title = "ai助手"

    def task_logic(self):

        try:
            # 告诉RabbitMQ调用callback函数来处理接收到的消息
            channel.basic_consume(queue=MQEnum.GPT_QUEUE.value, on_message_callback=callback, auto_ack=False)
            channel.start_consuming()
        except Exception as e:
            print("Error:", e)


register = RegisterTask()
