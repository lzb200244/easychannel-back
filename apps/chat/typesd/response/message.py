# -*- coding: utf-8 -*-
"""
    @Time：2023/8/22
    @Author：斑斑砖
    Description：
        
"""
from typing import TypedDict, List


class User(TypedDict):
    userID: int


class MessageStatus(TypedDict):
    likes: int
    drop: str
    members: List[int]
    isDrop: bool


class MessageType(TypedDict):
    content: str
    time: float
    msgID: int
    type: int
    messageStatus: MessageStatus


class RoomMessage(TypedDict):
    type: int
    user: User
    roomID: int
    message: MessageType
