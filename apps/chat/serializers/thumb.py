from rest_framework import serializers

from apps.chat.serializers.base import BaseSerializer


class ThumbMessageSerializers(serializers.Serializer):
    msgID = serializers.IntegerField(
        error_messages={'required': '消息ID不能为空', 'null': '消息ID不能为空', 'blank': '消息ID不能为空'})



class ThumbSerializers(BaseSerializer):
    message = ThumbMessageSerializers(
        error_messages={'required': '点赞消息不能为空', 'null': '点赞消息不能为空', 'blank': '点赞消息不能为空'})
