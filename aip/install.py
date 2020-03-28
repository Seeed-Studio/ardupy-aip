

from pip._internal.cli.base_command import Command
from pip._internal.cli.req_command import RequirementCommand
from pip._internal.cli.status_codes import SUCCESS,ERROR
from pip._internal.utils import appdirs
from pip._internal.cli import cmdoptions
from pip._internal.network.download import Downloader
from pip._internal.models.link import Link

from pip._internal.operations.prepare import (
    _copy_source_tree,
    _download_http_url,
    unpack_url,
)

import os
from pygit2 import clone_repository
from pygit2 import Repository

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
            '-a', '--ailes',
            dest='files',
            action='store_true',
            default=False,
            help='Show the full list of installed files for each package.')

        self.parser.insert_option_group(0, self.cmd_opts)
        self.user_data_dir = appdirs.user_data_dir(appname = "aip")

        index_opts = cmdoptions.make_option_group(
            cmdoptions.index_group,
            self.parser,
        )

        self.parser.insert_option_group(0, index_opts)


    def run(self, options, args):
        moduledir = self.user_data_dir + "/modules"
        for package in args:
            print(package)
            clone_repository("https://github.com/"+package, moduledir + package[package.find("/") : ])
            repo = Repository(path=moduledir + package[package.find("/") : ])
            repo.init_submodules()
            repo.update_submodules()            
        

