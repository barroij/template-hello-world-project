#!/usr/bin/env python3

# Disable R0911:Too many return statements due to yes builder_main is just a big switch as designed
# pylint: disable=R0911

import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter, ArgumentError
from .my_utils import builder_print_error
try:
    from . import builder_build, builder_config, builder_system_tests, builder_unit_tests, my_utils
except ModuleNotFoundError as e:
    builder_print_error(f'{e}: install required modules with command: `py -3 -m pip install -r scripts/builder/requirements.txt`')
    sys.exit(1)

main_desc = '''
Command
    'build'                   Generate/Build with Cmake
    'config'                  Create builder-config.txt to store options in a text file that will be read in subsequent calls to the builder

    'unit-tests'              Run the unit tests (requires the unit tests to have been built)
    'system-tests'            Run the system tests (requires the app to have been built)

    'help', '-h', '--help'    Print this help

    See 'builder <command> --help' for more information on a specific command.
'''

def main(workspace_root, sys_argv=None):
    sys_argv = sys_argv if sys_argv else sys.argv
    command_choices = ['help', 'build', 'config', 'unit-tests', 'system-tests', 'lint']

    main_parser = ArgumentParser(add_help=False, formatter_class=RawDescriptionHelpFormatter, description=main_desc)
    main_parser.add_argument('command', nargs='?', default='help', choices=command_choices, help='', metavar='<command>')

    argv = sys_argv[1:]
    args, command_argv = main_parser.parse_known_args(argv)

    try:
        if args.command in ('help', '-h'):
            return main_parser.print_help()

        if args.command == 'config':
            return builder_config.main(workspace_root, command_argv, argv)

        if args.command == 'build':
            return builder_build.main(workspace_root, command_argv, argv)

        if args.command == 'unit-tests':
            return builder_unit_tests.main(workspace_root, command_argv, argv)

        if args.command == 'system-tests':
            return builder_system_tests.main(workspace_root, command_argv, argv)

    except ArgumentError:
        # Same behavior than argparse for ArgumentError raised out of argparse
        print(f'{args.command}: error: {str(sys.exc_info()[1])}', file=sys.stderr)
        return 1

    raise NotImplementedError(f'Command `{args.command}` is not implemented!')
