from typing import TypedDict, Union, List
from enums.message import PushTypeEnum, MessageTypeEnum


class FileInfo(TypedDict):
    fileName: str
    fileSize: int
    filePath: str


class BaseMessage(TypedDict):
    type: Union[MessageTypeEnum, int]
    time: int
    msgID: int
    messageStatus: 'MessageStatus'


class RecallMessage(TypedDict):
    type: MessageTypeEnum
    msgID: int


class TextMessage(BaseMessage):
    content: str


class FileMessage(BaseMessage):
    fileInfo: FileInfo


Message = TextMessage | FileMessage


class MessageStatus(TypedDict):
    drop: str
    likes: int
    isDrop: bool
    # 是否喜欢
    members: List[int]  # 0|1|2


class ReplayMessage(TypedDict):
    type: Union[MessageTypeEnum, int]
    time: int
    msgID: int
    roomID: int
    replay: Message
    messageStatus: MessageStatus


class MessageWithReplay(BaseMessage):
    replay: ReplayMessage


class BaseUserItem(TypedDict):
    userID: int


class BaseRecord(TypedDict):
    type: Union[PushTypeEnum, int]
    message: BaseMessage | ReplayMessage | TextMessage | FileMessage | RecallMessage
    user: BaseUserItem
    roomID: int


class UserMessage(TypedDict):
    type: Union[PushTypeEnum, int]
    user: BaseUserItem
