# -*- coding: utf-8 -*-
# @Time : 2023/3/27 12:28
# @Site : https://www.codeminer.cn 
"""
file-name:response
ex:枚举状态码
"""
from enum import IntEnum


class StatusResponseEnum(IntEnum):
    """操作"""
    # 成功
    Success = 200
    # 提交资源已经创建
    """
    客户端
    """
    # 参数错误
    BadRequest = 400
    # 认证
    Unauthorized = 401
    # 访问被被禁止
    Forbidden = 403
    # 为找到
    NotFound = 404
    """
    服务的
    """
    # 服务端错误
    ServerError = 405


class CodeResponseEnum(IntEnum):
    """操作"""
    # 成功
    Success = 1000
    # 提交资源已经创建
    """
    客户端
    """
    # 参数错误
    BadRequest = 1200

    # 认证失败
    Unauthorized = 1201
    # 未认证
    NotAuthorized = 1202
    # 访问被被禁止
    Forbidden = 1203
    # 为找到+过期
    NotFound = 1204
    """
    服务的
    """
    # 服务端错误
    ServerError = 1300

