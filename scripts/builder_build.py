#!/usr/bin/env python3

import os
import sys
import platform
import shutil
import stat
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import psutil
from .my_generic_parser import MyGenericParser
from . import my_utils
from . import cmake_utils

app_name = "my_app"
unit_test_name = "my_app_unit_test"

def set_generator_if_needed(args):
    args.current_system = platform.system()
    default_generators = {'Windows': 'msvc15', 'Linux': 'makefile', 'Darwin': 'makefile'}

    if not args.current_system in list(default_generators.keys()):
        my_utils.builder_print_error(f'The platform {args.current_system} is not supported by the builder')
        return 1

    if args.generator is None:
        if not args.current_system:
            my_utils.builder_print_error('The builder was unabled was determine the current system. Please provide a valid generator option.')
            return 1

        args.generator = default_generators.get(args.current_system)
        if not args.generator:
            my_utils.builder_print_error(f'No default generator defined for the current system {args.current_system} . Please provide a valid generator option.')
            return 1

    if args.current_system == 'Windows':
        if not args.generator.startswith('msvc'):
            my_utils.builder_print_error(f'For now only msvc generator are supported on Windows.')
            return 1

    if args.generator == 'makefile':
        if args.current_system == 'Windows':
            args.cmake_generator = "NMake Makefiles JOM"
            my_utils.builder_print_error(f'makefile is not supported for windows.')
            return 1
        else:
            args.cmake_generator = "Unix Makefiles"
    elif args.generator.startswith('msvc'):
        if args.generator == 'msvc14':
            args.cmake_generator = "Visual Studio 15 2017"
        elif args.generator == 'msvc15':
            args.cmake_generator = "Visual Studio 14 2015"
        else:
            my_utils.builder_print_error(f'unsupported generator {args.generator}.')
            return 1

        if sys.maxsize > 2**32:
            args.cmake_generator = args.cmake_generator + ' Win64'

    return 0

def kill_processed_if_needed(args):
    if not args.no_build or args.clean:
        # kill all instance of app or unitests
        for p in psutil.process_iter(attrs=["name", "exe", "cmdline"]):
            process_name = p.info['name']
            for name in [app_name, unit_test_name]:
                if name == process_name or \
                        p.info['exe'] and os.path.basename(p.info['exe']) == name or \
                        p.info['cmdline'] and p.info['cmdline'][0] == name:

                    my_utils.builder_print(f'killing process {process_name}')
                    p.kill()
    return 0

def create_or_delete_build_directories(args):
    def print_error(func, path, excinfo):
        error = True
        if not os.access(path, os.W_OK):
            # Is the error an access error ?
            os.chmod(path, stat.S_IWUSR)
            try:
                func(path)
                error = False
            except:
                pass

        if error:
            rpath = my_utils.make_path_relative(args.workspace_root, path)
            my_utils.builder_print_warning(f'Failed to delete file {rpath} : [{excinfo}]. ')

    if args.clean and os.path.exists(args.build_dir):
        shutil.rmtree(args.build_dir, onerror=print_error)

    if not os.path.exists(args.build_dir):
        os.makedirs(args.build_dir)

    return 0

def get_camke_path(args):
    args.cmake_path = my_utils.normalize_path(shutil.which('cmake'))
    if args.cmake_path is None:
        my_utils.builder_print_error(f'Cmake executable not found. Make sure it avaiblable in your PATH environment variable.')
        return 1

    if args.current_system != 'Windows' and not os.access(args.cmake_path, os.X_OK):
        my_utils.builder_print_error(f'Cmake file is not an executable.')
        return 1
    return 0


def main(workspace_root, command_argv, argv):
    desc = '''
builder make [options]     run cmake to generate and build solution

See 'builder make --help' for more information on this command.
'''
    parser = ArgumentParser('make', usage='builder make [options]', formatter_class=RawDescriptionHelpFormatter, description=desc)

    my_parser = MyGenericParser(parser, workspace_root)
    my_parser.add_args_for_build_command()
    args = my_parser.parse_args_with_config_file(command_argv)

    args.workspace_root = workspace_root

    args.build_dir = my_utils.normalize_path(f'{workspace_root}/build')
    args.app_build_dir = my_utils.normalize_path(f'{args.build_dir}/app')
    args.lib_build_dir = my_utils.normalize_path(f'{args.build_dir}/lib')
    args.tests_build_dir = my_utils.normalize_path(f'{args.build_dir}/tests')
    args.no_build = False if args.rebuild else args.no_build

    if args.app_name is None:
        args.app_name = "my_app"
    if args.lib_name is None:
        args.lib_name = "my_lib"
    if args.unit_tests_name is None:
        args.unit_tests_name = "my_tests"

    if args.verbose:
        my_utils.builder_print_command(workspace_root, argv)
        print(str(args).replace(', ', ', \n'))

    for f in [set_generator_if_needed,
              kill_processed_if_needed,
              create_or_delete_build_directories,
              set_generator_if_needed,
              get_camke_path]:
        error = f(args)
        if error != 0:
            return error

    if not args.no_generate:
        if cmake_utils.cmake_generate(args) != 0:
            return 1

    if not args.no_build:
        if cmake_utils.cmake_build(args) != 0:
            return 1

    return 0
