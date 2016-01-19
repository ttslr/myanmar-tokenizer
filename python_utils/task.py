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

from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool

'''
from multiprocessing import Pool   # 进程池，适合cpu密集型程序
from multiprocessing.dummy import Pool as ThreadPool # 线程池， 适合IO密集型程序
函数解释：
apply_async(func[, args[, kwds[, callback]]]) 它是非阻塞，
apply(func[, args[, kwds]])是阻塞的
close()    关闭pool，使其不在接受新的任务。
terminate()    结束工作进程，不在处理未完成的任务。
join()    主进程阻塞，等待子进程的退出， join方法要在close或terminate之后使用。
'''


class Task:
    def __init__(self, processes=10, userprocesses=False):
        '''
        :param processes: 进程（线程）数
        :param userprocesses: 是否使用进程，默认使用线程
        :return:
        '''
        self.__pool = Pool(processes) if userprocesses else ThreadPool(processes)

    def add_async(self, func, args=(), kwargs={}, callback=None):
        '''返回结果对象，需要通过get获取结果（堵塞）
        :param func:
        :param args:
        :param kwargs:
        :param callback:
        :return:
        '''
        result = self.__pool.apply_async(func, args, kwargs, callback)
        return result

    def add(self, func, args=(), kwargs={}, callback=None):
        '''堵塞，会返回执行结果
        :param func:
        :param args:
        :param kwargs:
        :param callback:
        :return:
        '''
        result = self.__pool.apply(func, args, kwargs, callback)
        return result

    def terminate(self):
        ''' 结束工作进程，不在处理未完成的任务。
        :return:
        '''
        self.__pool.terminate()

    def close(self):
        ''' 关闭pool，使其不在接受新的任务。
        :return:
        '''
        self.__pool.close()

    def join(self):
        '''主进程阻塞，等待子进程的退出， join方法要在close或terminate之后使用。
        :return:
        '''
        self.__pool.close()
        self.__pool.join()

    def map(self, func, iterable):
        '''堵塞，会返回执行结果
        map(sum, [(1, 2), (3, 4)]), 分别计算1+2， 3+4
        :param func:
        :param iterable:
        :return:
        '''
        result = self.__pool.map(func, iterable)
        return result
    def map_async(self, func, iterable):
        '''返回结果对象，需要通过get获取结果（堵塞）
        :param func:
        :param iterable:
        :return:
        '''
        result = self.__pool.map_async(func, iterable)
        return result


def test(userprocesses):
    task = Task(20, userprocesses)
    input = '/home/zhaokun/IME/StatisticalLanguageModel'
    for root, dirs, files in os.walk(input):
        for filename in files:
            ip = os.path.join(root, filename)
            op = ''
            task.add_async(work, (ip, op))

    task.join()

if __name__ == '__main__':
    import time
    import math
    import os
    def work(input, output):
        #print "work:", input
        try:
            open(input).read()
        except:
            pass

    print 'user processes:'
    st = time.time()
    test(True)
    print 'time:', time.time() - st

    print 'user processes:'
    st = time.time()
    test(False)
    print 'time:', time.time() - st

