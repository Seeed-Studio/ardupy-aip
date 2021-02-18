
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


from pip._internal.cli.base_command import Command
from pip._internal.cli.req_command import RequirementCommand
from pip._internal.cli.status_codes import SUCCESS, ERROR
from pip._internal.cli import cmdoptions
from pip._internal.network.download import Downloader
from pip._internal.models.link import Link
from aip.parser import parser
from aip.logger import log
from aip.utils import dealGenericOptions

from pip._internal.operations.prepare import (
    unpack_url,
)
import os
import sys
from pathlib import Path
import platform
from aip.utils import SerialUtils
import time


class flashCommand(Command):
    """
    flash firmware to ArduPy board.
    """
    name = 'flash'
    usage = """
      %prog [options] <args> ..."""
    summary = "Flash firmware to ArduPy board."
    ignore_require_venv = True

    def __init__(self, *args, **kw):
        dealGenericOptions()
        super(flashCommand, self).__init__(*args, **kw)
        self.cmd_opts.add_option(
            '-p', '--port',
            dest='port',
            action='store',
            default="",
            help='The port of the ArduPy board.')

        self.cmd_opts.add_option(
            '-o', '--origin',
            dest='origin',
            action='store_true',
            default=False,
            help='flash latest version firmware')

        self.parser.insert_option_group(0, self.cmd_opts)
        self.serial = SerialUtils()
        self.port = ""

    @property
    def stty(self):

        if self.port == "":
            port, desc, hwid, isbootloader = self.serial.getAvailableBoard()
            self.port = port

        if self.port == "None":
            log.warning("please plug in a ArduPy Board!")
            print("<usage>    aip run [-p, --port=<port>] [local_file]")
            return "echo not support"

        if os.name == "posix":
            if platform.uname().system == "Darwin":
                return "stty -f " + self.port + " %d"
            return "stty -F " + self.port + " %d"
        elif os.name == "nt":
            return "MODE " + self.port + ":BAUD=%d PARITY=N DATA=8"

        return "echo not support"

    def run(self, options, args):

        if options.port == "":
            port, desc, hwid, isbootloader = self.serial.getAvailableBoard()
            self.port = port
        else:
            port = options.port
        
        if port == None:
            log.error("Sorry, the device you should have is not plugged in.")
            return ERROR
        
        board_id = self.serial.getBoardIdByPort(self.port)
        if parser.get_flash_isTouch_by_id(board_id):
            try_count = 0
            do_bossac = True
            while True:
                stty = self.stty
                print(stty)
                if stty != "echo not support":
                    os.system(stty % 1200)
                #os.system(str(bossac)+ " --help")
                time.sleep(1)
                port, desc, hwid, isbootloader = self.serial.getBootloaderBoard()
                if isbootloader == True:
                    self.port = port
                    break
                try_count = try_count + 1
                if port == None:
                    continue
                if try_count == 5:
                    do_bossac = False
                break

            if do_bossac == True:
                flash_tools = parser.get_flash_tool_by_id(board_id)
                #print(flash_tools)
                if len(args) != 0:
                    ardupybin = args[0]
                else:
                    ardupybin = str(Path(parser.get_deploy_dir_by_id(board_id), "Ardupy.bin"))
                flash_command = parser.get_flash_command_by_id(board_id, self.port, ardupybin)
                print(flash_tools + "/" + flash_command)
                os.system(flash_tools + "/" + flash_command)
            else:
                log.warning("Sorry, the device you should have is not plugged in.")
                return ERROR
        else:
            flash_tools = parser.get_flash_tool_by_id(board_id)
            ardupybin = ""
            if len(args)!=0:
                ardupybin = args[0]
            else:
                ardupybin = str(Path(parser.get_deploy_dir_by_id(board_id), "Ardupy.bin"))
            flash_command = parser.get_flash_command_by_id(board_id, self.port, ardupybin)
            print(flash_tools + "/" + flash_command)
            os.system(flash_tools + "/" + flash_command)
        return SUCCESS
