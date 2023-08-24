from rest_framework import serializers

from apps.chat.serializers.base import BaseMessageSerializers, BaseUserItemSerializer, BaseSerializer
from enums.message import MessageTypeEnum


class FileInfoSerializer(serializers.Serializer):
    """文件类型模型校验"""
    fileName = serializers.CharField(error_messages={
        'required': '文件名不能为空', 'null': '文件名不能为空', 'blank': '文件名不能为空'
    })
    fileSize = serializers.IntegerField(
        error_messages={'required': '文件大小不能为空', 'null': '文件大小不能为空', 'blank': '文件大小不能为空'}
    )
    filePath = serializers.CharField(
        error_messages={'required': '文件路径不能为空', 'null': '文件路径不能为空', 'blank': '文件路径不能为空'}
    )


class TextMessageSerializer(BaseMessageSerializers):
    """针对文本类型"""
    content = serializers.CharField(max_length=500, error_messages={
        'max_length': '发送的内容太长了',
        'invalid': '发送的内容太长了',
        'required': '发送的内容不能为空',
        'null': '发送的内容不能为空',
        'blank': '发送的内容不能为空'

    })


class FileMessageSerializer(BaseMessageSerializers):
    """针对文件类型"""
    fileInfo = FileInfoSerializer(error_messages=
                                  {'required': '文件信息不能为空', 'null': '文件信息不能为空',
                                   'blank': '文件信息不能为空'}
                                  )


class MessageWithReplaySerializer(serializers.Serializer):
    """回复"""
    type = serializers.IntegerField(error_messages={
        'required': '消息类型不能为空', 'null': '消息类型不能为空', 'blank': '消息类型不能为空'}

    )
    msgID = serializers.IntegerField(error_messages={
        "required": "消息ID不能为空", "null": "消息ID不能为空", "blank": "消息ID不能为空"
    })
    userID = serializers.IntegerField(error_messages={
        "required": "回复用户ID不能为空", "null": "回复用户ID不能为空", "blank": "回复用户ID不能为空"
    })
    username = serializers.CharField(error_messages={
        "required": "回复用户名不能为空", "null": "回复用户名不能为空", "blank": "回复用户名不能为空"
    })


class MessageSerializer(serializers.Serializer):
    def to_representation(self, instance):
        return None

    def valid_msg(self, tp, data):
        if tp == MessageTypeEnum.TEXT.value or tp == MessageTypeEnum.GPT.value:
            """文本类型"""
            serializer = TextMessageSerializer(data=data)
        elif tp == MessageTypeEnum.IMAGE.value or tp == MessageTypeEnum.FILE.value:
            """图片、文件类型"""
            serializer = FileMessageSerializer(data=data)
        else:
            raise serializers.ValidationError("Invalid message type")
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    def valid_replay(self, replay):
        """进行校验回复"""
        ser_obj = MessageWithReplaySerializer(data=replay)
        ser_obj.is_valid(raise_exception=True)
        return ser_obj.validated_data

    def to_internal_value(self, data):
        replay_obj = {}
        # 获取消息类型 文件、文本、图片、音频
        message_type = data.get('type')
        replay = data.get('replay')
        if replay:  # 存在replay
            replay_obj = self.valid_replay(replay)
        res = self.valid_msg(message_type, data)
        res.update(replay_obj)
        return res


class MessageRecordSerializer(BaseSerializer):
    """
    校验消息类型，包括回复消息
    """
    user = BaseUserItemSerializer(error_messages={
        'required': '用户ID不能为空', 'null': '用户ID不能为空', 'blank': '用户ID不能为空'}
    )
    message = MessageSerializer(
        error_messages={'required': '消息体不能为空', 'null': '消息体不能为空', 'blank': '消息体不能为空'}
    )
