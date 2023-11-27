# -*- coding: utf-8 -*-
# @Author  : LouJingshuo
# @E-mail  : 3480339804@qq.com
# @Time    : 2023/7/8 7:25
# @Function: Infringement must be investigated, please indicate the source of reproduction!


import aiofiles
import aiohttp
import asyncio
import os
import requests
import shutil
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from PyQt5.QtWidgets import QDialog, QWidget, QMessageBox
from lxml import etree

from classify_novel_info import classify_novel_dic


class PbarDownloader(QObject):
    """此类用于抓取目标资源相关信息"""
    top_url = 'http://book.pianbar.net'
    save_address = open('save_address.txt', 'r').read().replace(r'/', '\\')
    search_novel_information_dic = dict()
    cn_dic = dict()
    finished_task_num = 0
    progressbar_value = pyqtSignal(int)  # 进度条信号
    task_done = pyqtSignal()  # 下载任务完成信号

    def search_novel(self, novel_name):
        search_url = 'http://book.pianbar.net/search/'
        params = {
            'searchkey': novel_name
        }
        text = requests.post(url=search_url, params=params).text
        html = etree.HTML(text)
        div_list = html.xpath('/html/body/div[1]//div')

        for div in div_list:
            try:
                novel_name = div.xpath('./div/div[1]/a/h3/text()')[0]
                novel_author = div.xpath('./div/div[1]/span/text()')[0]
                novel_url = self.top_url + div.xpath('./div/div[1]/a/@href')[0]
                novel_base_info = div.xpath('div/div[2]/text()')[0]
                self.search_novel_information_dic[novel_name] = (novel_url, novel_author, novel_base_info)

            except IndexError:
                continue

    async def classify_novel(self):
        async def one_kind_novel(session, novel_kind, novel_kind_url):
            one_kind_novel_list = []
            async with session.get(url=novel_kind_url) as resp:
                text = await resp.text()
                html = etree.HTML(text)
                div_list = html.xpath('/html/body/div[2]/div[1]//div')
                for div in div_list:
                    novel_name = div.xpath('./span[1]/em[2]/a/text()')[0]
                    novel_url = self.top_url + div.xpath('./span[1]/em[2]/a/@href')[0]
                    novel_author = div.xpath('./span[2]/text()')[0][:-7]
                    one_kind_novel_list.append((novel_name, novel_author, novel_url))
                self.cn_dic[novel_kind] = one_kind_novel_list

        async with aiohttp.ClientSession() as session:
            async with session.get(url=self.top_url) as resp:
                text = await resp.text()
            html = etree.HTML(text)
            a_list = html.xpath('/html/body/nav//a')

            tasks = []
            for a in a_list[1:11]:
                novel_kind = a.xpath('./text()')[0]
                novel_kind_url = self.top_url + a.xpath('./@href')[0]
                tasks.append(asyncio.create_task(one_kind_novel(session, novel_kind, novel_kind_url)))
            await asyncio.wait(tasks)

    async def download_novel(self, novel_info_list):
        async def download_one_chapter(chapter_url, chapter_id):
            async def reset_session():
                await self.session.close()
                self.session = aiohttp.ClientSession()

            async def test_session(chapter_url):
                while True:
                    try:
                        async with self.session.get(url=chapter_url) as resp:
                            return await resp.text()
                    except aiohttp.client_exceptions.ClientConnectorError:
                        await reset_session()
                    except aiohttp.client_exceptions.ClientOSError:
                        await reset_session()
                    except aiohttp.client_exceptions.ClientConnectionError:
                        await reset_session()
                    except asyncio.exceptions.TimeoutError:
                        await reset_session()

            text = await test_session(chapter_url)
            html = etree.HTML(text)
            chapter_name = html.xpath('//*[@id="ss-reader-main"]/div[2]/h1/text()')[0]
            chapter_text = ''
            p_list = html.xpath('//*[@id="article"]//p')
            for p in p_list:
                chapter_text += p.xpath('./text()')[0]

            async with aiofiles.open(rf'{self.save_address}\{novel_info_list[0]}\{chapter_id}.txt', 'w',
                                     encoding='utf-8') as fp:
                await fp.write('\n' * 2 + chapter_name + '\n' * 2 + chapter_text)
                self.finished_task_num += 1
                self.progressbar_value.emit(self.finished_task_num)

        os.system(rf'md {self.save_address}\{novel_info_list[0]}')

        # 用于给小说编号
        chapter_num = len(novel_info_list[2:])
        chapter_num_bit = 0
        while int(chapter_num) > 0:
            chapter_num /= 10
            chapter_num_bit += 1

        self.session = aiohttp.ClientSession()
        tasks = []
        num_id = 0
        for chapter_url in novel_info_list[1:]:
            s = '{:0>' + str(chapter_num_bit + 1) + '}'
            chapter_id = s.format(num_id)
            tasks.append(asyncio.create_task(download_one_chapter(chapter_url, chapter_id)))
            num_id += 1
        await asyncio.wait(tasks)

        os.system(
            rf'copy {self.save_address}\{novel_info_list[0]}\*.txt {self.save_address}\{novel_info_list[0]}.txt')
        shutil.rmtree(rf'{self.save_address}\{novel_info_list[0]}')

        self.task_done.emit()  # 小说下载完毕

        await self.session.close()


