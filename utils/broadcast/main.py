# -*- coding: utf-8 -*-
"""
    @Time：2023/8/19
    @Author：斑斑砖
    Description：
        
"""
import script.__init__script
from channels.layers import get_channel_layer

from asgiref.sync import async_to_sync


def broadcast(room: str, data: str) -> None:
    channel = get_channel_layer()
    async_to_sync(channel.group_send)(
        room,
        {
            'type': 'handle.message',
            'text': data,
        }
    )
