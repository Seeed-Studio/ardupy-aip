
# from ._vendor import appdirs


import sys
import os
import locale

from .command import commands_dict,parse_command
from pip._internal.exceptions import PipError


from pip._internal.utils import deprecation
from pip._internal.cli.autocompletion import autocomplete
import importlib




def main(args=None):
     # type: (Optional[List[str]]) -> int
    if args is None:
        args = sys.argv[1:]

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

    module = importlib.import_module("aip."+cmd_name)
    command_class = getattr(module, cmd_name+"Command")
    command = command_class(name=cmd_name, summary="...")
    return command.main(cmd_args)



if __name__ == '__main__':
    main()

