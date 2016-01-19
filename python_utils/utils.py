#!/usr/bin/env python
# -*- coding=utf-8 -*-

'''
   Copyright (C) 2015 兜福工作室

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
'''

import re
import time
import os
import codecs

##################################################################################
''' html相关
'''
def getHtmlCharsetByFile(path, defaultCharset='utf-8'):
    with open(path, 'r') as fp:
        return getHtmlCharset(fp.read(), defaultCharset)

def getHtmlCharset(html, defaultCharset='utf-8'):
    cs = re.findall('<meta.+?charset=[^\w]*?([-\w]+)', html, re.IGNORECASE)+[defaultCharset]
    return cs[0]

##################################################################################
''' 字符串相关
'''
def toUnicode(text):
    if not isinstance(text, unicode):
        try:
            text = text.decode('utf-8', 'ignore')
        except UnicodeDecodeError:
            text = text.decode('gbk', 'ignore')
    return text

##################################################################################
''' 文件相关
'''
def getFiles(rootdir, recursive=False, suffix='*', bIgnoreHiddenFile=True):
    '''
    rootdir: 目录
    recursive: 是否递归查找
    suffix: 筛选文件扩展名
    bIgnoreHiddenFile: 忽略隐藏文件
    '''
    #paths = []
    if recursive:
        for root, dirs, files in os.walk(rootdir):
            if bIgnoreHiddenFile and os.path.basename(root).startswith('.'):
                continue
            for filename in files:
                if bIgnoreHiddenFile and (filename.startswith('.') or filename.endswith('~')):
                    continue
                if '*' == suffix or os.path.splitext(filename)[1][1:] == suffix:
                    path = os.path.join(root, filename)
                    #paths.append(os.path.abspath(path))
                    yield path
    else:
        for filename in os.listdir(rootdir):
            if bIgnoreHiddenFile and (filename.startswith('.') or filename.endswith('~')):
                continue
            if '*' == suffix or os.path.splitext(filename)[1][1:] == suffix:
                path = os.path.join(rootdir, filename)
                #paths.append(os.path.abspath(path))
                yield path
                #return paths

def getfilecount(path):
    '''通过shell方式,获取指定路径的文件个数,不包含文件夹.'''
    import subprocess
    cmd = 'ls -lR "%s" | grep "^-" | wc -l' % (path)
    count = 0
    try:
        ls = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        count = int(ls.stdout.read().strip())
    except:
        pass

    return count

def getfileencode(path, defaultencoding='utf-8'):
    encoding = defaultencoding
    with open(path, 'r') as fp:
        header = fp.read(3)
        if header == codecs.BOM_UTF8:
            encoding='utf_8_sig'
        elif header[:2] == codecs.BOM_LE:
            encoding='utf-16'
        elif header[:2] == codecs.BOM_BE:
            encoding='utf-16'
        return encoding

def transform_coding(inputpath, outputpath, inputcoding, outputcoding):
    with codecs.open(inputpath, 'r', inputcoding) as fpIn:
        with codecs.open(outputpath, 'w', outputcoding) as fpOut:
            fpIn.tell
            size = os.path.getsize(inputpath)
            for line in fpIn:
                #print '%d%%\r' %(1.0* fpIn.tell() / size * 100),
                fpOut.write(line)

def getchars(path, coding='utf8'):
    ''' 统计文件字符
    :param path:
    :param coding:
    :return:
    '''
    codes = {}
    totalfreq = 0
    with codecs.open(path, 'r', coding) as fp:
        for line in fp:
            for c in line.strip():
                freq = codes.get(c, 1)
                codes[c] = freq + 1
                totalfreq += 1.0

    for c, f in sorted(codes.iteritems(), key=lambda line: line[1], reverse=True):
        prop = f / totalfreq
        print u"%s(%5s)\t%8d\t%s\t%f" % (hex(ord(c)), c, f, '#' * int(100 * prop + 1), 100.0 * prop)

    # for i, c in enumerate([c for c, f in sorted(codes.iteritems(), key=lambda line: line[0]) if ord(c) >= 0x1000]):
    #     print hex(ord(c))
    # 所有字符按unicode顺序排列
    print [c for c, f in sorted(codes.iteritems(), key=lambda line: line[0])]

def unzip(zipfilepath, outputfilepath):
    '''直接解压文件到指定目录
    '''
    import zipfile
    print 'start extract file:', zipfilepath
    z = zipfile.ZipFile(zipfilepath, 'r')
    z.extractall(outputfilepath)
    z.close()
    print 'end extract....'

def unzip(zipfilepath, outputfilepath, coding='utf8', outputcoding='utf16'):
    '''解压文件，把文件按指定编码输出
    coding：压缩包里文件的编码
    outputcoding：解压后的文件编码
    '''
    import zipfile
    z = zipfile.ZipFile(zipfilepath, 'r')
    if not os.path.exists(outputfilepath):
        os.makedirs(outputfilepath)
    for name in z.namelist():
        buf = z.read(name);
        buf = buf.decode(coding)
        newpath = os.path.join(outputfilepath, name)
        newdir, newname = os.path.split(newpath)
        if not os.path.exists(newdir):
            os.makedirs(newdir)
        if newname == '':
            continue
        fp = codecs.open(newpath, 'w', outputcoding)
        fp.write(buf)
        fp.close()
    z.close();

##################################################################################
''' 时间相关
'''
def now():
    return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))


##################################################################################
''' 其他
'''

def domainHashCode(domain):
    ''' 域名hashcode，从larbin工程中提取的代码，
    通过域名的hashcode值保存网站内容
    hashcode最大为20000，larbin生成目录最大为1000.
    目录用d00000标识
    '''
    h = 0
    for c in domain:
        h = 37*h + ord(c)
        h &= 0xFFFFFFFF
    return h % 20000 % 1000






if __name__ == "__main__":

    path = '/home/zhaokun/IME/StatisticalLanguageModel/data/NLP.zip'
    ts = time.time()
    size = os.path.getsize(path)
    print "size:", size
    time1 = time.time()-ts
    print 'time:', time1

    import io
    ts = time.time()
    with open(path) as fp:
        fp.seek(0, io.SEEK_END)
        size = fp.tell()
        print "size:", size
    time2 = time.time()-ts
    print 'time:',time2

    print time1 - time2
