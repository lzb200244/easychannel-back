import jwt
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.model import BaseModel
from utils import snowflake


class Medal(BaseModel):
    """
    勋章
    """
    title = models.CharField(max_length=32, verbose_name="勋章")
    path = models.URLField(verbose_name="地址")
    desc = models.CharField(max_length=64, verbose_name="描述")


class UserMedal(BaseModel):
    """用户勋章"""
    user = models.ForeignKey('UserInfo', on_delete=models.CASCADE, verbose_name="用户")
    medal = models.ForeignKey(Medal, on_delete=models.CASCADE, verbose_name="勋章")


class UserInfo(BaseModel, AbstractUser):
    """用户表"""
    id = models.PositiveBigIntegerField(primary_key=True, verbose_name='用户id')
    username = models.CharField(max_length=18, verbose_name="用户名", unique=True)
    name = models.CharField(max_length=18, verbose_name="昵称")
    avatar = models.URLField(verbose_name="头像地址", default='', )
    desc = models.TextField(verbose_name="描述", default='')
    medals = models.ManyToManyField(Medal, through=UserMedal, verbose_name="用户勋章")

    class Meta(object):
        ordering = ["create_time"]
        verbose_name = '账户'
        verbose_name_plural = verbose_name

        indexes = [
            models.Index(fields=['username', 'password'], name='idx_name_pwd'),
        ]

    def save(self, *args, **kwargs):

        if not self.id:
            self.id = snowflake.snowflake.generate_id()
        if not self.name:
            self.name = self.username

        super(UserInfo, self).save(*args, **kwargs)

    def get_token(self) -> str:
        """
        生成jwt返回给用户
        :return:
        """
        SALT = settings.SECRET_KEY  # 岩

        headers = {
            'typ': settings.JWT_CONF.get('typ', 'jwt'),  # 头
            'alg': settings.JWT_CONF.get('alg', 'HS256'),  # 算法
        }
        payload = {
            'id': self.pk,
            'username': self.username,
            'exp': settings.JWT_CONF.get('exp', 60)
        }

        token = jwt.encode(payload=payload, key=SALT, algorithm=headers.get('alg'), headers=headers).encode(
            "utf-8").decode(
            'utf-8')
        return token
