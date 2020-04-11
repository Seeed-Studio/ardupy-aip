
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
from pip._internal.cli import cmdoptions

import os
import sys
from pathlib import Path
import platform
import time
from aip.files import *
from aip.pyboard import *
from aip.serialUtils import windows_full_port_name
from aip.serialUtils import SerialUtils
import serial
import subprocess
import posixpath


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
            '-l', '--long_format',
            dest='long_format',
            action='store_true',
            default=False,
            help='long_format')

        self.cmd_opts.add_option(
            '-r', '--recursive',
            dest='recursive',
            action='store_true',
            default=False,
            help='recursive')

        self.parser.insert_option_group(0, self.cmd_opts)

    def run(self, options, args):

        ser = SerialUtils()
        if options.port == "":
            port, desc, hwid, isbootloader = ser.getAvailableBoard()
        else:
            port = options.port

        if port == "None":
            print("\033[93mplease plug in a ArduPy Board!\033[0m")
            print("<usage>    aip get -p, --port <port>  <remote_file>  <local_file>")
            return ERROR

        _board = Pyboard(port)

        board_files = Files(_board)

        directory = "/"
        if len(args) > 0:
            directory = args[0]

        for f in board_files.ls(directory, options.long_format, options.recursive):
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

        ser = SerialUtils()
        if options.port == "":
            port, desc, hwid, isbootloader = ser.getAvailableBoard()
        else:
            port = options.port

        if port == "None":
            print("\033[93mplease plug in a ArduPy Board!\033[0m")
            print("<usage>    aip get -p, --port <port>  <remote_file>  <local_file>")
            return ERROR

        _board = Pyboard(port)

        if len(args) == 0:
            print("remote_file is necessary!")
            print("<usage>    aip get -p, --port <port>  <remote_file>  <local_file>")
            return ERROR

        remote_file_name = args[0]
        local_file_name = ""
        if len(args) >= 2:
            local_file_name = args[1]

        board_files = Files(_board)

        remote_file = board_files.get(remote_file_name)

        if local_file_name != "":
            local_file = open(local_file_name, mode="wb", newline=None)
            local_file.write(remote_file)
            local_file.close()
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

        ser = SerialUtils()
        if options.port == "":
            port, desc, hwid, isbootloader = ser.getAvailableBoard()
        else:
            port = options.port

        if port == "None":
            print("\033[93mplease plug in a ArduPy Board!\033[0m")
            print(
                "<usage>    aip put -p, --port <port>  <local_file>  <remote_file>")
            return ERROR

        _board = Pyboard(port)

        if len(args) == 0:
            print("local file is necessary!")
            print("<usage>    aip put -p, --port <port>  <local_file>  <remote_file>")
            return ERROR

        local_file_name = args[0]
        remote_file_name = ""
        if len(args) >= 2:
            remote_file_name = args[1]
        # Use the local filename if no remote filename is provided.

        if remote_file_name == "":
            remote_file_name = os.path.basename(
                os.path.abspath(local_file_name))

        board_files = Files(_board)

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


class mkdirCommand(Command):
    """
    mkdir
    """
    name = 'mkdir'
    usage = """
      %prog [options] <package> ..."""
    summary = "mkdir"

    def __init__(self, *args, **kw):
        super(mkdirCommand, self).__init__(*args, **kw)
        self.cmd_opts.add_option(
            '-p', '--port',
            dest='port',
            action='store',
            default="",
            help='The port of the ArduPy board.')

        self.cmd_opts.add_option(
            '-e', '--exists',
            dest='exists',
            action='store_true',
            default=True,
            help='Ignore if the directory already exists')

        self.parser.insert_option_group(0, self.cmd_opts)

    def run(self, options, args):

        ser = SerialUtils()
        if options.port == "":
            port, desc, hwid, isbootloader = ser.getAvailableBoard()
        else:
            port = options.port

        if port == "None":
            print("\033[93mplease plug in a ArduPy Board!\033[0m")
            print(
                "<usage>    aip mkdir -p, --port <port> -e --exists <exists> <directory>")
            return ERROR

        _board = Pyboard(port)

        if len(args) == 0:
            print("directory is necessary!")
            print(
                "<usage>    aip mkdir -p, --port <port> -e --exists <exists> <directory>")
            return ERROR

        directory = args[0]

        board_files = Files(_board)

        board_files.mkdir(directory, exists_okay=options.exists)

        return SUCCESS


class rmCommand(Command):
    """
    rm
    """
    name = 'rm'
    usage = """
      %prog [options] <package> ..."""
    summary = "rm"

    def __init__(self, *args, **kw):
        super(rmCommand, self).__init__(*args, **kw)
        self.cmd_opts.add_option(
            '-p', '--port',
            dest='port',
            action='store',
            default="",
            help='The port of the ArduPy board.')

        self.parser.insert_option_group(0, self.cmd_opts)

    def run(self, options, args):

        ser = SerialUtils()
        if options.port == "":
            port, desc, hwid, isbootloader = ser.getAvailableBoard()
        else:
            port = options.port

        if port == "None":
            print("\033[93mplease plug in a ArduPy Board!\033[0m")
            print(
                "<usage>    aip rm -p, --port <port> <remote_file>")
            return ERROR

        _board = Pyboard(port)

        if len(args) == 0:
            print("remote file is necessary!")
            print(
                "<usage>    aip rm -p, --port <port> <remote_file>")
            return ERROR

        remote_file_name = args[0]

        board_files = Files(_board)

        board_files.rm(remote_file_name)

        return SUCCESS


