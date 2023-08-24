# -*- coding: utf-8 -*-
# @Time : 2022/12/24 11:35
# @Site : https://www.codeminer.cn 
"""
ex:封装Response
"""

from rest_framework.response import Response

from enums.response import CodeResponseEnum


class APIResponse(Response):
    # code=status+800
    def __init__(self, data=None,
                 code=CodeResponseEnum.Success.value,
                 msg='ok',
                 error=None,
                 status=None,
                 headers=None,
                 **kwargs):
        dic = {'code': code, 'msg': msg, 'data': data, }

        if data is None:
            dic.pop('data')
        if error:
            dic['error'] = error
        dic.update(kwargs)

        super().__init__(data=dic, status=status, headers=headers)
