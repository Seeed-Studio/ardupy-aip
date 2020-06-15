# The MIT License (MIT)
#
# Author: Hongtai Liu (lht856@foxmail.com)
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

from pip._internal.cli.base_command import Command
from pip._internal.cli.req_command import RequirementCommand
from pip._internal.cli.status_codes import SUCCESS, ERROR
from pip._internal.cli import cmdoptions

import os
import sys
from pathlib import Path
import platform
import time
from aip.utils import windows_full_port_name
from aip.utils import SerialUtils
from aip.utils import dealGenericOptions
import serial
import subprocess
import posixpath
from aip.logger import log

class boardCommand(Command):
    """
    Get basic information of ArduPy board. For example, board firmware 
    version information, currently connectable information
    """
    name = 'board'
    usage = """
      %prog [options] <args> ..."""
    summary = "Get basic information of ArduPy board."

    def __init__(self, *args, **kw):
        dealGenericOptions()
        super(boardCommand, self).__init__(*args, **kw)
        self.cmd_opts.add_option(
            '-s', '--scan',
            dest='scan',
            action='store_true',
            default=False,
            help='Scan all ArduPy board.')
        self.cmd_opts.add_option(
            '-d', '--desc',
            dest='desc',
            action='store',
            default="",
            help='Scan the designated ArduPy Board.'
        )

        self.cmd_opts.add_option(
            '-p', '--port',
            dest='port',
            action='store',
            default="",
            help='The port of the ArduPy board.')
        
        self.cmd_opts.add_option(
            '--baudrate',
            dest='baudrate',
            action='store',
            default="",
            help='The baudrate of the ArduPy board port.')

        self.cmd_opts.add_option(
            '-l', '--list',
            dest='list',
            action='store_true',
            default=False,
            help='List all available boards')
        
        self.cmd_opts.add_option(
            '-c', '--connect',
            dest='connect',
            action='store_true',
            default=False,
            help='Connect available boards')
        
        
        self.parser.insert_option_group(0, self.cmd_opts)
    
    def board_halt(self):

        buf = bytearray()

        for i in range(0, 3):
            i
            try:
                com = self.serial
                com.timeout = 1
                com.writeTimeout = 1
                com.write(b"\x03")
                time.sleep(1)
                com.write(b"\x02")
                time.sleep(0.05)
                lines = com.read(100)
                buf = buf + lines
                return buf
            except: 
                continue

        return None
    
    
    def get_version(self):

        buf = self.board_halt()
        #print(buf)
        ver = ""
        try:
            tmp = str(buf, "utf-8")
            #print(tmp)
            r = tmp.index("; Ardupy with seeed")
            ver = tmp[r - 10 : r]
        except:
            ver = "It's not an ardupy device!"
        
        return ver

    def run(self, options, args):

        ser = SerialUtils()

        if options.scan:
            if options.desc == "":
                print(ser.listAvailableBoard())
            else:
                print(ser.listDesignatedBoard(options.desc))
            return SUCCESS
        
        if options.list == True:
            print(ser.listBoard())
            return SUCCESS
        
       

        if options.port == "":
            port, desc, hwid, isbootloader = ser.getAvailableBoard()
        else:
            port = options.port

        if port == None:
            log.error("Sorry, the device you should have is not plugged in.")
            return ERROR
        
        try:
            if options.baudrate != "":
                baudrate  = int(options.baudrate)
            else:
                baudrate = 115200
            
            self.serial = serial.Serial(port, baudrate=baudrate, interCharTimeout=1)

            print(self.get_version())
        except Exception as e:
            log.error(e)
            return ERROR

        return SUCCESS


