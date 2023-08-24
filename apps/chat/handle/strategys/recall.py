import json
from apps.account.models import UserInfo
from apps.chat.handle.strategy import Strategy
from apps.chat.models import GroupRecords
from apps.chat.typesd.request.recall import RecallRecord, RecallRecordItem
from apps.chat.typesd.base import BaseRecord
from enums.message import PushTypeEnum, MessageTypeEnum
from enums.const import Room2GroupEnum, Record2GroupEnum

import datetime


class RecallStrategy(Strategy):
    """
    撤回
    """
    TYPE_CODE = PushTypeEnum.RECALL_PUSH

    def execute(self, user: UserInfo, content: RecallRecord):
        resp = None
        response = {}
        room_id = content['roomID']
        message: RecallRecordItem = content['message']
        # 撤回文本类型
        if message['type'] == MessageTypeEnum.TEXT.value:
            resp = self.delete_text_form_mysql(user, message)
        elif content['message']['type'] in [MessageTypeEnum.FILE.value, MessageTypeEnum.IMAGE.value]:
            resp = self.delete_file_form_mysql(user, message)

        response['type'] = self.TYPE_CODE.value
        response['message'] = resp
        response['roomID'] = room_id
        self.delete_form_redis(room_id, response)
        return response

    def delete_text_form_mysql(self, user: UserInfo, message: RecallRecordItem):
        """
        撤回消息
        :param user:
        :param message:
        :return:
        """
        cause = f'{datetime.datetime.now().strftime("%H:%M:%S ")} {user.name} 撤销了一条消息'
        GroupRecords.objects.filter(pk=message['msgID']).update(
            isDrop=True,
            drop=cause)
        return {
            'msgID': message['msgID'],
            'type': 1,
            'messageStatus': {
                'isDrop': True,
                'drop': cause,
                'members': [],
                'likes': 0,
            }
        }

    def delete_file_form_mysql(self, user: UserInfo, message: RecallRecordItem):
        """
        删除文件
        :param user:
        :param message:
        :return:
        """
        cause = f'{datetime.datetime.now().strftime("%H:%M:%S ")} {user.name} 撤销了一条消息'
        # 撤销直接删除
        GroupRecords.objects.filter(pk=message['msgID']).update(
            isDrop=True,
            drop=cause)
        return {
            'msgID': message['msgID'],
            'type': 1,
            'messageStatus': {
                'isDrop': True,
                'drop': cause,
                'likes': 0,
                'members': [],
            }
        }
        # 删除cos文件
        # file = obj.first().file
        # bucketName = file.bucketName
        # key = file.fileName

    def delete_form_redis(self, group, content: BaseRecord, ):
        key = Room2GroupEnum.ROOM_RECORDS.value % group
        length = self.conn.llen(key)
        # 撤销非删除，且记录撤销时间和操作人
        for i in range(length):
            res = self.conn.lpop(key)
            parse: BaseRecord = json.loads(res)
            if parse['message']['msgID'] != content['message']['msgID']:
                self.conn.rpush(key, res)
            else:
                # 标记为撤销的消息，内容为时间+某某操作
                self.conn.rpush(key, json.dumps(content))
        # 删除该条记录所有在redis的信息
        # 1. 点赞记录
        self.conn.delete(Record2GroupEnum.RECORD_LIKES.value % content['message']['msgID'])
