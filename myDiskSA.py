#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SA stand-alone 单机版
'''
pyinstaller myDiskSA.py --noconsole --hidden-import PySide2.QtXml --icon="ui/xwLogo32.ico"
待解决问题
1. 密码如果也写入json，无法解决并发问题
2020查朋友圈 1.0版

20201122 2.0版
1. 解决密码登录问题，方案为每个id生成一个配置文件，从配置文件读取密码
2. 锁定ip，不能随意登录其他人账户
3. 程序设计班登录后，开启2个网络空间。
4. 已打开个人空间，直接进入已开启的空间
5. 编号不正确的状态下，按登录按钮，程序报错
6. 解决图片无法显示问题（qrc文件二进制化，<pyside2-rcc logo.qrc -o logo.py >生成logo.py文件，并在项目中引用）

3.0版 待开发
已解决：图片显示问题
待解决：
1. 从配置文件中读取参数
2. 提升安全性，服务器端开启专用账户，通过用户名、密码访问网络空间

'''
import subprocess
import os
import time
import json
import socket
import ui.logo
# import sys
# from PySide2 import QtCore, QtGui, QtWidgets

from PySide2.QtWidgets import QApplication
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import QIcon


sevIP = "10.65.191.10"  # 10.65.191.10    192.168.31.198
teaIP = "10.65.164.51"      #教师机IP可以登录任何账户10.65.164.51
jsonPath = "\\\\" + sevIP + "\\Pzoneshare\\usr.json"


