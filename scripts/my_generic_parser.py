#!/usr/bin/env python3

from os.path import isdir
from pathlib import Path
from argparse import ArgumentParser, ArgumentTypeError, ArgumentError
from . import my_utils

def get_config_path(workspace_root):
    return my_utils.normalize_path(f"{workspace_root}/builder-config.txt")

class MyGenericParser:
    def __init__(self, parser: ArgumentParser, workspace_root):
        self.workspace_root = workspace_root
        self.parser = parser
        self.config_names = []
        self.config_names_dict = {} # names_dict[name] = name used for shortnames support
        self.config_values_from_file = {} # config_values[name] = value
        self.config_values_from_cmd_line = {} # config_values[name] = value

    # path might be relative or absolute
    # raise exception if the directory does not exist
    def to_abs(self, path):
        abspath = my_utils.make_path_absolute(self.workspace_root, path)
        if not isdir(abspath):
            raise ArgumentTypeError(f'Invalid directory: {path} => {abspath}')
        return abspath

    def add_config_argument_name(self, name, short_name = None):
        self.config_names.append(name)
        self.config_names_dict[name] = name
        if short_name is not None:
            self.config_names_dict[short_name] = name

    def write_config_file(self, ignore_current_file_content):
        config_file_abspath = get_config_path(self.workspace_root)
        path = Path(config_file_abspath)
        text = ""
        for arg_name in self.config_names:
            value = self.config_values_from_cmd_line.get(arg_name)
            if value is None and not ignore_current_file_content:
                value = self.config_values_from_file.get(arg_name)
            if value is not None:
                text = text + f'{arg_name} {value}\n'
        path.write_text(text)
        my_utils.builder_print(f'builder config written to: {config_file_abspath}')

    def _read_config_file(self):
        all_tokens_in_file = []
        config_file_abspath = get_config_path(self.workspace_root)
        try:
            all_tokens_in_file = my_utils.tokens_from_file(config_file_abspath)
        except FileNotFoundError:
            pass # no config file is perfectly ok

        config_values = {}
        iter_tokens = iter(all_tokens_in_file)
        for token in iter_tokens:
            name = self.config_names_dict.get(token)
            if name is not None:
                value = next(iter_tokens, None)
                if not value:
                    raise ArgumentError(name, f'in {config_file_abspath} expected one argument after {token}')
                existing_value = config_values.get(name)
                if existing_value is not None:
                    my_utils.builder_print_warning(f'Ignoring value {existing_value} for options for option {name}, as an other value has already be found ({existing_value}).')
                else:
                    config_values[name] = value

        self.config_values_from_file = config_values

    ## returns
    # not_config_arg_list : args that don't correspond to config entries
    # extra_arg_list      : args '---' and after
    def _parse_cmd_line_from_config(self, argv):
        not_config_arg_list = []
        extra_arg_list = []
        args = enumerate(argv)
        for i, arg in args:
            if arg == '---':
                extra_arg_list = argv[i:] # all remainings args are not arguments of the commands
                break

            name = self.config_names_dict.get(arg)
            if name is not None:
                _, value = next(args, None)
                if value is None:
                    raise ArgumentError(arg, f'in command line arguments expected one argument after {arg}')
                self.config_values_from_cmd_line[name] = value
            else:
                not_config_arg_list.append(arg)

        return not_config_arg_list, extra_arg_list

    # this also updates the config entries if they are overriden by the command line
    def parse_args_with_config_file(self, command_arg_list):
        self._read_config_file()

        # config_cmd_line_values[name] = value
        not_config_arg_list, extra_arg_list = self._parse_cmd_line_from_config(command_arg_list)
        config_arg_list = []
        for arg_name in self.config_names:
            value = self.config_values_from_cmd_line.get(arg_name) or self.config_values_from_file.get(arg_name)
            if value is not None:
                config_arg_list.extend((arg_name, value))

        completed_command_arg_list = not_config_arg_list + config_arg_list + extra_arg_list
        return self.parser.parse_args(completed_command_arg_list)

    # options not stored in config files
    def add_args_for_build_command(self):
        self.add_args_for_config_command()

        # target_choices = ['app', 'tests', 'all']
        # self.parser.add_argument('--target', '-t', nargs=1, default='all', type=str, metavar='<target>', choices=target_choices,
        #                          help='Target project to build (default is all)')

        config_choices = ['debug', 'release']
        self.parser.add_argument('--config', '-c', default='release', type=str, metavar='<configuration>',
                                 choices=config_choices, help='build configuration in debug or release (default is release)')
        self.parser.add_argument('--no_generate', '-ng', default=False, action='store_true', help='Prevent from generating the project files.')
        self.parser.add_argument('--no_build'   , '-nb', default=False, action='store_true', help='Prevent from building the project files.')
        self.parser.add_argument('--no_debug'   , '-nz', default=False, action='store_true', help='Prevent debug information ')
        self.parser.add_argument('--rebuild'    ,  '-r', default=False, action='store_true', help='Clean all output targets before build')
        self.parser.add_argument('--clean'      ,  '-x', default=False, action='store_true', help='Clean the build directory before running any build command')
        self.parser.add_argument('--verbose'    ,  '-v', default=False, action='store_true', help='run the command in verbose')

    def add_args_for_config_command(self, in_config_command=False):
        self.add_cmake_generator_option()
        self.add_app_name_option()
        self.add_lib_name_option()
        self.add_unit_tests_name_option()
        if in_config_command:
            # config specific option
            self.parser.add_argument('--clear', default=False, action='store_true', help='Shall we clear the existing file and keep only the provided options instead  of updating it?')
            self.parser.add_argument('--verbose', '-v', default=False, action='store_true', help='run the command in verbose')

    # options stored in config files
    def add_cmake_generator_option(self):
        name, short_name = '--generator', '-g'
        generator_choices = ["msvc14", "msvc15", "makefile"]
        generator_list = " ".join(generator_choices)
        self.parser.add_argument(name, short_name, metavar='<generator>',
                                 help=f"CMake generator shortname among ({generator_list})")
        self.add_config_argument_name(name, short_name)

    def add_app_name_option(self):
        name, short_name = '--app_name', '-a'
        self.parser.add_argument(name, short_name, metavar='<app-name>',
                                 help='The desired name of the application executable. default is \"my_app\"')
        self.add_config_argument_name(name, short_name)

    def add_lib_name_option(self):
        name, short_name = '--lib_name', '-l'
        self.parser.add_argument(name, short_name, metavar='<lib-name>',
                                 help='The desired name of the library. default is \"my_lib\"')
        self.add_config_argument_name(name, short_name)

    def add_unit_tests_name_option(self):
        name, short_name = '--unit_tests_name', '-u'
        self.parser.add_argument(name, short_name, metavar='<unit-test-name>',
                                 help='The desired name of the unit-tests executable. default is \"my_test\"')
        self.add_config_argument_name(name, short_name)
