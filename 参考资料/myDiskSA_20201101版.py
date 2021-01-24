#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SA stand-alone 单机版

import subprocess
import os
import time
import json
from PySide2.QtWidgets import QApplication, QMessageBox
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import  QIcon

sevIP = "192.168.31.198"        #10.65.191.10

class NetDisk:
    def __init__(self):
        # 从文件中加载UI定义
        # 从 UI 定义中动态 创建一个相应的窗口对象
        # 注意：里面的控件对象也成为窗口对象的属性了
        # 比如 self.ui.button , self.ui.textEdit
        self.flag = False
        self.ui = QUiLoader().load('ui/netDiskClientWdw.ui')
        self.ui.checkBTN.clicked.connect(self.checkNum)
        self.ui.loginBTN.clicked.connect(self.isOpen)
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
            stuName = self.getName(stuID)
            self.ui.stuName.setText(stuName)
            self.flag = True
            return stuID

    def getName(self,stuid):
        #从JSON文件中获取编号的对应姓名
        with open('data.json','r') as f:
            data = json.load(f,encoding="utf-8")
            # print(data)
            for k,v in data.items():
                # print(k,v)
                if (k==stuid):
                    return v
            return "编号不正确"




    def closeWdw(self):
        netDisk.ui.close()

    def isOpen(self):
        if self.flag:
            self.openNetDisk()

    def openNetDisk(self):
        #获取学生编号和姓名
        stuID = self.ui.stuID.text()
        stuName = self.ui.stuName.text()
        print("in openNetDisk id & name " ,stuID,stuName)

        # 如果已经打开个人空间，先关闭，6秒后才能改其他姓名
        if os.path.exists('z:'):
            subprocess.call(r'net use z: /del', shell=True)
            time.sleep(6)

        path = '\\'+ stuID[0:2]+'\\'+stuID[0:4]+'\\'+stuID
        print(path)
        path="\\\\" + sevIP + "\\Pzoneshare" +path
        print(path, os.path.exists(path))
        #如果文件夹不存在，则创建文件夹
        if os.path.exists(path)==False:
            os.makedirs(path)
            print("two time",os.path.exists(path))
        # Connect to shared drive, use drive letter M
        subprocess.call(r'net use z: '+ path, shell=True)
        # 修改映射网络磁盘名称为学生姓名的个人空间
        path2 = '#'+ stuID[0:2]+'#'+stuID[0:4]+'#'+stuID
        print(path2)
        str='reg add HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\MountPoints2\##'+sevIP+'#Pzoneshare'+path2+' /v _LabelFromReg /d "'+stuName+' 的个人空间" /f'
        subprocess.call(str,shell=True)
        #关闭软件窗口
        self.closeWdw()
        #打开个人空间文件夹
        os.startfile(r'z:\\')

app = QApplication([])
# 加载 icon
app.setWindowIcon(QIcon('ui/xwLogo.jpg'))
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