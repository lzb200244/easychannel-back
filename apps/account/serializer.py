# -*- coding: utf-8 -*-
# @Time : 2022/12/24 11:58
# @Site : https://www.codeminer.cn
"""
    ex:账号序列化器

"""
import copy
import time

import redis
from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from apps.account.models import UserInfo, Medal
from apps.chat.models import Room
from consts.errors import ErrorMessageConst
from enums.const import ChannelRoomEnum, UserEnum, MedalEnum
from utils.factory.patternFc import Pattern

channel_conn: redis.Redis = get_redis_connection('channel')
account_conn: redis.Redis = get_redis_connection('account')


class AccountSerializers(serializers.ModelSerializer):
    pat = Pattern()

    password = serializers.CharField(max_length=32, min_length=6, write_only=True, error_messages={
        'required': '密码不能为空', 'blank': '密码不能为空', 'max_length': '密码不能超过32个字符',
        'min_length': '密码不能少于6个字符',
    })
    rePassword = serializers.CharField(max_length=32, min_length=6, write_only=True, error_messages={
        'required': '确认密码不能为空', 'blank': '确认密码不能为空', 'max_length': '密码不能超过32个字符',
        'min_length': '密码不能少于6个字符',
    })
    email = serializers.CharField(max_length=64, read_only=True)
    username = serializers.CharField(max_length=20, min_length=6, write_only=True, error_messages={
        'required': '用户名不能为空', 'blank': '用户名不能为空', 'max_length': '用户名不能超过20个字符',
        'min_length': '用户名不能少于6个字符',
    })

    class Meta:

        model = UserInfo
        fields = ['username', 'password', 'rePassword', 'email']

    def get_userID(self, attr):
        return attr.pk

    def validate_username(self, value):

        # 用户名已经存在
        if UserInfo.objects.filter(username=value).exists():
            raise ValidationError(detail=ErrorMessageConst.USERNAME_EXIST_ERROR.value)
        return value

    def validate_email(self, value):
        # 邮箱必须是邮箱格式
        if UserInfo.objects.filter(email=value).exists():
            raise ValidationError(detail=ErrorMessageConst.EMAIL_EXIST_ERROR.value)
        if not self.pat['email'].match(value):
            raise ValidationError(detail=ErrorMessageConst.EMAIL_TYPE_ERROR.value)

        return value

    def validate(self, attrs):
        # 校验确认密码是否一致
        if attrs["rePassword"] != attrs["password"]:
            raise ValidationError(detail=ErrorMessageConst.PASSWORD_MATCH_ERROR.value)
        return attrs

    def save(self, **kwargs):

        data = copy.deepcopy(self.validated_data)
        data.pop('rePassword')
        obj = UserInfo.objects.create_user(**data)
        # 初始用户
        # 加入到默认的大群聊里
        channel_conn.sadd(ChannelRoomEnum.ROOM_MEMBERS.value % obj.pk, ChannelRoomEnum.DEFAULT_ROOM.value)
        # 放入到我加入的群聊里
        account_conn.sadd(UserEnum.JOIN_ROOM.value % obj.pk, ChannelRoomEnum.DEFAULT_ROOM.value)
        # 初始化用户聊天状态
        account_conn.hmset(UserEnum.USER_CHAT_STATUS.value % obj.pk, {
            MedalEnum.THUMB.value: 0,  # 点赞数量
            MedalEnum.SOLVER.value: 0,  # 回复他人
            MedalEnum.TROLLS.value: 0,  # 违规词数量
            MedalEnum.SOCIAL.value: 0,  # 互相关注数量
        })
        return obj


class LoginSerializers(serializers.ModelSerializer):
    userID = serializers.IntegerField(read_only=True, required=False, source='pk')
    email = serializers.EmailField(read_only=True, required=False)
    desc = serializers.CharField(read_only=True, required=False)
    username = serializers.CharField(error_messages={
        'required': '用户名不能为空', 'blank': '用户名不能为空',
    })
    password = serializers.CharField(write_only=True, error_messages={
        'required': '密码不能为空', 'blank': '密码不能为空',
    })
    medals = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    avatar = serializers.CharField(max_length=255, required=False)
    token = serializers.SerializerMethodField()

    class Meta:
        model = UserInfo

        fields = ['username', 'password', 'email', 'userID', 'desc', 'avatar', 'medals', "token", ]

    def get_token(self, obj):
        return obj.get_token()


class UserInfoSerializers(serializers.ModelSerializer):
    userID = serializers.IntegerField(read_only=True, required=False, source='pk')
    email = serializers.EmailField(required=False, error_messages={
        "invalid": "邮箱格式不正确",
    })
    desc = serializers.CharField(max_length=255, required=False, error_messages={
        "max_length": "描述不能超过255个字符",
    })
    username = serializers.CharField(source='name', max_length=20, required=True,
                                     error_messages={
                                         'required': '用户名不能为空', 'blank': '用户名不能为空',
                                         'max_length': '用户名不能超过20个字符',

                                     })
    medals = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    avatar = serializers.CharField(max_length=255, required=False, error_messages={
        "max_length": "头像地址不能超过255个字符",
    })

    class Meta:
        model = UserInfo
        fields = ['username', 'email', 'userID', 'desc', 'avatar', 'medals']


class MedalSerializers(serializers.ModelSerializer):
    acquire = serializers.SerializerMethodField()
    create_time = serializers.SerializerMethodField()

    class Meta:
        model = Medal
        fields = ['title', 'path', 'desc', 'acquire', 'id', 'create_time']

    def get_acquire(self, obj):
        """是否获得"""
        return False

    def get_create_time(self, obj):
        return obj.create_time.strftime("%Y年%m月%d日 %H:%M:%S")


class JoinRoomSerializers(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'name', 'desc', 'create_time', 'type']
