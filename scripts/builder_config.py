#!/usr/bin/env python3

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from .my_generic_parser import MyGenericParser
from . import my_utils

def main(workspace_root, command_argv, argv):
    desc = '''
builder config [options]     Create builder-config.txt to store options in a text file that will be read in subsequent calls to the builder

See 'builder config --help' for the list of options that can be stored in the config file.
'''

    parser = ArgumentParser('config', usage='builder config [options]', formatter_class=RawDescriptionHelpFormatter, description=desc)

    my_parser = MyGenericParser(parser, workspace_root)
    my_parser.add_args_for_config_command(in_config_command=True)
    args = my_parser.parse_args_with_config_file(command_argv)

    if args.verbose:
        my_utils.builder_print_command(workspace_root, argv)

    if args.clear is False:
        if not my_parser.config_values_from_cmd_line:
            my_utils.builder_print_error("no argument provided to the config command. In order to clear the config file, you can use the --clear option")
            return 1

    my_parser.write_config_file(args.clear)
    return 0
