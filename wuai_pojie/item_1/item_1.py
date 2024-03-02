# Copyright (C) 2023 - 2023 wutljs, Inc. All Rights Reserved
# @Time: 2023/12/2 10:12
# @Author: wutljs
# @File: item_1.py
# @IDE: PyCharm

import sys
import time
from PyQt5.QtCore import QRect, QThread, pyqtSignal
from PyQt5.QtWidgets import QDialog, QProgressBar, QApplication


class UiProgressBarDialog:
    """主线程类"""

    def __init__(self, dialog):
        """做一些简单的初始化工作"""

        self.dialog = dialog  # 获得空dialog
        self.dialog.setFixedSize(480, 360)  # 设置dialog尺寸
        self.progressbar = QProgressBar(self.dialog)  # 添加进度条
        self.progressbar.setGeometry(QRect(80, 80, 351, 31))  # 进设置度条尺寸
        self.progressbar.setValue(0)  # 设置进度初始值为0

    def add_task_thread(self):
        """添加子线程,并建立线程通信(重头戏)"""

        task_thread = TaskThread()  # 添加任务子线程(任务线程)
        task_thread.update_signal.connect(self.update_progressbar)  # 连接子线程(任务线程)信号与主线程的槽,搭建线程通信
        task_thread.start()  # 开启子线程(任务线程)

        self.dialog.exec_()  # dialog开始生效(显示)

    def update_progressbar(self, progressbar_value):
        """槽: 用来接收来自子线程(任务线程)发射的信号,并作出响应(更新进度条)"""
        self.progressbar.setValue(progressbar_value)


class TaskThread(QThread):
    """子线程类"""

    update_signal = pyqtSignal(int)  # 信号: 通知主线程更新进度条的信号
    task_total_num = 1000  # 假设任务总量为1000
    task_finished_num = 0  # 任务完成量

    def do_task(self):
        self.task_finished_num += 1  # 更新任务完成量
        self.update_signal.emit(
            self.task_finished_num / self.task_total_num * 100)  # 子线程(任务线程)发射信号,通知主线程更新进度条的值为此信号所携带的值.

    def run(self):
        # 模拟完成任务
        for i in range(self.task_total_num):
            self.do_task()  # 模拟做任务
            time.sleep(0.001)  # 防止进度条更新过快不便于观察


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = UiProgressBarDialog(QDialog())
    ui.add_task_thread()
