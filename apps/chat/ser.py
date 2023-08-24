import redis
from django_redis import get_redis_connection
from rest_framework import serializers

from apps.account.models import UserInfo
from enums.const import ChannelRoomEnum, UserEnum
from apps.chat.models import Record, Room
from enums.message import PushTypeEnum, MessageTypeEnum

channel_conn: redis.Redis = get_redis_connection('channel')
account_conn: redis.Redis = get_redis_connection('account')


class RecordUserSerializers(serializers.ModelSerializer):
    userID = serializers.SerializerMethodField()

    class Meta:
        model = UserInfo
        fields = ['userID']

    def get_userID(self, obj):
        return obj.pk


class RecordSerializers(serializers.ModelSerializer):
    message = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    user = RecordUserSerializers()  # 嵌套的子序列化器

    class Meta:
        model = Record
        fields = ['message', 'user', 'type']

    def get_type(self, obj):
        """消息类型"""
        return PushTypeEnum.MESSAGE_PUSH

    def base_message(self, obj):
        baseMsg = {
            'type': obj.type,
            'time': int(obj.create_time.timestamp() * 1000),
            'msgID': obj.pk,
            "messageStatus": {
                'isDrop': obj.isDrop,
                'drop': obj.drop,
                'likes': obj.likes,
                'members': []
            }
        }
        return baseMsg

    # 制造回复
    def make_message(self, replay):
        base = self.base_message(replay)
        if replay.type == MessageTypeEnum.TEXT.value:
            msg = {
                'content': replay.content
            }
            base.update(msg)
        elif replay.type == MessageTypeEnum.IMAGE.value:
            msg = {
                'fileInfo': {
                    'fileName': replay.file.fileName,
                    'fileSize': replay.file.fileSize,
                    'filePath': replay.file.filePath,
                }
            }
            base.update(msg)
        return base

    def get_message(self, obj):
        msg = self.make_message(obj)

        if obj.replay is not None:
            replayMsg = self.make_message(obj.replay)
            replayMsg['userID'] = obj.replay.user.pk
            replayMsg['username'] = obj.replay.user.name
            msg['replay'] = replayMsg

        return msg


class OnlineSerializers(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = UserInfo
        fields = ['user']

    def get_user(self, obj):
        online_members = self.context['online_members']
        return {
            'userID': obj.pk,
            'avatar': obj.avatar,
            'username': obj.name,
            'isActive': True if str(obj.pk).encode('utf-8') in online_members else False,
            "desc": obj.desc,
            "medals": [
                {'id': item.pk, 'title': item.title} for item in obj.medals.all()
            ],
            "email": obj.email
        }


class CreateChatRoomSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    createTime = serializers.DateTimeField(read_only=True, source="create_time", format='%Y-%m-%d %H:%M:%S')
    creator = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Room
        fields = ['id', 'createTime', 'creator', 'password', 'desc', 'type', 'isPublic', 'name']

    def get_creator(self, obj):
        return {
            "username": obj.creator.name,
            "desc": obj.creator.desc,
            "userID": obj.creator.pk,
            "avatar": obj.creator.avatar,
        }

    def create(self, validated_data):
        instance = Room.objects.create(
            creator=self.context['request'].user,
            **validated_data
        )
        # 初始化群聊
        # 加入到现有群聊里
        channel_conn.sadd(ChannelRoomEnum.ROOMS.value, instance.pk)
        # 加入创建者的已入群聊集合
        account_conn.sadd(UserEnum.JOIN_ROOM.value % instance.creator_id, instance.pk)
        # 创建者加入创建的群聊
        channel_conn.sadd(ChannelRoomEnum.ROOM_MEMBERS.value % instance.pk, instance.creator_id)
        # 智能ai加入群聊/在线
        channel_conn.sadd(ChannelRoomEnum.ROOM_MEMBERS.value % instance.pk, UserEnum.GPT_ID.value)
        channel_conn.sadd(ChannelRoomEnum.ROOM_ONLINE_MEMBERS.value % instance.pk, UserEnum.GPT_ID.value)
        return instance


class JoinChatRoomSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField()
    createTime = serializers.DateTimeField(read_only=True, source="create_time", format='%Y-%m-%d %H:%M:%S')
    creator = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True, required=False)
    name = serializers.CharField(read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'createTime', 'creator', 'password', 'desc', 'type', 'isPublic', 'name']

    def get_creator(self, obj):
        return {
            "username": obj.creator.name,
            "desc": obj.creator.desc,
            "userID": obj.creator.pk,
            "avatar": obj.creator.avatar,
        }

    def validated_id(self, obj):
        # 判断房间是否存在
        if not channel_conn.sismember(ChannelRoomEnum.ROOMS.value, obj):
            raise serializers.ValidationError("房间不存在")
        return obj

    def validate(self, attr):
        """
        判断加入的房间是否需要密码
        :return:
        """
        roomID = attr.get("id")
        password = attr.get("password")
        try:
            room = Room.objects.get(pk=roomID)
            attr['roomObj'] = room
        except Room.DoesNotExist:
            raise serializers.ValidationError("房间不存在")
        # 房间并不是公开的且密码错误
        if not room.isPublic and room.password != password:
            raise serializers.ValidationError("密码错误")
        return attr

    def create(self, validated_data):
        user_id = self.context['request'].user.pk
        room_id = validated_data['id']
        # 放入用户的加入群聊集合里
        account_conn.sadd(UserEnum.JOIN_ROOM.value % user_id, room_id)
        # 用户进入群聊
        channel_conn.sadd(ChannelRoomEnum.ROOM_MEMBERS.value % room_id,
                          user_id)
        return validated_data['roomObj']
