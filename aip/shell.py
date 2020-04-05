
# The MIT License (MIT)
#
# Author: Hongtai Liu (hongtai@foxmail.com)
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
from pip._internal.utils import appdirs
from pip._internal.cli import cmdoptions

import os
import sys
from pathlib import Path
import platform
import time
from .files import *
from .pyboard import *
from .serialUtils import windows_full_port_name

class lsCommand(Command):
    """
    List the contents of the specified directory (or root if none is
    specified).  Returns a list of strings with the names of files in the
    specified directory.  If long_format is True then a list of 2-tuples
    with the name and size (in bytes) of the item is returned.  Note that
    it appears the size of directories is not supported by MicroPython and
    will always return 0 (i.e. no recursive size computation).
    """
    name = 'ls'
    usage = """
      %prog [options] <package> ..."""
    summary = "ls."
    ignore_require_venv = True

    def __init__(self, *args, **kw):
        super(lsCommand, self).__init__(*args, **kw)
        self.cmd_opts.add_option(
            '-p', '--port',
            dest='port',
            action='store',
            default="",
            help='The port of the ArduPy board.')

        self.cmd_opts.add_option(
            '-d', '--directory',
            dest='directory',
            action='store',
            default="/",
            help='The directory of the ArduPy board.')

        self.cmd_opts.add_option(
            '-l', '--long_format',
            dest='long_format',
            action='store_true',
            default=True,
            help='long_format')
        
        self.cmd_opts.add_option(
            '-r', '--recursive',
            dest='recursive',
            action='store_true',
            default=False,
            help='recursive')

        self.parser.insert_option_group(0, self.cmd_opts)

    def run(self, options, args):
        
        if options.port == "":
            print("port is is necessary!")
            print("<usage>    aip ls -p, --port <port>")
            return ERROR

        _board = Pyboard(options.port)
        board_files = Files(_board)
    
        if platform.system() == "Windows":
            port = windows_full_port_name(port)

        for f in board_files.ls(options.directory, options.long_format, options.recursive):
            print(f)
            
        return SUCCESS
