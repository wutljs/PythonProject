# -*- coding: utf-8 -*-
# @Author  : LouJingshuo
# @E-mail  : 3480339804@qq.com
# @Time    : 2023/7/6 16:23
# @Function: Infringement must be investigated, please indicate the source of reproduction!


import sys

from PyQt5.QtWidgets import QApplication, QMainWindow

import main_window

if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = main_window.Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
