#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import os
import json
from PySide2.QtWidgets import QApplication, QMessageBox
from PySide2.QtUiTools import QUiLoader

serverIP = "127.0.0.1"
port = "8585"

class NetDisk:
    def __init__(self):
        # 从文件中加载UI定义
        # 从 UI 定义中动态 创建一个相应的窗口对象
        # 注意：里面的控件对象也成为窗口对象的属性了
        # 比如 self.ui.button , self.ui.textEdit
        self.ui = QUiLoader().load('ui/netDiskClientWdw.ui')
        self.ui.checkBTN.clicked.connect(self.checkNum)
        self.ui.loginBTN.clicked.connect(self.openNetDisk)
        self.ui.cancelBTN.clicked.connect(self.closeWdw)

    def checkNum(self):
        #本地检测输入内容是否合法
        stuID = self.ui.stuID.text()    #获取用户输入的ID
        self.ui.wrgTip.setText("")      #错误提示label初妈化为空字符
        print(stuID)
        if (len(stuID)<6):
            self.ui.wrgTip.setText("你输入的编号错误！")
            return ""
        else:
            self.ui.stuName.setText("show name")
            return stuID




    def closeWdw(self):
        netDisk.ui.close()

    def openNetDisk(self):
        # Disconnect anything on M
        subprocess.call(r'net use z: /del', shell=True)
        # Connect to shared drive, use drive letter M
        subprocess.call(r'net use z: \\localhost\d', shell=True)
        # 修改映射网络磁盘名称为学生姓名的个人空间
        str='reg add HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\MountPoints2\##localhost#d /v _LabelFromReg /d "***的个人空间" /f'
        subprocess.call(str,shell=True)

app = QApplication([])
netDisk = NetDisk()
netDisk.ui.show()
app.exec_()


'''
#创建映射网络磁盘，并命名
# Disconnect anything on M
subprocess.call(r'net use z: /del', shell=True)

# Connect to shared drive, use drive letter M
subprocess.call(r'net use z: \\localhost\d', shell=True)
str='reg add HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\MountPoints2\##localhost#d /v _LabelFromReg /d "换个名字" /f'
subprocess.call(str,shell=True)
'''