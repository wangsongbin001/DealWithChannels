#!/usr/bin/python
# coding=utf-8
import os

cmd = ['java -jar lib/walle-cli-all.jar batch -f channel.txt ',' ./channelPackages']
print('cmd', cmd);

#查找当前目录下的apk
# python3 : os.listdir()即可，这里使用兼容Python2的os.listdir('.')
for file in os.listdir('.'):
    if os.path.isfile(file):
        extension = os.path.splitext(file)[1][1:]
        #print('ex',extension)
        if extension == 'apk':
            strCmd = cmd[0] + file + cmd[1]
            print('cmd', strCmd);
            os.system(strCmd)
            print('successful！')