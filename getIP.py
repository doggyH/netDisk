#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'doggy'

import os

path =os.getcwd()
print(path)
jsnPath=path+"\\data.json"
print(jsnPath)
print(os.path.exists(jsnPath))

logPath=path+"\\log"    #\\160101.log
print(os.path.exists(logPath))

global false,null,true
false=null=true=''
'''
出现NameError: name 'false' is not defined这个错误时，是因为在使用eval转化为字典时，中间的false，null等区分大小写导致。
global false, null, true
false = null = true = ''
result1 = eval(content)
在使用eval之前出现这个问题，应该这样处理。
'''
with open(jsnPath,"r") as fjs:
    jsStr=fjs.read()
    print("jsStr",type(jsStr))
    print(jsStr)
    jsDict=eval(jsStr)
    print(type(jsDict),jsDict)
fjs.close()

for root, ds, fs in os.walk(logPath):
    for f in fs:
        with open(logPath+"\\"+f ,"r") as ff:
            str=ff.readline()
            lst=str.split(" ")
            ip=lst[2]
            jsDict[f[:6]]["stuIP"]=ip;

# print(jsDict)
# print(type(jsDict))
# # wrStr=str(jsDict)
# with open(jsnPath,"r") as fjs:
#     fjs.write(wrStr)
