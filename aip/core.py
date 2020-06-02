
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
    _download_http_url,
    unpack_url,
)

import os
from aip.utils import readonly_handler
from aip.utils import dealGenericOptions
from aip.utils import parser
from aip.logger import log
import shutil
import json
from pathlib import Path
import time

class coreCommand(RequirementCommand):
    """
    Ardupy Core opration.
    """
    name = 'core'
    usage = """
      %prog [options] <args> ..."""
    summary = "Ardupy Core opration."
    ignore_require_venv = True

    def __init__(self, *args, **kw):
        dealGenericOptions()
        super(coreCommand, self).__init__(*args, **kw)

        index_opts = cmdoptions.make_option_group(
            cmdoptions.index_group,
            self.parser,
        )


    def downloadAll(self, session):
        board_id = 0
        archiveFile = parser.get_archiveFile_by_id(board_id)
        downloader = Downloader(session, progress_bar="on")
        ardupycoredir = str(Path(parser.user_config_dir, 'ardupycore', archiveFile['package'], archiveFile['version']))
        if os.path.exists(str(Path(parser.user_config_dir, 'ardupycore', archiveFile['package']))):
            if not os.path.exists(ardupycoredir):
                shutil.rmtree(str(Path(parser.user_config_dir, 'ardupycore', archiveFile['package'])), onerror=readonly_handler)
                time.sleep(1)
                os.makedirs(ardupycoredir)
                log.info('Downloading ' + archiveFile['archiveFileName'] + '...')
                try:
                    unpack_url(
                        Link(archiveFile['url']),
                        ardupycoredir,
                        downloader=downloader,
                        download_dir=None,
                    )
                except Exception as e:
                    log.error(e)
                    os.remove(ardupycoredir)
        else:
            os.makedirs(ardupycoredir)
            log.info('Downloading ' + archiveFile['archiveFileName'])
            try:
                unpack_url(
                    Link(archiveFile['url']),
                    ardupycoredir,
                    downloader=downloader,
                    download_dir=None,
                )
            except Exception as e:
                log.error(e)
                os.remove(ardupycoredir)
        
        toolsDependencies = parser.get_toolsDependencies_url_by_id(board_id)
        for tool in toolsDependencies:
            tooldir = parser.get_tool_dir_byid(board_id)
            if not os.path.exists(tooldir):
                log.info('Downloading '+ tool['name'] + '...')
                os.makedirs(tooldir)
                try:
                    unpack_url(
                        Link(tool['url']),
                        tooldir,
                        downloader=downloader,
                        download_dir=None,
                        )
                except Exception as e:
                    log.error(e)
                    os.remove(tooldir)
          
    def run(self, options, args):
        session = self.get_default_session(options)
        self.downloadAll(session)
        return SUCCESS




