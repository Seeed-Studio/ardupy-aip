
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
import serial
import subprocess
import posixpath


class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""

    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty
        import sys

    def __call__(self):
        import sys
        import tty
        import termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


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
            print("port is necessary!")
            print("<usage>    aip ls -p, --port <port>")
            return ERROR

        _board = Pyboard(options.port)
        board_files = Files(_board)

        if platform.system() == "Windows":
            port = windows_full_port_name(port)

        for f in board_files.ls(options.directory, options.long_format, options.recursive):
            print(f)

        return SUCCESS


class replCommand(Command):
    """
    repl
    """
    name = 'repl'
    usage = """
      %prog [options] <package> ..."""
    summary = "repl."

    def __init__(self, *args, **kw):
        super(replCommand, self).__init__(*args, **kw)
        self.cmd_opts.add_option(
            '-p', '--port',
            dest='port',
            action='store',
            default="",
            help='The port of the ArduPy board.')

        self.parser.insert_option_group(0, self.cmd_opts)

    def run(self, options, args):

        print(
            '\033[31mSorry, this function is not implemented yet. Please look forward to the next version.')

        # if options.port == "":
        #     print("port is is necessary!")
        #     print("<usage>    aip repl -p, --port <port>")
        #     return ERROR

        # port = serial.Serial(port=options.port, baudrate=115200, bytesize=8, parity='E', stopbits=1, timeout=2)

        # while True:
        #     getch = _Getch()
        #     a = getch()
        #     port.write(bytes(a,encoding='utf-8'))

        return SUCCESS


class getCommand(Command):
    """
    get
    """
    name = 'get'
    usage = """
      %prog [options] <package> ..."""
    summary = "get"

    def __init__(self, *args, **kw):
        super(getCommand, self).__init__(*args, **kw)
        self.cmd_opts.add_option(
            '-p', '--port',
            dest='port',
            action='store',
            default="",
            help='The port of the ArduPy board.')

        self.parser.insert_option_group(0, self.cmd_opts)

    def run(self, options, args):

        if options.port == "":
            print("port is necessary!")
            print("<usage>    aip get -p, --port <port>  <remote_file>  <local_file>")
            return ERROR

        if args[0] == "":
            print("remote_file is necessary!")
            print("<usage>    aip get -p, --port <port>  <remote_file>  <local_file>")
            return ERROR

        remote_file_name = args[0]
        local_file_name = ""
        if len(args) >= 2:
            local_file_name = args[1]

        _board = Pyboard(options.port)
        board_files = Files(_board)

        if platform.system() == "Windows":
            port = windows_full_port_name(port)

        remote_file = board_files.get(remote_file_name)

        if local_file_name != "":
            local_file = open(local_file_name, "w")
            local_file.write(remote_file.decode("utf-8"))
        else:
            print(remote_file.decode("utf-8"))

        return SUCCESS


class putCommand(Command):
    """
    put
    """
    name = 'put'
    usage = """
      %prog [options] <package> ..."""
    summary = "put"

    def __init__(self, *args, **kw):
        super(putCommand, self).__init__(*args, **kw)
        self.cmd_opts.add_option(
            '-p', '--port',
            dest='port',
            action='store',
            default="",
            help='The port of the ArduPy board.')

        self.parser.insert_option_group(0, self.cmd_opts)

    def run(self, options, args):

        if options.port == "":
            print("port is necessary!")
            print("<usage>    aip put -p, --port <port>  <local_file>  <remote_file>")
            return ERROR

        if args[0] == "":
            print("lccal file is necessary!")
            print("<usage>    aip put -p, --port <port>  <local_file>  <remote_file>")
            return ERROR

        local_file_name = args[0]
        remote_file_name = ""
        if len(args) >= 2:
            remote_file_name = args[1]
        # Use the local filename if no remote filename is provided.

        if remote_file_name == "":
            remote_file_name = os.path.basename(os.path.abspath(local_file_name))

        _board = Pyboard(options.port)

        if platform.system() == "Windows":
            port = windows_full_port_name(port)

        if os.path.isdir(local_file_name):
            # Directory copy, create the directory and walk all children to copy
            # over the files.

            board_files = Files(_board)

            for parent, child_dirs, child_files in os.walk(local_file_name, followlinks=True):
                # Create board filesystem absolute path to parent directory.
                remote_parent = posixpath.normpath(
                    posixpath.join(remote_file_name, os.path.relpath(
                        parent, local_file_name))
                )
                try:
                    # Create remote parent directory.
                    board_files.mkdir(remote_parent)
                except DirectoryExistsError:
                    # Ignore errors for directories that already exist.
                    pass
                # Loop through all the files and put them on the board too.
                for filename in child_files:
                    with open(os.path.join(parent, filename), "rb") as infile:
                        remote_filename = posixpath.join(
                            remote_parent, filename)
                        board_files.put(remote_filename, infile.read())

        else:
            # File copy, open the file and copy its contents to the board.
            # Put the file on the board.
            with open(local_file_name, "rb") as infile:
                board_files = Files(_board)
                board_files.put(remote_file_name, infile.read())

        return SUCCESS
