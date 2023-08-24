from django.db import models

from apps.model import BaseModel
from apps.account.models import UserInfo
from utils.snowflake import snowflake


class Record(BaseModel, models.Model):
    """
        聊天记录表
    """
    # 消息类型
    RECORD_TYPE = (
        (1, "文本"),
        (2, "文件"),
        (3, "图片"),
        (4, "音频"),
        (5, "GPT"),
    )
    id = models.AutoField(primary_key=True)
    content = models.TextField(verbose_name="内容", null=True, blank=True, )
    type = models.PositiveSmallIntegerField(choices=RECORD_TYPE, default=1, verbose_name="消息类型")
    isDrop = models.BooleanField(default=False, verbose_name="是否是撤回")
    drop = models.CharField("撤回内容", null=True, max_length=64, blank=True)
    likes = models.PositiveIntegerField(verbose_name='点赞数量', default=0)
    replay = models.ForeignKey('self', on_delete=models.CASCADE, verbose_name='回复',
                               null=True, blank=True)
    user = models.ForeignKey(UserInfo, on_delete=models.CASCADE,
                             verbose_name='发言人', )
    # 自关联
    room = models.ForeignKey('Room', on_delete=models.CASCADE, verbose_name='聊天室')
    file = models.OneToOneField(to='RecordFileInfo', on_delete=models.CASCADE, verbose_name="文件详细记录", null=True,
                                blank=True)

    def __str__(self):
        if self.content == "":
            return self.get_type_display() + ":" + self.file.fileName
        return self.content


class RecordFileInfo(models.Model):
    bucketName = models.CharField(max_length=64, default="chat-1311013567", verbose_name="存储对象bucket地址")
    fileName = models.CharField(max_length=64, verbose_name="文件名称,也就是cos的key")
    fileSize = models.PositiveIntegerField(verbose_name="文件大小")
    filePath = models.CharField(max_length=255, verbose_name="文件路径")


class Room(BaseModel, models.Model):
    """
    聊天室模型
    """
    id = models.PositiveBigIntegerField(primary_key=True, verbose_name="房间id")
    name = models.CharField(max_length=32, verbose_name="房间名称", )
    desc = models.CharField(max_length=255, verbose_name="房间描述", blank=True, default="")
    ROOM_TYPE = (
        (1, "私聊"),
        (2, "群聊"),
    )
    type = models.PositiveSmallIntegerField(choices=ROOM_TYPE, default=2, verbose_name="房间类型")
    creator = models.ForeignKey(UserInfo, on_delete=models.CASCADE,
                                verbose_name="创建者")
    isPublic = models.BooleanField(default=True, verbose_name="是否公开")
    password = models.CharField(max_length=32, verbose_name="房间密码", null=True)

    class Meta:
        indexes = [
            models.Index(fields=['name', ], name='idx_name'),
        ]

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = snowflake.generate_id()
        super(Room, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Sensitive(models.Model):
    """
    敏感词过滤
    """
    # id, parent_id, character_text, is_end
    # id = models.PositiveIntegerField(primary_key=True, auto_created=True)
    # parentID = models.PositiveIntegerField(verbose_name="节点树的父亲..", null=True)
    # char = models.CharField(max_length=1, default=" ", blank=True, verbose_name="敏感词")
    # isWord = models.BooleanField(default=False, verbose_name="是否是一整个单词")
    id = models.AutoField(primary_key=True)
    word = models.CharField(max_length=32, verbose_name="敏感词")  # 构造优化，减少查询，通过应用层来进行构建树结构。
