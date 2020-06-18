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
import logging
import os.path
import time
from colorama import Fore, Style
import sys
import os
if os.name == "nt":
    os.system("")
 
 
class Logger(object):
    def __init__(self, logger):
        self.logger = logging.getLogger(name=logger)
        self.logger.setLevel(logging.DEBUG)  # critical > error > warning > info > debug

    def debug(self, msg):
        print(Fore.WHITE + str(msg) + Style.RESET_ALL)
 
    def info(self, msg):
        print(Fore.GREEN + str(msg) + Style.RESET_ALL)
 
    def warning(self, msg):
        self.logger.warning(Fore.YELLOW + str(msg) + Style.RESET_ALL)
 
    def error(self, msg):
        self.logger.error(Fore.RED + str(msg) + Style.RESET_ALL)
 
    def critical(self, msg):
        self.logger.critical(Fore.RED + str(msg) + Style.RESET_ALL)


log = Logger(logger="aip")