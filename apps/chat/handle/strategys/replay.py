import json
from typing import Union
from collections import defaultdict

from apps.account.models import UserInfo
from apps.chat.handle.strategy import Strategy
from apps.chat.models import GroupRecords
from apps.chat.typesd.base import BaseRecord, ReplayMessage
from apps.chat.typesd.replay import TextMessageWithReplayType, ImageMessageWithReplayType
from enums.message import MessageTypeEnum, PushTypeEnum
from enums.const import Room2GroupEnum, UserEnum, MedalEnum
from utils.file.filesize import cal_file_size
from utils.mq.gpt.product import send_message
from utils.sensitive.tree_plus.prefix import tree_prefix


class ReplayStrategy(Strategy):
    """回复"""

    # 对应的码

    def execute(self, user: UserInfo, content: BaseRecord):
        response: BaseRecord = defaultdict()
        room_id = content['roomID']
        resp = None
        if content['message']['type'] in [MessageTypeEnum.TEXT.value, MessageTypeEnum.GPT.value]:
            resp = self.save_text_to_mysql(room_id, user, content)
            # 回复的AI,AI进行回应
            if resp['replay']['userID'] == UserEnum.GPT_ID.value:
                gpt_replay = {
                    'type': MessageTypeEnum.TEXT.value,
                    "roomID": room_id,
                    "content": resp['replay']['content'],  # 进行问答的问题
                    "username": user.username,
                    "userID": user.pk,
                    'msgID': resp['msgID'],  # 回复消息的id
                    'mul': True,
                    'question': resp['content']  # 用户的问题
                }
                # 放入消息队列处理进行处理异步任务
                send_message(message=gpt_replay)
        # # 消息体是图片类型
        elif content['message']['type'] in [MessageTypeEnum.IMAGE.value, MessageTypeEnum.FILE.value]:
            resp = self.save_file_to_mysql(room_id, user, content)
        #     存储到redis
        response['type'] = PushTypeEnum.REPLAY_PUSH.value
        response['user'] = {
            'userID': user.pk
        }
        response['roomID'] = int(room_id)
        response['message'] = resp
        self.save_to_redis(room_id, response)
        return response

    def make_replay(self, replay):
        """
        构造回复
        """
        msg = {}
        if replay.type == MessageTypeEnum.TEXT.value:
            msg = {
                'type': replay.type,
                'content': replay.content,
                'userID': replay.user.pk,
                'username': replay.user.name,
                'msgID': replay.pk
            }
        elif replay.type in [MessageTypeEnum.IMAGE.value, MessageTypeEnum.FILE.value]:
            msg = {
                'type': replay.type,
                'fileInfo': {
                    'fileName': replay.file.fileName,
                    'fileSize': replay.file.fileSize,
                    'filePath': replay.file.filePath,
                },
                'userID': replay.user.pk,
                'username': replay.user.name,
                'msgID': replay.pk

            }

        return msg

    def save_text_to_mysql(self, group: Union[int, str], user: UserInfo, content: BaseRecord):
        """
        保存到数据库
        """
        message: TextMessageWithReplayType = content['message']

        # 敏感词替换
        filter_list, pure_content = tree_prefix.replace(message['content'])
        pure_content = pure_content.strip()

        # 更新用户活跃状态
        key = UserEnum.USER_CHAT_STATUS.value % user.pk
        # 存在敏感词
        if len(filter_list) > 0:
            # 用户活跃状态更新
            self.conn.hincrby(key, MedalEnum.TROLLS.value, 1)  # 骂人次数+1
        self.conn.hincrby(key, MedalEnum.SOLVER.value, 1)

        replay: ReplayMessage = message['replay']
        msgObj = GroupRecords.objects.create(
            type=message['type'],
            content=pure_content,
            user=user,
            room_id=group,
            replay_id=replay['msgID']
        )
        try:
            # 构造回复
            replay_obj = GroupRecords.objects.get(pk=replay['msgID'])
            replay_msg = self.make_replay(replay_obj)
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
                },
                "replay": replay_msg
            }

        except GroupRecords.DoesNotExist:
            pass

    def save_file_to_mysql(self, group: Union[int, str], user: UserInfo, content: BaseRecord):
        """
        保存到数据库
        """
        message: ImageMessageWithReplayType = content['message']
        replay: ReplayMessage = message['replay']
        # 获取文件大小单位kb
        fileSize = cal_file_size(message['fileInfo']['fileSize'])
        # 更新用户活跃状态
        key = UserEnum.USER_CHAT_STATUS.value % user.pk
        self.conn.hincrby(key, MedalEnum.SOLVER.value, 1)
        # 入库
        message['fileInfo']['fileSize'] = fileSize
        msgObj = GroupRecords.objects.create(
            type=message['type'],
            file=message['fileInfo'],
            user=user,
            room_id=group,
            replay_id=replay['msgID']
        )

        try:
            # 构造回复
            replay_obj = GroupRecords.objects.get(pk=replay['msgID'])

            replay_msg = self.make_replay(replay_obj)
            message['replay'] = replay_msg

            return {
                'fileInfo': message['fileInfo'],
                'type': message['type'],
                'time': msgObj.create_time.timestamp() * 1000,
                'msgID': msgObj.pk,
                'messageStatus': {
                    'likes': 0,
                    'drop': '',
                    'members': [],
                    'isDrop': False,
                },
                "replay": replay_msg

            }

        except GroupRecords.DoesNotExist:
            pass

    def save_to_redis(self, group: Union[int, str],
                      content: BaseRecord):

        # 获取key
        key = Room2GroupEnum.ROOM_RECORDS.value % group
        value = json.dumps(content)
        self.conn.eval(Room2GroupEnum.APPEND_POP_LUA.value, 1, key, Room2GroupEnum.ROOM_RECORD_MAX.value, value)
