#!/usr/bin/env python3

# Disable E1101:Instance of 'URLError' has no 'headers|geturl' member'
# pylint: disable=E1101

import sys
from os.path import normpath, expanduser, expandvars, join
from pathlib import Path
import re

## generic utils

# ~/a/b/../${MYDIR} => /home/username/a/my_real_dir
def normalize_path(path):
    return str(Path(normpath(expanduser(expandvars(path)))))

def make_path_absolute(base_absdir, path):
    return normalize_path(join(base_absdir, path))

def make_path_relative(base_absdir, abs_path):
    return str(Path(abs_path).relative_to(base_absdir))

#### builder specific utils
def blank_line():
    print(flush=True)

def builder_blank_line():
    print(flush=True)

def builder_print(*args, **kwargs):
    kwargs.setdefault('flush', True)
    print('[builder]', *args, **kwargs)

def builder_print_warning(*args, **kwargs):
    builder_print('[warning]', *args, **kwargs)

def builder_print_error(*args, **kwargs):
    kwargs.setdefault('file', sys.stderr)
    builder_print('[ERROR]', *args, **kwargs)

def builder_print_wide_horizontal_separator(**kwargs):
    builder_print('========================================', **kwargs)

def builder_verbose_wide_horizontal_separator(verbose, **kwargs):
    if verbose:
        builder_print_wide_horizontal_separator(**kwargs)

def builder_print_horizontal_separator(**kwargs):
    builder_print('--------------------', **kwargs)

def builder_verbose_horizontal_separator(verbose, **kwargs):
    if verbose:
        builder_print_horizontal_separator(**kwargs)

def _join_quoted(cmd):
    quoted = []
    for a in cmd:
        s = str(a)
        # quote if space
        # quote '$', '%' to handle env vars. But do we really want to support env vars here ?
        if re.search(r'\s|\$|%', s):
            quoted.append('"{}"'.format(s))
        else:
            quoted.append(s)
    return ' '.join(quoted)

def builder_print_command(workspace_root, arg_list):
    builder_print(f'######## builder')
    cmd = [f'{workspace_root}/builder'] + arg_list
    builder_print(f'=> {_join_quoted(cmd)}')

def tokens_from_file(abspath: str):
    def _filter_comments(line):
        i = line.find('#')
        return line[:i] if i != -1 else line

    def filtered_lines(file_path: str):
        file_content = Path(file_path).read_text(encoding='utf-8', errors='surrogateescape')
        for line in file_content.splitlines():
            filtered_line = _filter_comments(line)
            if filtered_line:
                yield filtered_line.strip()

    def tokens_from_line(line: str):
        if not line:
            return []
        tokens = line.split()
        if not tokens:
            return []
        return [t.strip() for t in tokens]

    tokens = []
    for line in filtered_lines(abspath):
        tokens.extend(tokens_from_line(line))
    return tokens
