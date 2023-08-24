from apps.account.models import UserInfo
from apps.chat.handle.strategy import Strategy
from apps.chat.handle.strategys.message import MessageStrategy
from apps.chat.handle.strategys.replay import ReplayStrategy
from apps.chat.handle.strategys.recall import RecallStrategy
from apps.chat.handle.strategys.thumb import ThumbStrategy

from apps.chat.typesd.base import BaseMessage
from enums.message import PushTypeEnum


class MessageTypeHandler:

    def __init__(self):
        self.strategies: dict = {}

    def add_strategy(self, code, strategy: 'Strategy'):
        self.strategies[code] = strategy

    def handle_message(self, code, user: UserInfo, content: BaseMessage):
        if code in self.strategies:
            strategy = self.strategies[code]
        else:
            strategy = self.strategies.get('default')

        if strategy:
            return strategy.execute(user, content)
        else:
            return "No strategy found for code: {}".format(code)

    def __enter__(self, ):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


handler = MessageTypeHandler()
# 针对消息类型
handler.add_strategy(PushTypeEnum.MESSAGE_PUSH.value, MessageStrategy())
# 回复类型
handler.add_strategy(PushTypeEnum.REPLAY_PUSH.value, ReplayStrategy())
# 撤回
handler.add_strategy(PushTypeEnum.RECALL_PUSH.value, RecallStrategy())
# 点赞
handler.add_strategy(PushTypeEnum.THUMB_PUSH.value, ThumbStrategy())

if __name__ == '__main__':
    pass
