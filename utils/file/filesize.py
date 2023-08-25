# -*- coding: utf-8 -*-
"""
    @Time：2023/8/21
    @Author：斑斑砖
    Description：
        计算文件大小
"""


def cal_file_size(size: int) -> float:
    """计算文件大小"""
    if size < 1024:
        return size

    return round(size / 1024, 2)
