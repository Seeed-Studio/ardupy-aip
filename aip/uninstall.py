
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
from urllib.parse import urlparse

from pip._internal.operations.prepare import (
    unpack_url,
)

import os
import stat
from aip.utils import readonly_handler
from aip.parser import parser
from aip.logger import log
from aip.utils import dealGenericOptions
import shutil
from pathlib import Path

class uninstallCommand(Command):
    """
    Uninstall ArduPy Library.
    """
    name = 'uninstall'
    usage = """
      %prog [options] <args> ..."""
    summary = "Uninstall ArduPy Library."
    ignore_require_venv = True

    def __init__(self, *args, **kw):
        dealGenericOptions()
        super(uninstallCommand, self).__init__(*args, **kw)
        pass
          
    def run(self, options, args):
        if len(args) == 0:
            log.warning("Please enter the name of the library!")
            log.info('Usage:\n\r    aip uninstall seeed-ardupy-ultrasonic-sensor')
            return ERROR

        moduledir = Path(parser.user_config_dir, "modules")
        for package in args:
                log.debug(package[package.find("/")+1:])
                if os.path.exists(str(Path(moduledir, package[package.find("/") + 1:]))):
                    shutil.rmtree(
                        str(Path(moduledir, package[package.find("/") + 1:])), onerror=readonly_handler)
                    log.info("Uninstall " + package + " succeeded.")
                else:
                    log.warning(package[package.find("/") +1:] + " not exists!")

        return SUCCESS





