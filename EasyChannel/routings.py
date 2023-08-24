# -*- coding: utf-8 -*-
# @Time : 2023/5/12 17:07
# @Site : https://www.codeminer.cn 
"""
file-name:routings
ex:
"""
from django.urls import re_path

from apps.ws.consumer import ChatConsumer

websocket_urlpatterns = [
    re_path('room/(?P<group>\w+)/$', ChatConsumer.as_asgi()),
]
