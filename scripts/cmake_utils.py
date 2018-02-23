#!/usr/bin/env python3


import os
import time
import subprocess
import multiprocessing
from pathlib import Path
from . import my_utils


def get_cmake_set_command(var, value):
    if isinstance(value, str):
        return f"set({var} \"{value}\" CACHE STRING \"\" FORCE)\n"

    bool_value = "ON" if value else "OFF"
    return f"set({var} \"{bool_value}\" CACHE BOOL \"\" FORCE)\n"

def cmake_cache_init(args):
    content = "# CMake Initial Cache File\n# Auto Generated, no to be edited manually\n"
    content += "\n# CMake Global Properties\n"
    content += get_cmake_set_command("CMAKE_INSTALL_PREFIX", Path(args.workspace_root).as_posix())
    content += get_cmake_set_command("CMAKE_CONFIGURATION_TYPES", "debug;release")
    if args.generator == 'makefile':
        capitalized_config = args.config.capitalize()
        content += get_cmake_set_command("CMAKE_BUILD_TYPE", f"{capitalized_config}")
        content += get_cmake_set_command("CMAKE_RULE_MESSAGES", args.verbose)

    if args.current_system == 'Darwin':
        args.content += get_cmake_set_command("CMAKE_OSX_ARCHITECTURES", "x86_64")
    if args.generator == 'msvc14':
        # If building with VC14, requires targeting Windows 10 SDK
        content += get_cmake_set_command("CMAKE_SYSTEM_VERSION", "10.0")

    content += "\n# Build Properties\n"
    content += get_cmake_set_command("APP_NAME", args.app_name)
    content += get_cmake_set_command("LIB_NAME", args.lib_name)
    content += get_cmake_set_command("TESTS_NAME", args.unit_tests_name)

    content += get_cmake_set_command("APP_USE_DEBUG_INFO", not args.no_debug)

    current_dir = os.getcwd()
    cache_filename = my_utils.normalize_path(f'{current_dir}/cmake_initial_cache.cmake')
    path = Path(cache_filename)
    path.write_text(content)
    return cache_filename


def run_cmake(cmake_cmd_line, is_verbose):
    my_utils.builder_print("")
    my_utils.builder_print(f"Running command : {cmake_cmd_line}")

    start = time.clock()
    process = subprocess.Popen(cmake_cmd_line, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8', errors='surrogateescape')
    progress = []
    size = 50
    for i in range(0, size):
        p = ""
        for j in range(0, i):
            p+="."
        for j in range(i + 1, size):
            p += " "
        progress.append(p)

    i = 0
    for line in iter(process.stdout):
        if is_verbose:
           print(line, end='')
        else:
            p = progress[i % size]
            i = i+1
            print(f'\r{p}', end='\r')
    # here the stdout receiving EOF should occur almost at the same time as process exit, but let's still wait for for process completion
    process.wait()
    end = time.clock()
    s = end-start

    my_utils.builder_print("Done in % .2f seconds" % s)
    my_utils.builder_blank_line()
    return process.returncode

def go_to_build_dir(args):
    if not os.path.exists(args.build_dir):
        os.makedirs(args.build_dir)
    os.chdir(args.build_dir)

def cmake_generate(args):
    go_to_build_dir(args)
    # generate the projects
    cmake_cache_filename = cmake_cache_init(args)
    cmake_command_line = f"\"{args.cmake_path}\" -G \"{args.cmake_generator}\" -C \"{cmake_cache_filename}\" \"{args.workspace_root}\""
    error = run_cmake(cmake_command_line, args.verbose)
    os.chdir(args.workspace_root)
    return error


def cmake_build(args):
    go_to_build_dir(args)
    # generate the projects
    capitalized_config = args.config.capitalize()
    cmake_command_line = f"\"{args.cmake_path}\" --build . --config {capitalized_config}"
    if args.current_system == 'Windows' and args.generator.startswith('msvc'):
        cmake_command_line += " --target ALL_BUILD"
    else:
        cmake_command_line += " --target install"

    cmake_command_line += " --" # Additional compiler specific options
    if args.current_system == 'Windows':
        cmake_command_line += " /nologo"
        if args.generator.startswith('msvc'):
            cmake_command_line += " /p:WarningLevel=0  /maxcpucount  /nr:false  /verbosity:" + ("minimal" if args.verbose else "quiet")
    elif args.current_system == 'Darwin':
        pass
    elif args.current_system == 'Linux':
        if args.generator == "makefile":
            cpu_count = multiprocessing.cpu_count()
            cmake_command_line += f" -j {cpu_count}" + ("" if args.verbose else " -s")

    error = run_cmake(cmake_command_line, args.verbose)
    os.chdir(args.workspace_root)
    return error
