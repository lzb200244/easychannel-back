# -*- coding: utf-8 -*-
# @Time : 2023/4/23 15:33
# @Site : https://www.codeminer.cn 
"""
file-name:IsAuthenticated
ex:
"""
from django.contrib.auth.models import AnonymousUser
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

from consts.errors import ErrorMessageConst


class CustomIsAuthenticated(BasePermission):

    def has_permission(self, request, view):
        # 需要登录

        if isinstance(request.user, AnonymousUser) or request.user is None:
            raise PermissionDenied(ErrorMessageConst.AUTHORIZED_NOT_ERROR.value)
        return True
