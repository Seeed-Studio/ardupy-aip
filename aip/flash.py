
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
    _download_http_url,
    unpack_url,
)
import os
import sys
from pathlib import Path
import platform
from aip.utils import SerialUtils
from aip.utils import dealGenericOptions
from aip.variable import *
import time


class flashCommand(RequirementCommand):
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

        self.cmd_opts.add_option(
            '--flash',
            dest='flash',
            action='store',
            default=False,
            help='flash specific firmware')

        self.parser.insert_option_group(0, self.cmd_opts)

        index_opts = cmdoptions.make_option_group(
            cmdoptions.index_group,
            self.parser,
        )
        
        self.serial = SerialUtils()

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

        self.port = options.port
        bossacdir = str(Path(user_config_dir +"/ardupycore/Seeeduino/tools/bossac"))

        if not os.path.exists(bossacdir):
            os.makedirs(bossacdir)
        session = self.get_default_session(options)

        if sys.platform == "linux":
            link = Link(
                "http://files.seeedstudio.com/arduino/tools/i686-linux-gnu/bossac-1.9.1-seeeduino-linux.tar.gz")
        if sys.platform == "win32":
            link = Link(
                "http://files.seeedstudio.com/arduino/tools/i686-mingw32/bossac-1.9.1-seeeduino-windows.tar.bz2")
        if sys.platform == "darwin":
            link = Link(
                "http://files.seeedstudio.com/arduino/tools/x86_64-apple-darwin/bossac-1.8-48-gb176eee-i386-apple-darwin16.1.0.tar.gz")

        bossac = ""

        if platform.system() == "Windows":
            bossac = str(Path(bossacdir, "bossac.exe"))
        else:
            bossac = str(Path(bossacdir, "bossac"))

        if not os.path.exists(bossac):
            downloader = Downloader(session, progress_bar="on")
            unpack_url(
                link,
                bossacdir,
                downloader=downloader,
                download_dir=None,
            )

        try_count = 0
        do_bossac = True
        while True:
            stty = self.stty
            print(stty)
            if stty != "echo not support":
                os.system(stty % 1200)
            #os.system(str(bossac)+ " --help")
            port, desc, hwid, isbootloader = self.serial.getBootloaderBoard()
            print(port)
            time.sleep(1)
            if isbootloader == True:
                break
            try_count = try_count + 1
            if try_count == 5:
                do_bossac = False
                break

        if do_bossac == True:
            name, version, url = self.serial.getBoardByPort(port)
            ardupybin = ""
            if len(args) > 0:
                ardupybin = args[0]
                if not os.path.exists(ardupybin):
                    log.warning('The path of firmware didn\'t exists!')
                    return ERROR
            elif options.origin == True:
                firmwaredir = str(Path(user_config_dir +"/deploy/firmware/"+name.replace(' ', '_')))
                if not os.path.exists(firmwaredir):
                    os.makedirs(firmwaredir)
                ardupybin = str(Path(firmwaredir, "ardupy_laster.bin"))
                if not os.path.exists(ardupybin):
                    downloader = Downloader(session, progress_bar="on")
                    _download_http_url(
                        link=Link(url),
                        downloader=downloader,
                        temp_dir=firmwaredir,
                        hashes=None)
            else:
                ardupybin = str(Path(user_config_dir +"/deploy/Ardupy.bin"))

            _flash_parm = flash_param[name.replace(' ', '_')];
            print((str(bossac) + _flash_parm) % (port,  ardupybin))
            os.system((str(bossac) + _flash_parm) % (port,  ardupybin))
        else:
            log.warning("Sorry, the device you should have is not plugged in.")
            return ERROR

        return SUCCESS