class NetDisk:
    def __init__(self):
        # 从文件中加载UI定义
        # 从 UI 定义中动态 创建一个相应的窗口对象
        # 注意：里面的控件对象也成为窗口对象的属性了
        # 比如 self.ui.button , self.ui.textEdit
        self.isLegal = False   #检查学生信息是否合法，初始认为不合法
        self.stuID = ""  # 学生编号
        self.stuName = ""  # 学生姓名
        self.stuBDIP = ""     #学生在JSON中记录的，允许登录的合法IP
        self.stuIsCT = False        #学生是否C++程序班成员
        self.stuPWD = ""        #学生登录密码
        self.stuDBPWD = ""      #学生在JSON中记录的密码
        self.stuIsLock = True   #默认锁定IP登录
        self.stuPCname = socket.getfqdn(socket.gethostname())  # 获取电脑名称 写入日志
        self.stuIP = socket.gethostbyname(self.stuPCname)  # 获取电脑IP地址   写入日志
        self.ui = QUiLoader().load('ui/netDiskClientWdw.ui')
        self.ui.checkBTN.clicked.connect(self.checkNum)
        self.ui.loginBTN.clicked.connect(self.goOpen)
        self.ui.cancelBTN.clicked.connect(self.closeWdw)
        self.ui.stuPWD.setVisible(False)
        self.ui.chgPWD.setVisible(False)
        # self.ui.logo.setStyleSheet("image:url(：logo/xwLogo.png)")


    def showPWDCtrl(self):
        self.ui.stuPWD.setVisible(True)
        self.ui.chgPWD.setVisible(True)

    def hidePWDCtrl(self):
        self.ui.stuPWD.setVisible(False)
        self.ui.chgPWD.setVisible(False)

    def checkNum(self):
        # 本地检测输入内容是否合法
        self.stuID = self.ui.stuID.text()  # 获取用户输入的ID
        self.ui.wrgTip.setText("")  # 错误提示label初妈化为空字符
        print(self.stuID)
        if (len(self.stuID) < 6):
            self.ui.wrgTip.setText("你输入的编号错误！")
            return ""
        else:
            stuName = self.getName(self.stuID)
            self.ui.stuName.setText(stuName)
            self.isLegal = True
            print("when push checkname btn, show",self.checkIsCT())
            #如果是程序设计班成员，显示密码输入框
            if self.checkIsCT():
                self.showPWDCtrl()
            else:
                self.hidePWDCtrl()
            return self.stuID

    def getName(self, stuid):
        # 从JSON文件中获取编号的对应姓名
        data = self.readJsonFile()
        for k,v in data.items():
            if (k == stuid):
                print((v.get("stuname")))
                self.stuName = v.get("stuname")
                return self.stuName
        return "编号不正确"

    def writeLog(self):
        # 将编号、登录时间、登录电脑IP写入日志文件，每个学生一个日志文件，解决并发处理问题

        print(self.stuIP, self.stuPCname, self.stuID, self.stuName)
        # 格式化成2016-03-20 11:45:39形式
        dataT = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) )
        logPath = "\\\\" + sevIP + "\\Pzoneshare\\log\\" + self.stuID + ".log"
        with open(logPath, "a") as f:
            # 注注注 str这个变量不能随便用，估计是内置函数
            strLog = dataT +" "+ str(self.stuIP) +" "+ str(self.stuPCname) + '\n'
            # str.join(dataT,self.stuIP,self.stuPCname,'\n')
            print(strLog)
            f.write(strLog)

    def closeWdw(self):
        netDisk.ui.close()

    def goOpen(self):
        print("before open ",self.checkIsLock(),not self.checkIP())
        # IP锁定状态下，且IP与本机不匹配则无法登录
        if  self.checkIsLock() and not self.checkIP():
            self.ui.wrgTip.setText("你的电脑不允许登录该空间，请向老师申请！")
            return
        # 判断输出密码与JSON中的密码是否一致
        self.stuPWD=self.ui.stuPWD.text()
        self.getDBPWD()
        print("password ",self.stuPWD,self.stuDBPWD)
        if self.stuPWD!=self.stuDBPWD:
            self.ui.wrgTip.setText("你输入的密码不正确，请向老师查询！")
            return
        #进入开启流程
        if self.isLegal:
            self.openNetDisk()
            self.writeLog()

    def openNetDisk(self):
        # 获取学生编号和姓名
        # stuID = self.ui.stuID.text()
        # stuName = self.ui.stuName.text()
        # print("in openNetDisk id & name ", self.stuID, self.stuName)

        # 如果已经打开个人空间，先关闭，6秒后才能改其他姓名
        if os.path.exists('z:'):
            self.closeWdw()     #如果网络空间已开，暂时改为打开z盘窗口，关闭软件窗口。
            print("网络空间已开启")
            # 打开个人空间文件夹窗口
            os.startfile(r'z:\\')
            return
            # subprocess.call(r'net use z: /del', shell=True)
            # time.sleep(6)

        path = '\\' + self.stuID[0:2] + '\\' + self.stuID[0:4] + '\\' + self.stuID
        # print(path)
        path = "\\\\" + sevIP + "\\Pzoneshare" + path
        print(path, os.path.exists(path))
        # 如果个人空间文件夹不存在，则创建文件夹（适用于新增学生）
        if os.path.exists(path) == False:
            os.makedirs(path)
        # Connect to shared drive, use drive letter M
        subprocess.call(r'net use z: ' + path, shell=True)
        # 修改映射网络磁盘名称为学生姓名的个人空间
        path2 = '#' + self.stuID[0:2] + '#' + self.stuID[0:4] + '#' + self.stuID
        str = 'reg add HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\MountPoints2\##' + sevIP + '#Pzoneshare' + path2 + ' /v _LabelFromReg /d "' + self.stuName + ' 的个人空间" /f'
        subprocess.call(str, shell=True)
        # 关闭软件窗口
        self.closeWdw()
        # 打开个人空间文件夹窗口
        os.startfile(r'z:\\')
        #程序设计班成员，多开启一个网络空间，指向资源文件夹
        if self.checkIsCT():
            cPath = "\\\\" + sevIP + "\\Pzoneshare\\CTeam"
            subprocess.call(r'net use y: ' + cPath, shell=True)
            cTeamStr = 'reg add HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\MountPoints2\##' + sevIP + '#Pzoneshare#CTeam'' /v _LabelFromReg /d "程序设计班资源库" /f'
            subprocess.call(cTeamStr, shell=True)

    def checkIP(self):
        #获取学生在JSON中存储的IP地址
        self.stuBDIP = ""
        print(self.stuID)
        result = self.readJsonFile()
        self.stuBDIP=result[self.stuID]["stuIP"]
        print(self.stuBDIP)
        if self.stuIP== self.stuBDIP or self.stuIP==teaIP:
            return True
        else:
            return False

    def readJsonFile(self):
        with open(jsonPath, 'r') as f:
            data = json.load(f, encoding="utf-8")
        f.close()
        return data

    def checkIsCT(self):
        #查询学生是否是程序设置班的成员
        result = self.readJsonFile()
        try:
            self.stuIsCT=result[self.stuID]["isCTeam"]
        except:
            self.stuIsCT=False
        print("isCTeam ",self.stuIsCT)
        return self.stuIsCT

    def checkIsLock(self):
        #查询学生是否是锁定电脑登录的状态
        result = self.readJsonFile()
        try:
            self.stuIsLock=result[self.stuID]["isLock"]
        except:
            self.stuIsLock=False
        print("stuIsLock ",self.stuIsLock)
        return self.stuIsLock

    def getDBPWD(self):
        #获取学生在Json中存储的密码
        result = self.readJsonFile()
        try:
            self.stuDBPWD=result[self.stuID]["stuPWD"]
        except:
            self.stuDBPWD=""
        print("stuBDPWD ",self.stuDBPWD)
        return self.stuDBPWD


app = QApplication([])
# 加载界面左上角小LOGO icon
app.setWindowIcon(QIcon('ui/xwLogo.jpg'))
# app.QLabel.logo.setStyleSheet("image:url(:/logo/xwLogo.png)")
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