class rmdirCommand(Command):
    """
    rmdir
    """
    name = 'rmdir'
    usage = """
      %prog [options] <package> ..."""
    summary = "rmdir"

    def __init__(self, *args, **kw):
        super(rmdirCommand, self).__init__(*args, **kw)
        self.cmd_opts.add_option(
            '-p', '--port',
            dest='port',
            action='store',
            default="",
            help='The port of the ArduPy board.')

        self.cmd_opts.add_option(
            '-m', '--missing',
            dest='missing_okay',
            action='store_true',
            default=True,
            help='Ignore if the directory does not exist.')

        self.parser.insert_option_group(0, self.cmd_opts)

    def run(self, options, args):

        ser = SerialUtils()
        if options.port == "":
            port, desc, hwid, isbootloader = ser.getAvailableBoard()
        else:
            port = options.port

        if port == "None":
            print("\033[93mplease plug in a ArduPy Board!\033[0m")
            print(
                "<usage>    aip rmdir -p, --port <port> -m --missing <directory>")
            return ERROR

        _board = Pyboard(port)

        if len(args) == 0:
            print("directory is necessary!")
            print(
                "<usage>    aip rmdir -p, --port <port> -m --missing <directory>")
            return ERROR

        directory = args[0]

        _board = Pyboard(port)
        board_files = Files(_board)

        board_files.rmdir(directory, missing_okay=options.missing_okay)

        return SUCCESS


class runCommand(Command):
    """
    run
    """
    name = 'run'
    usage = """
      %prog [options] <package> ..."""
    summary = "run"

    def __init__(self, *args, **kw):
        super(runCommand, self).__init__(*args, **kw)
        self.cmd_opts.add_option(
            '-p', '--port',
            dest='port',
            action='store',
            default="",
            help='The port of the ArduPy board.')

        self.cmd_opts.add_option(
            '-n', '--no-output',
            dest='no_output',
            action='store_true',
            default=False,
            help='Run the code without waiting for it to finish and print output.  Use this when running code with main loops that never return.')

        self.parser.insert_option_group(0, self.cmd_opts)

    def run(self, options, args):

        ser = SerialUtils()
        if options.port == "":
            port, desc, hwid, isbootloader = ser.getAvailableBoard()
        else:
            port = options.port

        if port == "None":
            print("\033[93mplease plug in a ArduPy Board!\033[0m")
            print(
                "<usage>    aip run -p, --port <port> <local_file>")
            return ERROR

        if len(args) == 0:
            print("local file is necessary!")
            print(
                "<usage>    aip run -p, --port <port> <local_file>")
            return ERROR

        local_file_name = args[0]

        _board = Pyboard(port)
        board_files = Files(_board)

        try:
            output = board_files.run(
                local_file_name, not options.no_output, not options.no_output)
            if output is not None:
                print(output.decode("utf-8"), end="")
        except IOError:
            print("Failed to find or read input file: {0}".format(
                local_file), err=True)

        return SUCCESS


class scanCommand(Command):
    """
    scan
    """
    name = 'scan'
    usage = """
      %prog [options] <package> ..."""
    summary = "scan"

    def __init__(self, *args, **kw):
        super(scanCommand, self).__init__(*args, **kw)
        self.cmd_opts.add_option(
            '-b', '--board',
            dest='board',
            action='store',
            default="",
            help='Scan the designated ardupy board.')

        self.cmd_opts.add_option(
            '-l', '--list',
            dest='list',
            action='store_true',
            default=False,
            help='List all available boards')

        self.parser.insert_option_group(0, self.cmd_opts)

    def run(self, options, args):

        ser = SerialUtils()

        if options.list == True:
            print(ser.listBoard())
            return SUCCESS

        if options.board == "":
            print(ser.listAvailableBoard())
        else:
            print(ser.listDesignatedBoard(options.board))

        return SUCCESS


class bvCommand(Command):
    """
    bv
    """
    name = 'bv'
    usage = """
      %prog [options] <package> ..."""
    summary = "bv"

    def __init__(self, *args, **kw):
        super(bvCommand, self).__init__(*args, **kw)
        self.cmd_opts.add_option(
            '-p', '--port',
            dest='port',
            action='store',
            default="",
            help='The port of the ArduPy board.')

        self.parser.insert_option_group(0, self.cmd_opts)

    def run(self, options, args):
        ser = SerialUtils()
        if options.port == "":
            port, desc, hwid, isbootloader = ser.getAvailableBoard()
        else:
            port = options.port

        if port == "None":
            print("\033[93mplease plug in a ArduPy Board!\033[0m")
            print(
                "<usage>    aip run -p, --port <port> <local_file>")
            return ERROR

        _board = Pyboard(port)

        print(_board.get_version())

        return SUCCESS
