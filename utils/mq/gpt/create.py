# -*- coding: utf-8 -*-
"""
    @Time：2023/8/20
    @Author：斑斑砖
    Description：
    创建消息队列
"""
from enums.const import MQEnum
from utils.mq.conn.conn import channel


# 声明一个队列
def init_create():
    channel.queue_declare(queue=MQEnum.GPT_QUEUE.value, durable=True)