class Ui_DownloadNovelDialog(object):
    pd = PbarDownloader()
    widget_dic = dict()

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setFixedSize(800, 800)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("pictures/txt_downloader_ico.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        Dialog.setStyleSheet("background-image: url(:/background/pictures/浅色纹理.jpg);")
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(600, 50, 111, 51))
        self.pushButton.setStyleSheet("")
        self.pushButton.setStyleSheet("font: 20pt \"Muyao-Softbrush\";")
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushButton.clicked.connect(self.search_novel)
        self.label_1 = QtWidgets.QLabel(Dialog)
        self.label_1.setGeometry(QtCore.QRect(10, 10, 131, 41))
        self.label_1.setStyleSheet("font: 20pt \"Muyao-Softbrush\";")
        self.label_1.setObjectName("label_1")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(10, 130, 131, 41))
        self.label_2.setStyleSheet("font: 20pt \"Muyao-Softbrush\";")
        self.label_2.setObjectName("label_2")
        self.tabWidget = QtWidgets.QTabWidget(Dialog)
        self.tabWidget.setGeometry(QtCore.QRect(10, 190, 781, 611))
        self.tabWidget.setStyleSheet("font: 20pt \"Muyao-Softbrush\";")
        self.tabWidget.setObjectName("tabWidget")
        self.textBrowser = QtWidgets.QTextBrowser(Dialog)
        self.textBrowser.setGeometry(QtCore.QRect(110, 50, 471, 51))
        self.textBrowser.setStyleSheet("border-image: url(:/background/pictures/白色透明背景.png);")
        self.textBrowser.setReadOnly(False)
        self.textBrowser.setObjectName("textBrowser")

        for i in range(10):
            self.widget_dic[f'tab_{i}'] = QtWidgets.QWidget()
            self.widget_dic[f'tab_{i}'].setObjectName("tab")
            self.widget_dic[f'label_tab_{i}_1'] = QtWidgets.QLabel(self.widget_dic[f'tab_{i}'])
            self.widget_dic[f'label_tab_{i}_1'].setGeometry(QtCore.QRect(0, 0, 291, 271))
            self.widget_dic[f'label_tab_{i}_1'].setStyleSheet("font: 17pt \"Muyao-Softbrush\";")
            self.widget_dic[f'label_tab_{i}_1'].setObjectName("label")
            self.widget_dic[f'label_tab_{i}_2'] = QtWidgets.QLabel(self.widget_dic[f'tab_{i}'])
            self.widget_dic[f'label_tab_{i}_2'].setGeometry(QtCore.QRect(0, 280, 291, 301))
            self.widget_dic[f'label_tab_{i}_2'].setStyleSheet("font: 17pt \"Muyao-Softbrush\";")
            self.widget_dic[f'label_tab_{i}_2'].setObjectName("label")
            self.widget_dic[f'listWidget_{i}'] = QtWidgets.QListWidget(self.widget_dic[f'tab_{i}'])
            self.widget_dic[f'listWidget_{i}'].setGeometry(QtCore.QRect(330, 40, 440, 501))
            self.widget_dic[f'listWidget_{i}'].setStyleSheet("font: 17pt \"Muyao-Softbrush\";")
            self.widget_dic[f'listWidget_{i}'].setObjectName("listWidget")
            self.tabWidget.addTab(self.widget_dic[f'tab_{i}'], "")

        self.retranslateUi(Dialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.exec_()

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "下载小说"))
        self.pushButton.setText(_translate("Dialog", "搜索"))
        self.label_1.setText(_translate("Dialog", "搜索小说"))
        self.label_2.setText(_translate("Dialog", "分类专区"))
        asyncio.get_event_loop().run_until_complete(self.pd.classify_novel())

        self.novel_kind_list = list(self.pd.cn_dic.keys())
        novel_name_list = list(self.pd.cn_dic.values())
        for i in range(10):
            self.widget_dic[f'label_tab_{i}_1'].setText(_translate("Dialog", ""))
            self.widget_dic[f'label_tab_{i}_1'].setStyleSheet(
                f"border-image: url(:/background/pictures/{self.novel_kind_list[i]}.jpg);")
            self.widget_dic[f'label_tab_{i}_2'].setText(
                _translate("Dialog", classify_novel_dic[self.novel_kind_list[i]]))
            self.widget_dic[f'listWidget_{i}'].addItems([j[0] + '  作者: ' + j[1] for j in novel_name_list[i]])
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.widget_dic[f'tab_{i}']),
                                      _translate("Dialog", f"{self.novel_kind_list[i]}"))

        # 暂时没找到更好的算法代替(因为若是在循环写等待触发.itemClicked的相关逻辑,等触发时i已经变为9了,无法做到对应)
        self.widget_dic['listWidget_0'].itemClicked.connect(lambda: self.download_classify_novel('listWidget_0'))
        self.widget_dic['listWidget_1'].itemClicked.connect(lambda: self.download_classify_novel('listWidget_1'))
        self.widget_dic['listWidget_2'].itemClicked.connect(lambda: self.download_classify_novel('listWidget_2'))
        self.widget_dic['listWidget_3'].itemClicked.connect(lambda: self.download_classify_novel('listWidget_3'))
        self.widget_dic['listWidget_4'].itemClicked.connect(lambda: self.download_classify_novel('listWidget_4'))
        self.widget_dic['listWidget_5'].itemClicked.connect(lambda: self.download_classify_novel('listWidget_5'))
        self.widget_dic['listWidget_6'].itemClicked.connect(lambda: self.download_classify_novel('listWidget_6'))
        self.widget_dic['listWidget_7'].itemClicked.connect(lambda: self.download_classify_novel('listWidget_7'))
        self.widget_dic['listWidget_8'].itemClicked.connect(lambda: self.download_classify_novel('listWidget_8'))
        self.widget_dic['listWidget_9'].itemClicked.connect(lambda: self.download_classify_novel('listWidget_9'))

    def download_classify_novel(self, listwidget_id):
        listwidget = self.widget_dic[listwidget_id]
        item_id = listwidget.currentIndex().row()
        novel_url = self.pd.cn_dic[self.novel_kind_list[int(listwidget_id.split('_')[-1])]][item_id][2]
        Ui_DownloadSelectedNovelDialog(novel_url).setupUi(Dialog=QDialog())

    def search_novel(self):
        user_input_novel_name = self.textBrowser.toPlainText()
        self.pd.search_novel(user_input_novel_name)
        Ui_SearchNovelDialog(self.pd.search_novel_information_dic).setupUi(QDialog())


