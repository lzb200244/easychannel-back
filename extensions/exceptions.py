from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied, NotAuthenticated, APIException, NotFound
from rest_framework.views import exception_handler
from rest_framework.utils.serializer_helpers import ReturnDict
from enums.response import StatusResponseEnum, CodeResponseEnum
from utils.response.response import APIResponse


def flatten_errors(errors: dict) -> str:
    """
    处理serializers.ValidationError
    {'type': [ErrorDetail(string='This field is required.', code='required')]}
    {'user': {'userID': [ErrorDetail(string='This field is required.', code='required')]}}
    :param errors:
    :return:
    """
    if isinstance(errors, ReturnDict):
        errors = dict(errors)
    for key, value in errors.items():
        if isinstance(value, list):
            return value[0]
        if isinstance(value, dict):
            return flatten_errors(value)


def custom_exception_handler(exc, context):
    """
    自定义异常处理
    """
    # 参数错误
    if isinstance(exc, serializers.ValidationError):

        error = flatten_errors(exc.detail)
        if error:
            return APIResponse(
                error=error,
                code=CodeResponseEnum.BadRequest.value,
                status=StatusResponseEnum.BadRequest.value
            )
    # 无权限
    if isinstance(exc, PermissionDenied):
        return APIResponse(
            error=exc.detail,
            code=CodeResponseEnum.Forbidden.value,
            status=StatusResponseEnum.Forbidden.value
        )
    # 认证失败
    if isinstance(exc, AuthenticationFailed):
        return APIResponse(
            error=exc.detail,
            code=CodeResponseEnum.Unauthorized.value,
            status=StatusResponseEnum.Unauthorized.value,
        )
    # 未认证
    if isinstance(exc, NotAuthenticated):
        return APIResponse(
            msg=exc.detail,
            code=CodeResponseEnum.NotAuthorized.value,
            status=StatusResponseEnum.Unauthorized.value,
        )
    if isinstance(exc, NotFound):
        return APIResponse(
            error=exc.detail,
            code=CodeResponseEnum.NotFound.value,
            status=StatusResponseEnum.NotFound.value
        )
    return exception_handler(exc, context)
