
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


import sys
import os
import locale
import json
from datetime import date, datetime
from pathlib import Path
import urllib.request
import shutil


from pip._internal.exceptions import PipError


from pip._internal.utils import deprecation
from pip._internal.cli.autocompletion import autocomplete
import importlib
#from aip.variable import *
from pip._internal.utils import appdirs


def main(args=None):

     # type: (Optional[List[str]]) -> int
    if args is None:
        args = sys.argv[1:]

    # is update package_seeeduino_ardupy_index.json
    user_data_dir = str(appdirs.user_data_dir(appname="aip"))
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir)
    today = date.today()
    user_data_dir_files = os.listdir(user_data_dir)
    current_package_seeeduino_ardupy = "xxxxx"
    is_update = True
    for files in user_data_dir_files:
        if files[0:30] == "package_seeeduino_ardupy_index":
            file_data = datetime.strptime(files[31:41], '%Y-%m-%d').date()
            current_package_seeeduino_ardupy = files
            if file_data == today:
                is_update = False
                break

    if is_update:
        if os.path.exists(str(Path(user_data_dir, current_package_seeeduino_ardupy))):
            os.remove(
                str(Path(user_data_dir, current_package_seeeduino_ardupy)))
        print("update latest package_seeeduino_ardupy_index.json ...")
        urllib.request.urlretrieve('https://files.seeedstudio.com/ardupy/package_seeeduino_ardupy_index.json',
                                   str(Path(user_data_dir, "package_seeeduino_ardupy_index_" + today.isoformat() + ".json")))

    from aip.command import commands_dict, parse_command
    from aip.variable import shell_commands

    # Configure our deprecation warnings to be sent through loggers
    deprecation.install_warning_logger()

    autocomplete()

    try:
        cmd_name, cmd_args = parse_command(args)
    except PipError as exc:
        sys.stderr.write("ERROR: {}".format(exc))
        sys.stderr.write(os.linesep)
        sys.exit(1)

    # Needed for locale.getpreferredencoding(False) to work
    # in pip._internal.utils.encoding.auto_decode
    try:
        locale.setlocale(locale.LC_ALL, '')
    except locale.Error as e:
        # setlocale can apparently crash if locale are uninitialized
        print("Ignoring error %s when setting locale", e)

    if cmd_name in shell_commands:
        module = importlib.import_module("aip.shell")
    else:
        module = importlib.import_module("aip."+cmd_name)

    command_class = getattr(module, cmd_name+"Command")
    command = command_class(name=cmd_name, summary="...")

    return command.main(cmd_args)


if __name__ == '__main__':
    main()
