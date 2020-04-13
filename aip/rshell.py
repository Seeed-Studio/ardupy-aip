
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

from pip._internal.operations.prepare import (
    _copy_source_tree,
    _download_http_url,
    unpack_url,
)

import os
import sys
from pygit2 import clone_repository
from pygit2 import Repository
from aip.variable import *
import shutil
from pathlib import Path
from rshell import main as rsh
import argparse
from aip.serialUtils import SerialUtils




class rshellCommand(RequirementCommand):
    """
    Show information about one or more installed packages.

    The output is in RFC-compliant mail header format.
    """
    name = 'rshell'
    usage = """
      %prog [options] <package> ..."""
    summary = ""
    ignore_require_venv = True
    port = ""

    def __init__(self, *args, **kw):
        super(rshellCommand, self).__init__(*args, **kw)
        default_baud = 115200
        default_port = os.getenv('RSHELL_PORT')
        default_rts = os.getenv('RSHELL_RTS') or rsh.RTS
        default_dtr = os.getenv('RSHELL_DTR') or rsh.DTR
        default_user = os.getenv('RSHELL_USER') or 'micro'
        default_password = os.getenv('RSHELL_PASSWORD') or 'python'
        default_editor = os.getenv('RSHELL_EDITOR') or os.getenv('VISUAL') or os.getenv('EDITOR') or 'vi'
        default_color = sys.stdout.isatty()
        default_nocolor = not default_color
        self.cmd_opts.add_option(
            "-b", "--baud",
            dest="baud",
            action="store",
            type=int,
            help="Set the baudrate used (default = %d)" % default_baud,
            default=default_baud
        )
        self.cmd_opts.add_option(
            "--buffer-size",
            dest="buffer_size",
            action="store",
            type=int,
            help="Set the buffer size used for transfers "
                "(default = %d for USB, %d for UART)" %
                (rsh.USB_BUFFER_SIZE, rsh.UART_BUFFER_SIZE),
        )
        self.cmd_opts.add_option(
            "-p", "--port",
            dest="port",
            help="Set the serial port to use (default '%s')" % default_port,
            default=default_port
        )
        self.cmd_opts.add_option(
            "--rts",
            dest="rts",
            help="Set the RTS state (default '%s')" % default_rts,
            default=default_rts
        )
        self.cmd_opts.add_option(
            "--dtr",
            dest="dtr",
            help="Set the DTR state (default '%s')" % default_dtr,
            default=default_dtr
        )
        self.cmd_opts.add_option(
            "-u", "--user",
            dest="user",
            help="Set username to use (default '%s')" % default_user,
            default=default_user
        )
        self.cmd_opts.add_option(
            "-w", "--password",
            dest="password",
            help="Set password to use (default '%s')" % default_password,
            default=default_password
        )
        self.cmd_opts.add_option(
            "-e", "--editor",
            dest="editor",
            help="Set the editor to use (default '%s')" % default_editor,
            default=default_editor
        )
        self.cmd_opts.add_option(
            "--file",
            dest="filename",
            help="Specifies a file of commands to process."
        )
        self.cmd_opts.add_option(
            "-d", "--debug",
            dest="debug",
            action="store_true",
            help="Enable debug features",
            default=False
        )
        self.cmd_opts.add_option(
            "-n", "--nocolor",
            dest="nocolor",
            action="store_true",
            help="Turn off colorized output",
            default=default_nocolor
        )
        self.cmd_opts.add_option(
            "-l", "--list",
            dest="list",
            action="store_true",
            help="Display serial ports",
            default=False
        )
        self.cmd_opts.add_option(
            "-a", "--ascii",
            dest="ascii_xfer",
            action="store_true",
            help="ASCII encode binary files for transfer",
            default=False
        )
        self.cmd_opts.add_option(
            "--wait",
            dest="wait",
            type=int,
            action="store",
            help="Seconds to wait for serial port",
            default=0
        )
        self.cmd_opts.add_option(
            "--timing",
            dest="timing",
            action="store_true",
            help="Print timing information about each command",
            default=False
        )
        self.cmd_opts.add_option(
            "--cmd",
            dest="cmd",
            type=str,
            action="store",
            help="Optional command to execute"
        )


        self.parser.insert_option_group(0, self.cmd_opts)

        index_opts = cmdoptions.make_option_group(
            cmdoptions.index_group,
            self.parser,
        )

        self.parser.insert_option_group(0, index_opts)
        self.serial = SerialUtils()


    def run(self, options, args):

        save_settings = None
        stdin_fd = -1
        try:
            import termios
            stdin_fd = sys.stdin.fileno()
            save_settings = termios.tcgetattr(stdin_fd)
        except:
            pass
        BUFFER_SIZE = 512
        if options.buffer_size is not None:
            BUFFER_SIZE = options.buffer_size


        try:
            print("Debug = %s" % options.debug)
            print("Port = %s" % options.port)
            print("Baud = %d" % options.baud)
            print("User = %s" % options.user)
            print("Password = %s" % options.password)
            print("Wait = %d" % options.wait)
            print("List = %d" % options.list)
            print("nocolor = %d" % options.nocolor)
            print("ascii = %d" % options.ascii_xfer)
            print("Timing = %d" % options.timing)
            print("Quiet = %d" % options.quiet)
            print("BUFFER_SIZE = %d" % BUFFER_SIZE)
            print("Cmd = [%s]" % options.cmd)
            global ASCII_XFER
            ASCII_XFER = options.ascii_xfer
            RTS = options.rts
            DTR = options.dtr

            if options.list:
                rsh.listports()
                return

            if options.port:
                self.port = options.port
            else:
                port, desc, hwid, isbootloader = self.serial.getAvailableBoard()
                self.port = port
                
            rsh.ASCII_XFER = True
            try:
                rsh.connect(self.port, baud=options.baud, wait=options.wait, user=options.user, password=options.password)
            except rsh.DeviceError as err:
                    print(err)

            rsh.autoconnect()

            if options.filename:
                with open(options.filename) as cmd_file:
                    shell = rsh.Shell(stdin=cmd_file, filename=options.filename, timing=options.timing)
                    shell.cmdloop('')
            else:
                cmd_line = options.cmd
                if cmd_line == None:
                    print('Welcome to rshell.', rsh.EXIT_STR)
                if rsh.num_devices() == 0:
                    print('')
                    print('No MicroPython boards connected - use the connect command to add one')
                    print('')
                shell = rsh.Shell(timing=options.timing)
                try:
                    shell.cmdloop(cmd_line)
                except KeyboardInterrupt:
                    print('')

        finally:
            if save_settings:
                termios.tcsetattr(stdin_fd, termios.TCSANOW, save_settings)