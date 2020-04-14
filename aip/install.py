
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
import stat
from pygit2 import clone_repository
from pygit2 import Repository
from aip.variable import *
import shutil
from pathlib import Path


class installCommand(RequirementCommand):
    """
    Show information about one or more installed packages.

    The output is in RFC-compliant mail header format.
    """
    name = 'install'
    usage = """
      %prog [options] <package> ..."""
    summary = "install all of package"
    ignore_require_venv = True

    def __init__(self, *args, **kw):
        super(installCommand, self).__init__(*args, **kw)
        self.cmd_opts.add_option(
            '-r', '--remove',
            dest='uninstall',
            action='store_true',
            default=False,
            help='Install the aip package')
        
        self.cmd_opts.add_option(
            '-l', '--list',
            dest='list',
            action='store_true',
            default=False,
            help='list all the aip package')


        self.parser.insert_option_group(0, self.cmd_opts)

        index_opts = cmdoptions.make_option_group(
            cmdoptions.index_group,
            self.parser,
        )

        self.parser.insert_option_group(0, index_opts)

    def run(self, options, args):
        moduledir = Path(user_data_dir, "modules")
        if options.uninstall == True:
            for package in args:
                print(package[package.find("/")+1:])
                if os.path.exists(str(Path(moduledir, package[package.find("/") + 1:]))):
                    shutil.rmtree(str(Path(moduledir, package[package.find("/") + 1:])), onerror=readonly_handler)
                else:
                    print("\033[93m" + package[package.find("/")+1:] + " not exists\033[0m")
        elif options.list == True:
            print(os.listdir(moduledir))
        else:
            for package in args:
                print(package)
                if os.path.exists(str(Path(moduledir, package[package.find("/") + 1:]))):
                    shutil.rmtree(
                        str(Path(moduledir, package[package.find("/")+1:])))
                clone_repository("https://github.com/"+package,
                                 str(Path(moduledir, package[package.find("/")+1:])))
                repo = Repository(
                    str(Path(
                        str(Path(moduledir, package[package.find("/") + 1:])), '.git'))
                )
                repo.init_submodules()
                repo.update_submodules()
