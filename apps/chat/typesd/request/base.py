from typing import TypedDict
from enums.message import PushTypeEnum, MessageTypeEnum


class BaseUserItem(TypedDict):
    userID: int


class BaseMessage(TypedDict):
    type: MessageTypeEnum
    msgID: int


class BaseRecord(TypedDict):
    type: PushTypeEnum
    roomID: int
