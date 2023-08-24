from typing import TypedDict

from apps.chat.typesd.request.base import BaseRecord, BaseUserItem, BaseMessage


class FileInfo(TypedDict):
    fileName: str
    fileSize: int
    filePath: str


class TextMessage(BaseMessage):
    content: str


class FileMessage(BaseMessage):
    fileInfo: FileInfo


class MessageRecord(BaseRecord):
    message: TextMessage | FileMessage
    user: BaseUserItem
