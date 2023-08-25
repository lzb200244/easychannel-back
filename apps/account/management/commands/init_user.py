# -*- coding: utf-8 -*-
"""
    @Time：2023/8/20
    @Author：斑斑砖
    Description：
        初始化ai,和初始化用户
"""
import logging

from django.core.management import BaseCommand
from apps.account.models import UserInfo, Medal
from enums.const import UserEnum, MedalEnum

logger = logging.getLogger('account')
medals_data = [
    {
        'id': MedalEnum.THUMB.value,
        'title': MedalEnum.THUMB.title,
        'path': 'https://chat-default-source-1311013567.cos.ap-nanjing.myqcloud.com/default_medal01.png',
        'desc': '给评论点赞达到100个',
    },
    {
        'id': MedalEnum.SOLVER.value,
        'title': MedalEnum.SOLVER.title,
        'path': 'https://chat-default-source-1311013567.cos.ap-nanjing.myqcloud.com/default_medal02.png',
        'desc': '为他人解答疑惑',
    },
    {
        'id': MedalEnum.TROLLS.value,
        'title': MedalEnum.TROLLS.title,
        'path': 'https://chat-default-source-1311013567.cos.ap-nanjing.myqcloud.com/default_medal05.png',
        'desc': '被禁言一天',
    },
    {
        'id': MedalEnum.SOCIAL.value,
        'title': MedalEnum.SOCIAL.title,
        'path': 'https://chat-default-source-1311013567.cos.ap-nanjing.myqcloud.com/default_medal06.png',
        'desc': '互相关注超过10人',
    },
]


class Command(BaseCommand):
    # 帮助文本, 一般备注命令的用途及如何使用。
    help = 'init user'

    # 核心业务逻辑
    def handle(self, *args, **options):
        # 1. 初始化ai
        if not UserInfo.objects.filter(id=UserEnum.GPT_ID.value).exists():
            UserInfo.objects.create_user(
                id=UserEnum.GPT_ID.value,
                username=UserEnum.GPT_NAME.value,
                name=UserEnum.GPT_NAME.value,
                password=UserEnum.GPT_PWD.value,
                email=UserEnum.GPT_EMAIL.value,
                desc=UserEnum.GPT_DESC.value,
                avatar=UserEnum.GPT_AVATAR.value
            )
            logger.info('初始化ai成功!')
        # 2. 初始化admin
        if not UserInfo.objects.filter(username='admin').exists():
            UserInfo.objects.create_user(
                username='admin', password='admin',
                email='2632141215@qq.com',
                desc="我是这个站的老大",
                name='斑斑砖',
                is_superuser=True,
                avatar='https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif',
            )
            # https://p9-passport.byteacctimg.com/img/user-avatar/e9208e27ca98452d1e944fc4f0ce3d4c~40x40.awebp
            logger.info('初始化admin成功!')
        # 3. 初始化勋章列表
        if Medal.objects.count() == 0:
            for medal_data in medals_data:
                Medal.objects.create(
                    pk=medal_data['id'],
                    title=medal_data['title'],
                    path=medal_data['path'],
                    desc=medal_data['desc'],
                )
            logger.info('初始化勋章列表成功!')
