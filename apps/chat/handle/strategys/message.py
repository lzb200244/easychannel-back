import json
from typing import NoReturn
from collections import defaultdict
from apps.account.models import UserInfo
from apps.chat.handle.strategy import Strategy
from apps.chat.models import Record, RecordFileInfo
from apps.chat.typesd.request.message import TextMessage, FileMessage
from apps.chat.typesd.base import BaseRecord
from apps.chat.typesd.message import TextMessageType, FileMessageType
from enums.message import PushTypeEnum, MessageTypeEnum
from enums.const import ChannelRoomEnum, UserEnum, MedalEnum
from utils.file.filesize import cal_file_size
from utils.mq.gpt.product import send_message
from utils.sensitive.tree_plus.prefix import tree_prefix


class MessageStrategy(Strategy):
    """消息类型处理"""
    # 对应的码
    TYPE_CODE = PushTypeEnum.MESSAGE_PUSH

    def execute(self, user: UserInfo, content: BaseRecord):
        # 响应体
        response: BaseRecord = defaultdict()
        room_id = content['roomID']
        resp = None
        # 针对文本类型
        if content['message']['type'] == MessageTypeEnum.TEXT.value:
            resp = self.save_text_to_mysql(room_id, user, content)
        # 图片类型
        elif content['message']['type'] in [MessageTypeEnum.IMAGE.value, MessageTypeEnum.FILE.value]:
            resp = self.save_file_to_mysql(room_id, user, content)
        # AI 聊天
        elif content['message']['type'] == MessageTypeEnum.GPT.value:
            resp = self.handle_gpt_message(room_id, user, content)
        response['type'] = PushTypeEnum.MESSAGE_PUSH.value
        response['user'] = {'userID': user.pk}
        response['roomID'] = int(room_id)
        response['message'] = resp
        # 存储到redis
        self.save_to_redis(room_id, user, response)
        return response

    def save_text_to_mysql(self, room_id: int, user: UserInfo, content: BaseRecord) -> TextMessageType:
        """
        保存到数据库
        :param content:
        :param room_id:
        :param user:
        :return:
        """
        message: TextMessage = content['message']
        # 针对文本类型
        filter_list, pure_content = tree_prefix.replace(message['content'])
        pure_content=pure_content.strip()
        # 存在敏感词
        if len(filter_list) > 0:
            # 用户活跃状态更新
            key = UserEnum.USER_CHAT_STATUS.value % user.pk
            self.conn.hincrby(key, MedalEnum.TROLLS.value, 1)  # 骂人次数+1
        msgObj = Record.objects.create(
            type=MessageTypeEnum.TEXT.value,
            content=pure_content,
            user=user,
            room_id=room_id
        )
        return {
            "content": pure_content,
            'time': msgObj.create_time.timestamp() * 1000,
            'msgID': msgObj.pk,
            "type": MessageTypeEnum.TEXT.value,
            'messageStatus': {
                'likes': 0,
                'drop': '',
                'members': [],
                'isDrop': False,
            }
        }

    def save_file_to_mysql(self, room_id: int, user: UserInfo,
                           content: BaseRecord) -> FileMessageType:
        """
        保存到数据库
        :param room_id:
        :param user:
        :param content:
        :return:
        """
        message: FileMessage = content['message']
        fileObj = RecordFileInfo.objects.create(
            fileName=message['fileInfo']['fileName'],
            fileSize=cal_file_size(message['fileInfo']['fileSize']),
            filePath=message['fileInfo']['filePath'],
        )
        msgObj = Record.objects.create(
            type=message['type'],
            file=fileObj,
            user=user,
            room_id=room_id,

        )
        return {
            'fileInfo': {
                'fileName': fileObj.fileName,
                'fileSize': fileObj.fileSize,
                'filePath': fileObj.filePath,
            },
            # 文件类型、图片、文件、视频
            'type': message['type'],
            'time': msgObj.create_time.timestamp() * 1000,
            'msgID': msgObj.pk,
            'messageStatus': {
                'likes': 0,
                'drop': '',
                'members': [],
                'isDrop': False,
            }
        }

    def save_to_redis(self, room_id: int, user: UserInfo, content: BaseRecord) -> NoReturn:
        """
        保存到redis
        :param room_id:
        :param user:
        :param content:
        :return:
        """
        key = ChannelRoomEnum.ROOM_MESSAGE.value % room_id
        value = json.dumps(content)
        self.conn.eval(ChannelRoomEnum.APPEND_POP_LUA.value, 1, key, ChannelRoomEnum.ROOM_MESSAGE_MAX.value, value)

    def handle_gpt_message(self, room_id: int, user: UserInfo, content: BaseRecord) -> TextMessageType:
        """
        处理gpt的回应
        :param room_id:
        :param user:
        :param content:
        :return:
        """
        resp = self.save_text_to_mysql(room_id, user, content)
        # 构建回复用户的信息
        gpt_replay = {
            'type': MessageTypeEnum.TEXT.value,
            "roomID": room_id,
            "content": resp.get('content'),
            "username": user.username,
            "userID": user.pk,
            'msgID': resp.get('msgID'),  # 回复消息的id
            'mul': False
        }
        # 放入消息队列处理进行处理异步任务
        send_message(message=gpt_replay)
        return resp
