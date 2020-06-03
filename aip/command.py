
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

from pip._internal.cli.parser import (
    ConfigOptionParser,
    UpdatingDefaultsHelpFormatter,
)
from functools import partial

from pip._internal.commands import get_similar_commands

from pip._internal.cli.status_codes import SUCCESS
from pip._internal.cli import cmdoptions
from pip._internal.exceptions import PipError
from pip._internal.exceptions import CommandError


from pip._internal.utils.misc import get_prog
from optparse import SUPPRESS_HELP, Option, OptionGroup
from pip._internal.locations import get_major_minor_version

from pip._internal.cli.status_codes import SUCCESS, ERROR
from pip._internal.cli.base_command import Command
from aip.build import buildCommand
from aip.install import installCommand
from aip.flash import flashCommand
from aip.shell import shellCommand
from aip.board import boardCommand
from aip.list import listCommand
from aip.uninstall import uninstallCommand
from aip import __version__

import sys
import os

###########
# options #
###########

help_ = partial(
    Option,
    '-h', '--help',
    dest='help',
    action='help',
    help='Show help.',
)  # type: Callable[..., Option]

version = partial(
    Option,
    '-V', '--version',
    dest='version',
    action='store_true',
    help='Show version and exit.',
)  # type: Callable[..., Option]

general_group = {
    'name': 'General Options',
    'options': [
        help_,
        version,
    ]
}  # type: Dict[str, Any]

class HelpCommand(Command):
    """Show help for commands"""
    name = 'help'
    usage = """
      %prog <command>"""
    summary = 'Show help for commands.'
    ignore_require_venv = True

    def run(self, options, args):
        from pip._internal.commands import get_similar_commands

        try:
            # 'pip help' with no args is handled by pip.__init__.parseopt()
            cmd_name = args[0]  # the command we need help for
        except IndexError:
            return SUCCESS

        if cmd_name not in commands_dict:
            guess = get_similar_commands(cmd_name)

            msg = ['unknown command "%s"' % cmd_name]
            if guess:
                msg.append('maybe you meant "%s"' % guess)

            raise CommandError(' - '.join(msg))

        command = commands_dict[cmd_name]()
        command.parser.print_help()
        return SUCCESS


commands_order = [
    buildCommand,
    listCommand,
    installCommand,
    uninstallCommand,
    flashCommand,
    boardCommand,
    shellCommand,
    HelpCommand,
]  # type: List[Type[Command]]

commands_dict = {c.name: c for c in commands_order}

def get_aip_version():
    version = 'aip ({}) - ArduPy Integrated Platform is a utility to develop ArduPy and interact witch ArduPy board.'

    return (
        version.format(
            __version__,
        )
    )

def create_main_parser():
    # type: () -> ConfigOptionParser
    """Creates and returns the main parser for aip's CLI
    """

    parser_kw = {
        'usage': '\n%prog <command> [options]',
        'add_help_option': False,
        'formatter': UpdatingDefaultsHelpFormatter(),
        'name': 'global',
        'prog': get_prog(),
    }

    parser = ConfigOptionParser(**parser_kw)
    parser.disable_interspersed_args()

    parser.version = get_aip_version()

    # add the general options
    gen_opts = cmdoptions.make_option_group(general_group, parser)
    parser.add_option_group(gen_opts)

    # so the help formatter knows
    parser.main = True  # type: ignore

    # create command listing for description
    description = [''] + [
        '%-27s %s' % (name, command_info.summary)
        for name, command_info in commands_dict.items()
    ]
    parser.description = '\n'.join(description)

    return parser


def parse_command(args):
    # type: (List[str]) -> Tuple[str, List[str]]
    parser = create_main_parser()

    # Note: parser calls disable_interspersed_args(), so the result of this
    # call is to split the initial args into the general options before the
    # subcommand and everything else.
    # For example:
    #  args: ['--timeout=5', 'install', '--user', 'INITools']
    #  general_options: ['--timeout==5']
    #  args_else: ['install', '--user', 'INITools']
    general_options, args_else = parser.parse_args(args)

    # --version
    if general_options.version:
        sys.stdout.write(parser.version)  # type: ignore
        sys.stdout.write(os.linesep)
        sys.exit()
  
    # pip || pip help -> print_help()
    if not args_else or (args_else[0] == 'help' and len(args_else) == 1):
        parser.print_help()
        sys.exit()

    # the subcommand name
    cmd_name = args_else[0]

    if cmd_name not in commands_dict:
        guess = get_similar_commands(cmd_name)

        msg = ['unknown command "{}"'.format(cmd_name)]
        if guess:
            msg.append('maybe you meant "{}"'.format(guess))

        raise CommandError(' - '.join(msg))

    # all the args without the subcommand
    cmd_args = args[:]
    cmd_args.remove(cmd_name)

    return cmd_name, cmd_args
