from enum import Enum


class ErrorMessageConst(Enum):
    """
    常量错误
    """
    # ========================================================================== JWT 错误
    JWT_EXPIRED = 'token认证失效'
    JWT_DECODE_ERROR = 'token解码失败'
    JWT_VALID_ERROR = '非法token'

    # ========================================================================== 登录/注册错误

    USERNAME_OR_PASSWORD_ERROR = '用户名或密码错误'
    USERNAME_EXIST_ERROR = '用户名已存在'
    USERNAME_NOT_EXIST_ERROR = '用户名不存在'
    USER_NOT_LOGIN = '用户未登录'
    USER_NOT_IN_ROOM = '用户未加入群聊'
    EMAIL_EXIST_ERROR = '邮箱已存在'
    EMAIL_NOT_EXIST_ERROR = '邮箱不存在'
    EMAIL_TYPE_ERROR = '邮箱不符合'
    PASSWORD_MATCH_ERROR = "两次密码不一致"

    # ========================================================================== 认证错误

    AUTHORIZED_FAIL_ERROR = '用户认证失败'
    AUTHORIZED_NOT_ERROR = "用户未认证"

    # ========================================================================= 分页
    PAGE_NOT_EXIST = '页码不存在'

    # ========================================================================== channel的
    ROOM_NOT_EXIST = "房间不存在"