class Ui_SearchNovelDialog(object):

    def __init__(self, search_novel_information_dic):
        self.search_novel_information_dic = search_novel_information_dic

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setFixedSize(489, 625)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("pictures/txt_downloader_ico.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        Dialog.setStyleSheet("background-image: url(:/background/pictures/浅色纹理.jpg);")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(10, 10, 221, 51))
        self.label.setStyleSheet("font: 18pt \"Muyao-Softbrush\";")
        self.label.setObjectName("label")
        self.listWidget = QtWidgets.QListWidget(Dialog)
        self.listWidget.setGeometry(QtCore.QRect(30, 80, 441, 511))
        self.listWidget.setStyleSheet("font: 17pt \"Muyao-Softbrush\";")
        self.listWidget.setObjectName("listWidget")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.exec_()

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "搜索结果"))
        self.label.setText(_translate("Dialog", "以下是搜索结果"))
        novel_name_list = list(self.search_novel_information_dic.keys())
        self.listWidget.addItems(
            [novel_name + '  作者: ' + self.search_novel_information_dic[novel_name][1] for novel_name in
             novel_name_list])
        self.listWidget.itemClicked.connect(self.download_search_novel)

    def download_search_novel(self):
        item_id = self.listWidget.currentIndex().row()
        novel_url = list(self.search_novel_information_dic.values())[item_id][0]
        Ui_DownloadSelectedNovelDialog(novel_url).setupUi(Dialog=QDialog())


