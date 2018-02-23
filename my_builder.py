#!/usr/bin/env python3.6

import os
import sys
from scripts import builder_main

if __name__ == '__main__':
    workspace_root = builder_main.my_utils.normalize_path(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(workspace_root)
    sys.exit(builder_main.main(workspace_root))
