
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
from pip._internal.commands.list import tabulate
from urllib.parse import urlparse

from pip._internal.operations.prepare import (
    _download_http_url,
    unpack_url,
)

from pip._internal.utils.misc import (
    dist_is_editable,
    get_installed_distributions,
    write_output,
)

import os
import stat
from aip.variable import *
from aip.command import *
from aip.logger import log
from aip.utils import dealGenericOptions
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

    def output_package_listing_columns(self, data, header):
        # insert the header first: we need to know the size of column names
        if len(data) > 0:
            data.insert(0, header)

        pkg_strings, sizes = tabulate(data)

        # Create and add a separator.
        if len(data) > 0:
            pkg_strings.insert(1, " ".join(map(lambda x: '-' * x, sizes)))

        for val in pkg_strings:
            write_output(val)

    def run(self, options, args):
        header = ["Packages", "Version", "Location"]
        moduledir = Path(user_config_dir, "modules")
        lists = []

        for library in os.listdir(moduledir):
            library_json_location = str(Path(moduledir,library,'library.json'))
            try:
                with open(library_json_location, 'r') as package_json:
                    package_json_dict = json.load(package_json)
                    lib = [library, package_json_dict['version'], package_json_dict['repository']['url']]
            except Exception as e:
                pass
            lists.append(lib)
        if len(lists) >= 1:
            self.output_package_listing_columns(lists, header)
        print("-------------------------------------------------------------------------------------\n")
        header = ["Boards", "Version", ""]
        lists = []
        for b in json_dict["board"]:
            lists.append([b["name"],b["version"],""])
        self.output_package_listing_columns(lists, header)
        return SUCCESS