class Ui_DownloadSelectedNovelDialog(object):

    def __init__(self, novel_url):
        self.top_url = 'http://book.pianbar.net'
        text = requests.get(url=novel_url).text
        self.html = etree.HTML(text)
        self.novel_name = self.html.xpath('/html/body/div[1]/div[1]/div[2]/div/h1/text()')[0]
        self.novel_author = self.html.xpath('/html/body/div[1]/div[2]/a[1]/p/text()')[0].split('：')[-1]
        self.novel_introduction = self.html.xpath('/html/body/div[1]/div[1]/div[2]/div/div[3]/p/text()')[0]
        self.novel_last_update_time = self.html.xpath('/html/body/div[1]/div[2]/p/text()')[0].split('：')[-1].strip()

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setFixedSize(521, 537)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("pictures/txt_downloader_ico.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        Dialog.setStyleSheet("background-image: url(:/background/pictures/浅色纹理.jpg);")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(10, 10, 481, 51))
        font = QtGui.QFont()
        font.setFamily("Muyao-Softbrush")
        font.setPointSize(16)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(260, 70, 251, 41))
        font = QtGui.QFont()
        font.setFamily("Muyao-Softbrush")
        font.setPointSize(14)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.textBrowser = QtWidgets.QTextBrowser(Dialog)
        self.textBrowser.setGeometry(QtCore.QRect(70, 130, 371, 281))
        font = QtGui.QFont()
        font.setFamily("方正舒体")
        self.textBrowser.setFont(font)
        self.textBrowser.viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.IBeamCursor))
        self.textBrowser.setObjectName("textBrowser")
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(190, 440, 131, 51))
        font = QtGui.QFont()
        font.setFamily("Muyao-Softbrush")
        font.setPointSize(16)
        self.pushButton.setFont(font)
        self.pushButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushButton.clicked.connect(self.downloadSelectedNovel)
        self.pushButton.setObjectName("pushButton")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.exec_()

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "下载小说"))
        self.label.setText(_translate("Dialog", '秘籍: ' + self.novel_name))
        self.label_2.setText(_translate("Dialog", '作者: ' + self.novel_author))
        self.textBrowser.setHtml(_translate("Dialog",
                                            "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                                            "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                            "p, li { white-space: pre-wrap; }\n"
                                            "</style></head><body style=\" font-family:\'方正舒体\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
                                            f"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:12pt; font-style:italic;\">{'小说简介:' + self.novel_introduction + '(最后更新时间:' + self.novel_last_update_time + ')'}</span></p></body></html>"))
        self.pushButton.setText(_translate("Dialog", "获取秘籍!"))

    def downloadSelectedNovel(self):
        a_list = self.html.xpath('/html/body/div[3]/div[2]//a')
        novel_info_list = [self.novel_name]
        for a in a_list:
            chapter_url_1 = self.top_url + a.xpath('./@href')[0]
            novel_info_list.append(chapter_url_1)
            chapter_url_2 = chapter_url_1.split('.html')[0] + '_2' + '.html'
            novel_info_list.append(chapter_url_2)

        Ui_ProgressBarDialog(novel_info_list, QDialog()).setupUi()


class Ui_ProgressBarDialog(object):

    def __init__(self, novel_info_list, dialog):
        super().__init__()
        self.novel_info_list = novel_info_list
        self.task_num = len(self.novel_info_list) - 1
        self.dialog = dialog

    def setupUi(self):
        self.dialog.setObjectName("Dialog")
        self.dialog.setFixedSize(482, 530)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("pictures/txt_downloader_ico.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.dialog.setWindowIcon(icon)
        self.dialog.setStyleSheet("background-image: url(:/background/pictures/浅色纹理.jpg);")
        self.progressBar = QtWidgets.QProgressBar(self.dialog)
        self.progressBar.setRange(0, self.task_num)
        self.progressBar.setGeometry(QtCore.QRect(60, 320, 381, 41))
        self.progressBar.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setStyleSheet(
            "border: 2px solid grey; border-radius: 5px; color: #F44336; text-align:center; font-size:20px;\n"
            "font: 16pt \"Muyao-Softbrush\";")
        self.progressBar.setObjectName("progressBar")
        self.label = QtWidgets.QLabel(self.dialog)
        self.label.setGeometry(QtCore.QRect(10, 20, 461, 271))
        self.label.setStyleSheet("border-image: url(:/background/pictures/等待下载.jpg);")
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.dialog)
        self.label_2.setGeometry(QtCore.QRect(30, 400, 421, 81))
        self.label_2.setStyleSheet("font: 18pt \"Muyao-Softbrush\";\n"
                                   "text-decoration: underline;")
        self.label_2.setObjectName("label_2")

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self.dialog)
        download_novel_thread = DownloadNovelThread(self.novel_info_list)
        download_novel_thread.pd.progressbar_value.connect(self.callback)
        download_novel_thread.pd.task_done.connect(self.callback_)
        download_novel_thread.start()
        self.dialog.exec_()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.dialog.setWindowTitle(_translate("Dialog", "下载中"))
        self.label.setText(_translate("Dialog", "TextLabel"))
        self.label_2.setText(_translate("Dialog", "请耐心等待一会儿\n"
                                                  "马上完事儿ψ(｀∇´)ψ"))

    def callback(self, finished_task_num):
        self.progressBar.setValue(finished_task_num)

    def callback_(self):
        QMessageBox.information(QWidget(), '下载完毕', '希望您能愉快地度过一段与小说的时光!',
                                QMessageBox.Yes, QMessageBox.Yes)
        self.dialog.close()


class DownloadNovelThread(QThread):

    def __init__(self, novel_info_list):
        super().__init__()
        self.novel_info_list = novel_info_list
        self.pd = PbarDownloader()

    def run(self):
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        asyncio.get_event_loop().run_until_complete(
            self.pd.download_novel(self.novel_info_list))
