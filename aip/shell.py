##
# The MIT License (MIT)
#
# Copyright (c) 2016 Stefan Wendler
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

##
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
from pip._internal.network.download import Downloader
from pip._internal.models.link import Link

from pip._internal.operations.prepare import (
    unpack_url,
)

import os
import sys
from aip.variable import *
from mp import version
import serial
import shutil
from pathlib import Path
from mp import mpfshell as mpf
import argparse
from aip.utils import SerialUtils
from aip.utils import dealGenericOptions
import logging




class shellCommand(Command):
    """
    Integrated mpfshell for interaction with board.
    """
    name = 'shell'
    usage = """
      %prog [options] <package> ..."""
    summary = "Integrated mpfshell for interaction with board."
    ignore_require_venv = True
    port = ""
    
    def __init__(self, *args, **kw):
        dealGenericOptions()
        super(shellCommand, self).__init__(*args, **kw)
        self.cmd_opts.add_option(
            '-c', 
            '--command',
            dest='command',
            action='store',
            default=None,
            help='Execute given commands (separated by ;)')

        self.cmd_opts.add_option(
            '-s', 
            '--script',
            dest='script',
            action='store',
            default=None,
            help='Execute commands from file')

        self.cmd_opts.add_option(
            '-n', 
            '--noninteractive',
            dest='noninteractive',
            action='store_true',
            default=False,
            help="Non interactive mode (don't enter shell)")
        
        self.cmd_opts.add_option(
            '--nocolor',
            dest='nocolor',
            action='store_true',
            default=False,
            help="Disable color")
                
        self.cmd_opts.add_option(
            '--nohelp',
            dest='nohelp',
            action='store_true',
            default=False,
            help="Disable help")
        
        self.cmd_opts.add_option(
            '--nocache',
            dest='nocache',
            action='store_true',
            default=False,
            help="Disable nocache")
        
        self.cmd_opts.add_option(
            "--logfile",
            dest="logfile",
            default=None,
            help="Write log to file")
             
        self.cmd_opts.add_option(
            '--loglevel',
            dest='loglevel',
            action='store',
            default="INFO",
            help="Loglevel (CRITICAL, ERROR, WARNING, INFO, DEBUG)")
        
        self.cmd_opts.add_option(
            "--reset",
            action="store_true",
            default=False,
            help="Hard reset device via DTR (serial connection only)"
            )
        
        self.cmd_opts.add_option(
            "-o",
            "--open",
            dest="open",
            action="store",
            default=None,
            help="Directly opens board",
        )

        self.cmd_opts.add_option(
            '-p', '--port',
            dest='port',
            action='store',
            default="",
            help='The port of the ArduPy board.')

        self.parser.insert_option_group(0, self.cmd_opts)

  
    def run(self, options, args):
        
        if len(args) >= 1:
            port = args[0]
        else:
            port = None  

        ser = SerialUtils()
        if options.port == "":
            if port == None:
                port, desc, hwid, isbootloader = ser.getAvailableBoard()
        else:
            port = options.port

        format = "%(asctime)s\t%(levelname)s\t%(message)s"

        if options.logfile is not None:
            logging.basicConfig(format=format, filename=options.logfile, level=options.loglevel)
        else:
            logging.basicConfig(format=format, level=logging.CRITICAL)
        
        mpfs = mpf.MpFileShell(not options.nocolor, not options.nocache, options.reset, options.nohelp)

        if options.open is not None:
            if port is None:
                if not mpfs.do_open(options.open):
                    return ERROR
        else:
            print(
                "Positional argument ({}) takes precedence over --open.".format(
                    port
                )
            )
        if port is not None:
            mpfs.do_open(port)

        if options.command is not None:
            for acmd in "".join(options.command).split(";"):
                scmd = acmd.strip()
                if len(scmd) > 0 and not scmd.startswith("#"):
                    mpfs.onecmd(scmd)

        elif options.script is not None:

            f = open(options.script, "r")
            script = ""

            for line in f:

                sline = line.strip()

                if len(sline) > 0 and not sline.startswith("#"):
                    script += sline + "\n"

            if sys.version_info < (3, 0):
                sys.stdin = io.StringIO(script.decode("utf-8"))
            else:
                sys.stdin = io.StringIO(script)

            mpfs.intro = ""
            mpfs.prompt = ""

        if not options.noninteractive:

            try:
                mpfs.cmdloop()
            except KeyboardInterrupt:
                print("")
                
        return SUCCESS
        

