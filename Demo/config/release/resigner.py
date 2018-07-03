# coding=utf-8

import subprocess
import json
import sys
import os
import locale

def execute(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = p.stdout.read().decode(locale.getpreferredencoding()).strip()
    ret = p.wait()
    if ret != 0:
        print(out)
    return (ret, out)

def getSigningConfig():
    storeFile = 'null'
    storePsd = 'null'
    keyAlas = 'null'
    keyPsd = 'null'
    sdkDir = 'null'
    try:
       proFile = open('..\\signing.properties','Ur')
       for line in proFile.readlines():
           line = line.strip().replace('\n','')
           if line.find('#') != -1:
              line = line[0:line.find('#')]
           if line.find('=') > 0:
              strs = line.split('=')
              if strs[0] == 'STORE_FILE':
                  storeFile = strs[1]
              elif strs[0] == 'STORE_PASSWORD':
                  storePsd = strs[1]
              elif strs[0] == 'KEY_ALIAS':
                  keyAlas = strs[1]
              elif strs[0] == 'KEY_PASSWORD':
                  keyPsd = strs[1]
              elif strs[0] == 'SDK_BUILD_TOOL_PATH':
                  sdkDir = strs[1]
       return (storeFile, storePsd, keyAlas, keyPsd, sdkDir)
    except Exception as e:
       raise e
    else:
       proFile.close()

if len(sys.argv) < 3:
    print('缺少参数，第一个参数为360.py文件路径，第二个参数为apk路径，第三个参数为渠道号')
    sys.exit(0)

apk_path = sys.argv[1].replace('/', '\\') # 原始apk路径
apk_name = os.path.split(apk_path)[1].replace('.apk', '')
print('apk_name', apk_name)
channel = sys.argv[2] # 渠道号
print('channel', channel)

#读取签名配置
storeFile, storePsd, keyAlas, keyPsd, sdkDir = getSigningConfig()
storeFile = storeFile.replace('/', '\\')
sdkDir = sdkDir.strip().replace('/', '\\').replace('\:', ':')
print(storeFile, storePsd, keyAlas, keyPsd, sdkDir)

if(storeFile == 'null' or storePsd == 'null' or keyAlas == 'null' or keyPsd == 'null'):
    print('signing.properties error')
    sys.exit(0)

# 从local.properties读取SDK目录
sdk_dir = ''
if sdkDir != 'null' and sdkDir.endswith('Sdk'):
   sdk_dir = sdkDir;
else:
   with open('..\\..\\local.properties', 'rt') as f:
       for line in f.readlines():
           if line.startswith('sdk.dir='):
               sdk_dir = line.replace('sdk.dir=', '').strip().replace('\:', ':')

tools_dir = sdk_dir + '\\build-tools\\'
l = os.listdir(tools_dir)
for d in l:
    if d.startswith('25'):
        tools_dir += d + "\\"
        break
else:
    print('build-tools没有25+版')
    sys.exit(0)
print('tools_dir',tools_dir)

# 对齐
apk_tmp = apk_name + '_tmp.apk'
ret, out = execute(tools_dir + 'zipalign -v 4 ' + apk_path + ' ' + apk_tmp)
print('align:', ret)

if ret == 0 and out.endswith('Verification succesful'):
    # v2签名
    signShell = tools_dir + 'apksigner sign --ks '+ storeFile +' --ks-key-alias '+ keyAlas + ' --ks-pass pass:'+ storePsd + ' --key-pass pass:' + keyPsd + ' ' + apk_tmp
    ret, out = execute(signShell)
    print('sign:', ret)
    # 检查v2签名
    ret, out = execute('java -jar lib\\CheckAndroidV2Signature.jar ' + apk_tmp)
    print('check-sign:', ret)
    isV2OK = json.loads(out)['isV2OK']
    print('isV2OK:', isV2OK)

    if ret == 0 and isV2OK:
        # 写入渠道号
        apk_result = apk_name + '_' + channel + '.apk'
        ret, out = execute('java -jar lib\\walle-cli-all.jar put -c ' + channel + ' ' + apk_tmp + ' ' + apk_result)
        print('write-channel:', ret)
        if ret == 0:
            # 显示渠道信息
            ret, out = execute('java -jar lib\\walle-cli-all.jar show ' + apk_result)
            print('show-channel:', ret)
            print(out)
            # 删除中间生成文件
            execute('del /q ' + apk_tmp)
