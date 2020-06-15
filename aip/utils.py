
# The MIT License (MIT)
# 
# Author: Baozhu Zuo (zuobaozhu@gmail.com)
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

import re
import os
import sys
import json
import demjson
import stat

from pip._internal.cli import cmdoptions
from functools import partial
from aip.parser import parser
from aip.logger import log
from optparse import Option
from pip._internal.commands.list import tabulate
from pip._internal.utils.misc import (
    dist_is_editable,
    get_installed_distributions,
    write_output,
)


board  = partial(
    Option,
    '-b', '--board',
    dest='board',
    action='store',
    default="",
    help='The name of the ArduPy board.',
)  # type: Callable[..., Option]

verbose = partial(
    Option,
    '-v', '--verbose',
    dest='verbose',
    action='count',
    default=0,
    help='Output compilation information'
)  # type: Callable[..., Option]


if os.name == 'nt':  # sys.platform == 'win32':
    from serial.tools.list_ports_windows import comports
elif os.name == 'posix':
    from serial.tools.list_ports_posix import comports
#~ elif os.name == 'java':
else:
    raise ImportError("Sorry: no implementation for your platform ('{}') available".format(os.name))
    

def readonly_handler(func, path, execinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def dealGenericOptions():
    cmdoptions.general_group['options'].insert(6, board)
    cmdoptions.general_group['options'].insert(1, verbose)
    cmdoptions.general_group['options'].remove(cmdoptions.isolated_mode)
    cmdoptions.general_group['options'].remove(cmdoptions.verbose)
    cmdoptions.general_group['options'].remove(cmdoptions.no_python_version_warning)

def windows_full_port_name(portname):
    # Helper function to generate proper Windows COM port paths.  Apparently
    # Windows requires COM ports above 9 to have a special path, where ports below
    # 9 are just referred to by COM1, COM2, etc. (wacky!)  See this post for
    # more info and where this code came from:
    # http://eli.thegreenplace.net/2009/07/31/listing-all-serial-ports-on-windows-with-python/
    m = re.match("^COM(\d+)$", portname)
    if m and int(m.group(1)) < 10:
        return portname
    else:
        return "\\\\.\\{0}".format(portname)



def output_package_listing_columns(data, header):
    # insert the header first: we need to know the size of column names
    if len(data) > 0:
        data.insert(0, header)
        pkg_strings, sizes = tabulate(data)
        # Create and add a separator.
        if len(data) > 0:
            pkg_strings.insert(1, " ".join(map(lambda x: '-' * x, sizes)))
        for val in pkg_strings:
            write_output(val)

class SerialUtils(object):
    def __init__(self):
        super().__init__()
        if len(parser.boards) == 0:
            log.error("Unable to find any ardupy boards, please refer to aip core!")
            sys.exit(1)
        
    
    def getAllPortInfo(self):
        return comports(include_links=False)

    
    def listAvailableBoard(self):
        list = []
        for info in self.getAllPortInfo():
            port, desc, hwid = info 
            ii = hwid.find("VID:PID")
            #hwid: USB VID:PID=2886:002D SER=4D68990C5337433838202020FF123244 LOCATION=7-3.1.3:1.
            #print(hwid)
            if ii != -1:
                for b in  parser.boards:
                    (vid, pid) = b["hwids"]["application"]
                    if vid == hwid[ii + 8: ii + 8 + 4] and pid == hwid[ii + 8 + 5 :ii + 8 + 5 + 4 ]:
                        #print(port,desc, hwid)
                        list.append({"port":port, "desc":desc, "hwid":hwid, "state":False})
                    (vid, pid) = b["hwids"]["bootloader"] 
                    if vid == hwid[ii + 8: ii + 8 + 4] and pid == hwid[ii + 8 + 5 :ii + 8 + 5 + 4 ]:
                        #print(port,desc, hwid)
                         list.append({"port":port, "desc":desc, "hwid":hwid, "state":True})

        return demjson.encode(list)
    
    def getBootloaderBoard(self):
        for info in self.getAllPortInfo():
            port, desc, hwid = info 
            ii = hwid.find("VID:PID")
            #hwid: USB VID:PID=2886:002D SER=4D68990C5337433838202020FF123244 LOCATION=7-3.1.3:1.
            #print(hwid)
            if ii != -1:
                for b in  parser.boards:
                    (vid, pid) = b["hwids"]["bootloader"]
                    if vid == hwid[ii + 8: ii + 8 + 4] and pid == hwid[ii + 8 + 5 :ii + 8 + 5 + 4 ]:
                        #print(port,desc, hwid)
                        return port,desc, hwid, True

        return None, None, None, None
    
    def getAvailableBoard(self):
        for info in self.getAllPortInfo():
            port, desc, hwid = info 
            ii = hwid.find("VID:PID")
            #hwid: USB VID:PID=2886:002D SER=4D68990C5337433838202020FF123244 LOCATION=7-3.1.3:1.
            #print(hwid)
            if ii != -1:
                for b in  parser.boards:
                    
                    (vid, pid) = b["hwids"]["application"]
                    if vid == hwid[ii + 8: ii + 8 + 4] and pid == hwid[ii + 8 + 5 :ii + 8 + 5 + 4 ]:
                        #print(port,desc, hwid)
                        return port,desc, hwid, False
                    (vid, pid) = b["hwids"]["bootloader"] 
                    if vid == hwid[ii + 8: ii + 8 + 4] and pid == hwid[ii + 8 + 5 :ii + 8 + 5 + 4 ]:
                        #print(port,desc, hwid)
                        return port,desc, hwid, True

        return None, None, None, None
    
    def listBoard(self):
        list = [];
        for b in  parser.boards:
           list.append(b["name"])
        return demjson.encode(list)
    
    def listDesignatedBoard(self, designated):
        list = []
        for info in self.getAllPortInfo():
            port, desc, hwid = info 
            ii = hwid.find("VID:PID")
            #hwid: USB VID:PID=2886:002D SER=4D68990C5337433838202020FF123244 LOCATION=7-3.1.3:1.
            #print(hwid)
            if ii != -1:
                for b in  parser.boards:
                    if b["name"] != designated:
                        continue
                    (vid, pid) = b["hwids"]["application"]
                    if vid == hwid[ii + 8: ii + 8 + 4] and pid == hwid[ii + 8 + 5 :ii + 8 + 5 + 4 ]:
                        #print(port,desc, hwid)
                        list.append({"port":port, "desc":desc, "hwid":hwid, "state":False})
                    (vid, pid) = b["hwids"]["bootloader"] 
                    if vid == hwid[ii + 8: ii + 8 + 4] and pid == hwid[ii + 8 + 5 :ii + 8 + 5 + 4 ]:
                        #print(port,desc, hwid)
                        list.append({"port":port, "desc":desc, "hwid":hwid, "state":True})

        return demjson.encode(list)
    
    def getDesignatedBoard(self, designated):
        
        for info in self.getAllPortInfo():
            port, desc, hwid = info 
            ii = hwid.find("VID:PID")
            #hwid: USB VID:PID=2886:002D SER=4D68990C5337433838202020FF123244 LOCATION=7-3.1.3:1.
            #print(hwid)
            if ii != -1:
                for b in  parser.boards:
                    if b["name"] != designated:
                        continue
                    (vid, pid) = b["hwids"]["application"]
                    if vid == hwid[ii + 8: ii + 8 + 4] and pid == hwid[ii + 8 + 5 :ii + 8 + 5 + 4 ]:
                        #print(port,desc, hwid)
                        return port,desc, hwid, False
                    (vid, pid) = b["hwids"]["bootloader"] 
                    if vid == hwid[ii + 8: ii + 8 + 4] and pid == hwid[ii + 8 + 5 :ii + 8 + 5 + 4 ]:
                        #print(port,desc, hwid)
                        return port,desc, hwid, True

        None
        
    def isBootloaderStatus(self):

        return True

    
    def getBoardByPort(self, _port):
        for info in self.getAllPortInfo():
            port, desc, hwid = info 

            if _port != port:
                continue

            ii = hwid.find("VID:PID")
            #hwid: USB VID:PID=2886:002D SER=4D68990C5337433838202020FF123244 LOCATION=7-3.1.3:1.
            #print(hwid)
            if ii != -1:
                for b in  parser.boards:
                    (vid, pid) = b["hwids"]["application"]
                    if vid == hwid[ii + 8: ii + 8 + 4] and pid == hwid[ii + 8 + 5 :ii + 8 + 5 + 4 ]:
                        return (b["name"], b["version"], b["firmware_url"])
                    (vid, pid) = b["hwids"]["bootloader"] 
                    if vid == hwid[ii + 8: ii + 8 + 4] and pid == hwid[ii + 8 + 5 :ii + 8 + 5 + 4 ]:
                        #print(port,desc, hwid)
                        return (b["name"], b["version"], b["firmware_url"])
        return ""
    
    def getBoardIdByPort(self, _port):
        for info in self.getAllPortInfo():
            port, desc, hwid = info 

            if _port != port:
                continue

            ii = hwid.find("VID:PID")
            #hwid: USB VID:PID=2886:002D SER=4D68990C5337433838202020FF123244 LOCATION=7-3.1.3:1.
            #print(hwid)
            if ii != -1:
                for b in  parser.boards:
                    (vid, pid) = b["hwids"]["application"]
                    if vid == hwid[ii + 8: ii + 8 + 4] and pid == hwid[ii + 8 + 5 :ii + 8 + 5 + 4 ]:
                        return (b["id"])
                    (vid, pid) = b["hwids"]["bootloader"] 
                    if vid == hwid[ii + 8: ii + 8 + 4] and pid == hwid[ii + 8 + 5 :ii + 8 + 5 + 4 ]:
                        #print(port,desc, hwid)
                        return (b["id"])
        return ""
    
    def getBoardIdByName(self, _name):

        for b in  parser.boards:
            if b["name"] == _name:
                return b["id"]
    
        return -1

    #  def getFirmwareByBoard(self, Board):
    #         for b in  parser.boards:
    #         (_vid, _pid) = b["application"]
    #         if (_vid, _pid) == (vid, pid):
    #              return (b["version"], b["Firmware_url"])
    #         (_vid, _pid) = b["bootloader"]
    #         if (_vid, _pid) == (vid, pid):
    #              return (b["version"], b["Firmware_url"])
    #     return ""

if __name__ == '__main__':
    ser = SerialUtils()
    for info in ser.getAllPortInfo():
        port, desc, hwid = info
        print("port: {}, desc: {}, hwid: {}".format(port, desc, hwid))
    print(ser.getAvailableBoard())
    print(ser.getDesignatedBoard("wio terminal"))
