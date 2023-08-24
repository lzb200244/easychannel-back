from enum import Enum


class ChannelRoomEnum(Enum):
    # =========================================================== 默认房间（大聊天群）
    DEFAULT_ROOM = '1'
    # =========================================================== Room
    ROOM = "room-%s"
    # =========================================================== 存在的所有房间号
    ROOMS = "room_numbers"  # =》set
    # =========================================================== 存储房间号的所有消息
    ROOM_MESSAGE = "room_messages:%s"  # => list
    # =========================================================== 单个队列的最大长度
    ROOM_MESSAGE_MAX = 10
    # =========================================================== 房间总共人数
    ROOM_MEMBERS = "room_members:%s"  # =>set
    # =========================================================== 房间在线人数
    ROOM_ONLINE_MEMBERS = "room_online_members:%s"  # =>set
    # =========================================================== lua脚本
    APPEND_POP_LUA = """
              local key = KEYS[1]
              local maxlen = tonumber(ARGV[1])
              local value = ARGV[2]
              local current_length = redis.call('llen', key)

              if current_length >= maxlen 
              then
                  redis.call('lpop', key)
              end
              redis.call('rpush', key, value)
           """


class RecordEnum(Enum):
    """消息的状态"""
    # =========================================================== 消息的点赞状态
    RECORD_LIKES = "record:%s:likes"  # => zset 消息id ，记录k是用户id，v是点赞时间搓


class UserEnum(Enum):
    # =========================================================== ai聊天助手的id
    GPT_ID = 1
    # =========================================================== 我加入的群聊
    JOIN_ROOM = "user:%s:room_chats"  # => set
    # =========================================================== 用户的聊天状态，给用户发放勋章
    USER_CHAT_STATUS = "user:%s:chat_status"  # => hset 记录用户发言次数，违规发言，点赞数量，交友数量

    # ===========================================================


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
    def title(self):
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
