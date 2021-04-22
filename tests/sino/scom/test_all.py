#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import unittest

# Links of inspiration: http://stackoverflow.com/questions/1732438/how-to-run-all-python-unit-tests-in-a-directory

if __name__ == '__main__':
    test_files = glob.glob('test_*.py')
    module_strings = [test_file[0:len(test_file)-3] for test_file in test_files]
    suites = [unittest.defaultTestLoader.loadTestsFromName(test_file) for test_file in module_strings]
    test_suite = unittest.TestSuite(suites)
    test_runner = unittest.TextTestRunner().run(test_suite)
