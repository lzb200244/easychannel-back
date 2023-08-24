import redis
from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework.exceptions import NotFound, PermissionDenied

from apps.account.apps import AccountConfig
from apps.account.models import UserInfo
from apps.chat.apps import ChatConfig
from consts.errors import ErrorMessageConst
from enums.const import Room2GroupEnum, UserEnum
from apps.chat.models import GroupRecords, GroupRoom
from enums.message import PushTypeEnum, MessageTypeEnum

channel_conn: redis.Redis = get_redis_connection(ChatConfig.name)
account_conn: redis.Redis = get_redis_connection(AccountConfig.name)


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
        model = GroupRecords
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
                'fileInfo': replay.file
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
        model = GroupRoom
        fields = ['id', 'createTime', 'creator', 'password', 'desc', 'type', 'isPublic', 'name']

    def get_creator(self, obj):
        return {
            "username": obj.creator.name,
            "desc": obj.creator.desc,
            "userID": obj.creator.pk,
            "avatar": obj.creator.avatar,
        }

    def create(self, validated_data):
        instance = GroupRoom.objects.create(
            creator=self.context['request'].user,
            **validated_data
        )
        # 初始化群聊
        # 加入到现有群聊里
        channel_conn.sadd(Room2GroupEnum.ROOMS.value, instance.pk)
        # 加入创建者的已入群聊集合
        account_conn.sadd(UserEnum.JOIN_GROUP.value % instance.creator_id, instance.pk)
        # 创建者加入创建的群聊
        channel_conn.sadd(Room2GroupEnum.ROOM_MEMBERS.value % instance.pk, instance.creator_id)
        # 智能ai加入群聊/在线
        channel_conn.sadd(Room2GroupEnum.ROOM_MEMBERS.value % instance.pk, UserEnum.GPT_ID.value)
        channel_conn.sadd(Room2GroupEnum.ROOM_ONLINE_MEMBERS.value % instance.pk, UserEnum.GPT_ID.value)
        return instance


class JoinChatRoomSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField()
    createTime = serializers.DateTimeField(read_only=True, source="create_time", format='%Y-%m-%d %H:%M:%S')
    creator = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True, required=False)
    name = serializers.CharField(read_only=True)

    class Meta:
        model = GroupRoom
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
        if not channel_conn.sismember(Room2GroupEnum.ROOMS.value, obj):
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
            room = GroupRoom.objects.get(pk=roomID)
            attr['roomObj'] = room
        except GroupRoom.DoesNotExist:
            raise serializers.ValidationError("房间不存在")
        # 房间并不是公开的且密码错误
        if not room.isPublic and room.password != password:
            raise serializers.ValidationError("密码错误")
        return attr

    def create(self, validated_data):
        user_id = self.context['request'].user.pk
        room_id = validated_data['id']
        # 放入用户的加入群聊集合里
        account_conn.sadd(UserEnum.JOIN_GROUP.value % user_id, room_id)
        # 用户进入群聊
        channel_conn.sadd(Room2GroupEnum.ROOM_MEMBERS.value % room_id,
                          user_id)
        return validated_data['roomObj']


class ValidRoomSerializers(serializers.Serializer):
    page = serializers.IntegerField(
        required=False, default=1, error_messages={
            'required': '无效的页码', 'invalid': '无效的页码',
        })
    room = serializers.IntegerField(
        required=True,
        error_messages={
            'required': '无效的房间号', 'invalid': '无效的房间号',
        })

    def validate_room(self, value):
        request = self.context['request']
        # 房间是否存在
        if not channel_conn.sismember(Room2GroupEnum.ROOMS.value, value):
            raise NotFound(ErrorMessageConst.ROOM_NOT_EXIST.value)
        # 未登录用户只能查看大群聊
        if request.user is None and value != Room2GroupEnum.DEFAULT_ROOM.value:
            # 登录
            raise PermissionDenied(ErrorMessageConst.USER_NOT_LOGIN.value)
        # 登录用户是否加入了该群聊
        if not account_conn.sismember(UserEnum.JOIN_GROUP.value % request.user.pk, value):
            raise NotFound(ErrorMessageConst.USER_NOT_IN_ROOM.value)
        return value
