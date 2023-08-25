import random
import string
from enum import Enum


class Room2GroupEnum(Enum):
    """针对群聊的"""
    # =========================================================== 默认房间（大聊天群）
    DEFAULT_ROOM = '1'
    # =========================================================== GroupRoom
    ROOM = "group-%s"
    # =========================================================== 存在的所有房间号 =>set
    ROOMS = "group_numbers"
    # =========================================================== 房间的聊天记录 =>list
    ROOM_RECORDS = "group_records:%s"
    # =========================================================== 单个队列的最大长度 =>list
    ROOM_RECORD_MAX = 10
    # =========================================================== 房间总共人数 =>set
    ROOM_MEMBERS = "group_members:%s"
    # =========================================================== 房间在线人数=>set
    ROOM_ONLINE_MEMBERS = "group_online_members:%s"
    # =========================================================== lua脚本
    APPEND_POP_LUA = """
              local key = KEYS[1]
              local maxlen = tonumber(ARGV[1])
              local value = ARGV[2]
              local current_length = redis.call('llen', key)

              if current_length >= maxlen 
              then
                  redis.call('rpop', key)
              end
              redis.call('lpush', key, value)
           """


class Record2GroupEnum(Enum):
    """消息的状态"""
    # =========================================================== 消息的点赞状态
    RECORD_LIKES = "group_record:%s:likes"  # => zset 消息id ，记录k是用户id，v是点赞时间搓
    # RECORD_LIKES_EXPIRE = datetime.timedelta(days=15)


class Room2PrivateEnum(Enum):
    """私聊"""
    # =========================================================== GroupRoom
    ROOM = "private-%s"
    # =========================================================== 存在的所有房间号
    ROOMS = "private_numbers"  # =》set
    # =========================================================== 存储房间号的所有消息
    ROOM_RECORDS = "private_records:%s"  # => list
    # =========================================================== 房间成员
    ROOM_MEMBERS = "private_records:%s"  # =>set


class UserEnum(Enum):
    # =========================================================== ai聊天助手的id
    GPT_ID = 1
    GPT_NAME = "AI慧聊"
    GPT_PWD = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    GPT_DESC = '我是一个ai助手,你可以让我帮你做点什么。例如:写代码、聊天。'
    GPT_EMAIL = 'gpt@qq.com'
    GPT_AVATAR = 'https://chat-default-source-1311013567.cos.ap-nanjing.myqcloud.com/default-ai-avatar.svg'
    # =========================================================== 我加入的群聊
    JOIN_GROUP = "user:%s:groups"  # => set
    # =========================================================== 我加入的私聊
    JOIN_PRIVATE = "user:%s:private"
    # =========================================================== 用户的聊天状态，给用户发放勋章
    USER_CHAT_STATUS = "user:%s:chat_status"  # => hset 记录用户发言次数，违规发言，点赞数量，交友数量


class MedalEnum(Enum):
    # 点赞达人
    THUMB = 1
    # 解题砖家
    SOLVER = 2
    # 网络喷子
    TROLLS = 3
    # 交友达人
    SOCIAL = 4

    @property
    def title(self) -> str:
        mp = {
            1: '点赞达人',
            2: '解题砖家',
            3: '网络喷子',
            4: '交友达人',
        }
        return mp[self.value]


class MQEnum(Enum):
    # =========================================================== 调用gpt的队列
    GPT_QUEUE = 'easy-channel:gpt'
    GPT_EXCHANGE = ''

    # ============================================================
