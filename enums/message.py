from enum import IntEnum


class MessageTypeEnum(IntEnum):
    # 消息类型
    TEXT = 1
    # 文件类型
    FILE = 2
    # 图片类型
    IMAGE = 3
    # 音频类型
    VIDEO = 4
    # AI 聊天
    GPT = 5


class PushTypeEnum(IntEnum):
    MESSAGE_PUSH = 1
    ONLINE_PUSH = 2
    LEVEL_PUSH = 3
    RECALL_PUSH = 4
    UPLOAD_FILE_PUSH = 5
    THUMB_PUSH = 6
    REPLAY_PUSH = 7

    def __str__(self):
        return str(self.value)


