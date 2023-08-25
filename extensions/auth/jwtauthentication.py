import jwt
from rest_framework import status
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed, APIException
from django.conf import settings

from apps.account.models import UserInfo
from consts.errors import ErrorMessageConst

"""
ex:自定义jwt认证类
"""


def decode_jwt(token: str) -> dict:
    salt = settings.JWT_CONF.get('salt', settings.SECRET_KEY)  # 盐
    typ = settings.JWT_CONF.get('typ', 'HS256')  #
    payload = jwt.decode(
        token, salt, typ
    )
    return payload


class JWTAuthentication(BaseAuthentication):
    """
    jwt认证类
    """

    def authenticate(self, request):
        cookie: dict = request.COOKIES
        jwt_token = cookie.get('access_token')

        # 非法请求
        if jwt_token is None:
            # 未携带token未认证
            return None, None
        try:
            payload = decode_jwt(jwt_token)
            # print(payload)
        except jwt.exceptions.ExpiredSignatureError:
            # 1101 过期
            raise AuthenticationFailed(ErrorMessageConst.JWT_EXPIRED.value)
        except jwt.exceptions.DecodeError:
            # 解码错误
            raise AuthenticationFailed(ErrorMessageConst.JWT_DECODE_ERROR.value)
        except jwt.exceptions.InvalidTokenError:
            # 非法token
            raise AuthenticationFailed(ErrorMessageConst.JWT_VALID_ERROR.value)
        try:
            payload.pop('exp')
            user = UserInfo.objects.only('id', 'username').get(**payload)
        except UserInfo.DoesNotExist:
            # 用户不存在

            raise AuthenticationFailed(ErrorMessageConst.JWT_EXPIRED.value)

        return user, jwt_token  # 认证通过
