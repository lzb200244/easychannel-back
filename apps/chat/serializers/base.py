import logging

import redis
from django_redis import get_redis_connection
from rest_framework import serializers
from enums.const import UserEnum
from enums.message import PushTypeEnum

account_conn: redis.Redis = get_redis_connection('account')
account_logger = logging.getLogger('account')


class BaseMessageSerializers(serializers.Serializer):
    """消息体"""
    type = serializers.IntegerField(required=True,
                                    error_messages={'required': '消息体类型不能为空', 'null': '消息体类型不能为空',
                                                    'blank': '消息体类型不能为空'})


class BaseUserItemSerializer(serializers.Serializer):
    userID = serializers.IntegerField(error_messages={'required': '用户ID不能为空', 'null': '用户ID不能为空', 'blank': '用户ID不能为空'})


class EnumField(serializers.Field):
    """对消息类型进行校验"""

    def __init__(self, enum_type, **kwargs):
        self.enum_type = enum_type
        super().__init__(**kwargs)

    def to_representation(self, value):
        return value.name

    def to_internal_value(self, data):
        if data not in self.enum_type.__members__.values():
            raise serializers.ValidationError("无效的消息类型")
        return self.enum_type(data)  # 返回PushTypeEnum实例


class BaseSerializer(serializers.Serializer):
    """
    校验消息类型，
    """
    type = EnumField(enum_type=PushTypeEnum,
                     error_messages={'required': '消息类型不能为空',
                                     'null': '消息类型不能为空', 'blank': '消息类型不能为空'})
    roomID = serializers.IntegerField(
        required=True,
        error_messages={'required': '房间ID不能为空', 'null': '房间ID不能为空', 'blank': '房间ID不能为空'})

    def validate_roomID(self, obj):
        """
        校验用户是否在这个房间，且房间存在
        :param obj:
        :return:
        """
        user = self.context['request'].user
        if not account_conn.sismember(UserEnum.JOIN_ROOM.value % user.pk, obj):
            # 记录日志
            info = f"用户{user.pk}并不在{obj}房间"
            account_logger.info(info)
            raise serializers.ValidationError(info)
        return obj
