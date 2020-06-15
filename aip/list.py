
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
from aip.utils import dealGenericOptions
from aip.utils import output_package_listing_columns
from aip.parser import parser
import json

import os
import stat
from aip.logger import log
import shutil
from pathlib import Path

class listCommand(Command):
    """
    List installed ArduPy Libraries.

    Libraries are listed in a case-insensitive sorted order.
    """
    name = 'list'
    usage = """
      %prog [options] <args> ..."""
    summary = "List installed ArduPy Libraries."
    ignore_require_venv = True

    def __init__(self, *args, **kw):
        dealGenericOptions()
        super(listCommand, self).__init__(*args, **kw)

    def run(self, options, args):
        header = ["Library", "Version", "Location"]
        moduledir = Path(parser.user_config_dir, "modules")
        libs = []

        for library in os.listdir(moduledir):
            library_json_location = str(Path(moduledir,library,'library.json'))
            try:
                with open(library_json_location, 'r') as package_json:
                    package_json_dict = json.load(package_json)
                    lib = [library, package_json_dict['version'], package_json_dict['repository']['url']]
                    libs.append(lib)
            except Exception as e:
                e
                pass

        if len(libs) >= 1:
            output_package_listing_columns(libs, header)
        return SUCCESS


