# -*- coding: utf-8 -*-
"""
    @Time：2023/8/20
    @Author：斑斑砖
    Description：
        启动后台任务、注册后台任务
"""
import abc
import logging
import threading
from typing import List

logger = logging.getLogger('chat')


class BackgroundTask(threading.Thread):
    title = "后台任务"
    desc = "专门执行后台任务"

    def __init__(self):
        super().__init__()
        self.daemon = True

    def run(self):
        logger.log(level=logging.INFO, msg=f'名叫：{self.title}的后台任务执行成功......')
        self.task_logic()

    @abc.abstractmethod
    def task_logic(self):
        raise NotImplementedError("子类需要实现 task_logic 方法")


class RegisterTask:
    """进行任务注册"""
    tasks: List[BackgroundTask] = []
    task_count = 0

    def register(self, task: BackgroundTask):
        assert isinstance(task, BackgroundTask), "task 必须是 BackgroundTask 类型"
        self.tasks.append(task)
        self.task_count += 1

    def run(self):

        for task in self.tasks:
            task.start()
