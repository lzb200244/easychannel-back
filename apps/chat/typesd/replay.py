from apps.chat.typesd.base import TextMessage, ReplayMessage, FileMessage


class TextMessageWithReplayType(TextMessage, ReplayMessage):
    """消息回复类型"""
    pass


class ImageMessageWithReplayType(FileMessage, ReplayMessage):
    """图片回复类型"""
    pass