# The MIT License (MIT)
#
# Author: Hontai Liu (lht856@foxmail.com)
#
# Copyright (C) 2020  Seeed Technology Co.,Ltd.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

#import inspect

class Log(object):

    str_error = '\033[31m{0}\033[0m' # red
    str_tips = '\033[32m{0}\033[0m' # yellow
    str_waring = '\033[33m{0}\033[0m' # yellow
    str_info = '\033[34m{0}\033[0m' # blue

    def __init__(self):
        pass

    def info(self, i):
        str_info  = self.str_info.format(i)
        print(str_info)
    
    def error(self, e):
        str_error  = self.str_error.format(e)
        print(str_error)
    
    def waring(self, w):
        str_waring  = self.str_waring.format(w)
        print(str_waring)
    
    def tips(self, t):
        str_tips  = self.str_tips.format(t)
        print(str_tips)
    
    # def __line__ (self):
    #     caller = inspect.stack()[1]
    #     return int (caller[2])

    # def __function__ (self):
    #     caller = inspect.stack()[1]
    #     return caller[3]

    # def __header__(self):
    #     header = ''
    #     header += ' Function: ' + str(self.__function__ ())
    #     header += ' Line: ' + str(self.__line__ ())
    #     return header

log = Log()