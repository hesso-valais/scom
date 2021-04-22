# -*- coding: utf-8 -*-

import sys
import os

WORKING_DIRECTORY = os.path.dirname(__file__)

# Add additional paths allowing to correctly import local modules
sys.path.insert(0, os.path.abspath(os.path.join(WORKING_DIRECTORY, '.')))
sys.path.insert(0, os.path.abspath(os.path.join(WORKING_DIRECTORY, '../../../src')))


def update_working_directory():
    # Change working directory to folder where the test file is located
    os.chdir(WORKING_DIRECTORY)

