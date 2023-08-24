from rest_framework import serializers

from apps.chat.serializers.base import BaseSerializer


class RecallItemSerializers(serializers.Serializer):
    """消息体"""
    type = serializers.IntegerField(
        error_messages={'required': '消息体类型不能为空', 'null': '消息体类型不能为空', 'blank': '消息体类型不能为空'})
    msgID = serializers.IntegerField(
        error_messages={'required': '消息ID不能为空', 'null': '消息ID不能为空', 'blank': '消息ID不能为空'})


class RecallSerializers(BaseSerializer):
    """
    校验撤回类型。
    """
    message = RecallItemSerializers(
        error_messages={'required': '撤回消息体不能为空', 'null': '撤回消息体不能为空', 'blank': '撤回消息体不能为空'})
