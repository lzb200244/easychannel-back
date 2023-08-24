import abc

import redis
from django_redis import get_redis_connection

from apps.account.models import UserInfo
from apps.chat.apps import ChatConfig
from apps.chat.typesd.base import BaseMessage


class Strategy(abc.ABC):
    conn: redis.Redis = get_redis_connection(ChatConfig.name)
    @abc.abstractmethod
    def execute(self, user: UserInfo, content: BaseMessage) -> BaseMessage:
        """

        :param user: 用户对象
        :param content: MessageType对象
        :return: 返回处理好的mes对象
        """
        pass
