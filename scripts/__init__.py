#!/usr/bin/env python3
# NOTE do not add code specific to python 3+ in this file, otherwise the python version check won't work if ran from python 2!

import sys
from os.path import abspath, normpath, dirname, expanduser, expandvars

# check python version >= 3.6
required_version = (3, 6)
if not (sys.version_info[0] >= required_version[0] and sys.version_info[1] >= required_version[1]):
    exit("pie requires python {}.{}+ (you are running {}.{})".format(
        required_version[0], required_version[1], sys.version_info[0], sys.version_info[1]))

# compute pie_root once for the package
# not using utils.normalize_path(), because utils is python3 and this file has to be python 2 compatible
pie_root = dirname(abspath(__file__)).replace("\\", "/")
