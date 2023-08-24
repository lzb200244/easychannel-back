from typing import TypedDict

from apps.chat.typesd.request.base import BaseRecord


class ThumbItem(TypedDict):
    msgID: int


class ThumbType(BaseRecord):
    message: ThumbItem
