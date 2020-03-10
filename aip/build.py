

from pip._internal.cli.base_command import Command
from pip._internal.cli.status_codes import SUCCESS,ERROR
from pip._internal.utils import appdirs

class buildCommand(Command):
    """
    Show information about one or more installed packages.

    The output is in RFC-compliant mail header format.
    """
    name = 'build'
    usage = """
      %prog [options] <package> ..."""
    summary = "build all of package"
    ignore_require_venv = True

    def __init__(self, *args, **kw):
        super(buildCommand, self).__init__(*args, **kw)
        self.cmd_opts.add_option(
            '-f', '--files',
            dest='files',
            action='store_true',
            default=False,
            help='Show the full list of installed files for each package.')

        self.parser.insert_option_group(0, self.cmd_opts)
        self.user_data_dir = appdirs.user_data_dir(appname = "aip")


    def run(self, options, args):
        print("sfsdf")
        print(self.user_data_dir)

        return SUCCESS




