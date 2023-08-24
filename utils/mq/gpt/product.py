# -*- coding: utf-8 -*-
"""
    @Time：2023/8/20
    @Author：斑斑砖
    Description：
        生产者 处理gpt任务
"""
import json
import logging
from typing import TypedDict, Union

import pika

from enums.const import MQEnum
from utils.mq.conn.conn import channel

QUEUE_NAME = 'gpt'
logger = logging.getLogger('chat')


class GPTReplay(TypedDict):
    type: int
    roomID: int
    content: str
    username: str
    userID: int
    msgID: int
    mul: bool
    question: Union[str, None]


def send_message(message: GPTReplay):
    try:

        # 发布持久性消息
        properties = pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent)  # 设置消息持久性
        channel.basic_publish(
            exchange=MQEnum.GPT_EXCHANGE.value,
            routing_key=MQEnum.GPT_QUEUE.value,
            body=json.dumps(message),
            properties=properties
        )
    except Exception as e:
        # rabbitmq 消息发送失败
        logger.warning(f'消息发送失败：{e}')
