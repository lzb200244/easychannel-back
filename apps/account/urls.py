# -*- coding: utf-8 -*-
# @Time : 2022/12/26 8:57
# @Site : https://www.codeminer.cn
"""
ex:账户映射
"""
from django.urls import path

from apps.account.views import (
    RegisterAPIView,
    LoginAPIView, UploadAvatarAPIView, MedalsAPIView, ProfileUserInfoAPIView,UserJoinRoomAPIView
)

urlpatterns = [
    # 登录
    path('login', LoginAPIView.as_view(), name='login'),
    # 注册
    path('register', RegisterAPIView.as_view(), name='register'),
    # 获取用户信息，和更新用户信息
    path('profile', ProfileUserInfoAPIView.as_view(), name='profile'),
    # 获取用户获得的勋章
    path('medal', MedalsAPIView.as_view(), name='medals'),
    path('join', UserJoinRoomAPIView.as_view(), name='medals'),
    # 获取凭证
    path('get_credict', UploadAvatarAPIView.as_view(), name='get_credict'),
]
