from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from enums.const import Room2GroupEnum


class RecordPager(PageNumberPagination):
    invalid_page_message = "无效的页码"
    page_size = 10

    def get_paginated_response(self, data):
        """
        进行构建响应
        :param data:
        :return:
        """
        return Response(OrderedDict([
            ('count', self.page.paginator.count + Room2GroupEnum.ROOM_RECORD_MAX.value),  # 总页数sql+redis的数量
            ('results', data)
        ]))
