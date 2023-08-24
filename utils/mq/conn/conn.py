# -*- coding: utf-8 -*-
"""
    @Time：2023/8/20
    @Author：斑斑砖
    Description：
        连接到远程RabbitMQ服务器
        单例对象
"""
import os

import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import AMQPConnectionError


class RabbitMQSingleton:
    _instance, connection, channel = None, None, None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(RabbitMQSingleton, cls).__new__(cls, *args, **kwargs)

            cls._instance.init_connection()
        return cls._instance

    def init_connection(self):
        try:
            # 1. 构造连接property
            credentials = pika.PlainCredentials(os.getenv("RABBITMQ_DEFAULT_USER"), os.getenv("RABBITMQ_DEFAULT_PASS"))
            # 2. 获取mq连接
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    os.getenv("RABBITMQ_DEFAULT_HOST", "127.0.0.1"),
                    os.getenv("RABBITMQ_DEFAULT_PORT", 5672),
                    virtual_host=os.getenv("RABBITMQ_DEFAULT_VHOST", "/"),
                    credentials=credentials
                )
            )
            self.channel = self.connection.channel()
        except AMQPConnectionError as e:
            raise Exception("rabbitmq连接失败", e)

    def get_channel(self) -> BlockingChannel:
        return self.channel


channel = RabbitMQSingleton().get_channel()
if __name__ == '__main__':
    channel = RabbitMQSingleton().get_channel()
