#!/usr/bin/env python
# -*- coding: utf-8 -*-


import unittest

from tests.sino.scom.paths import update_working_directory

update_working_directory()  # Needed when: 'pipenv run python -m unittest tests/cloudio/glue/{this_file}.py'


class TestScomBaseFrame(unittest.TestCase):
    """Tests BaseFrame class.
    """

    # @unittest.skip('because adding a new test')
    def test_cloudio_attribute_getter(self):
        from sino.scom.baseframe import BaseFrame

        base_frame = BaseFrame(buffer_size=64)

        ba1 = bytearray('\x01\x02\x03\x04', encoding='latin-1')

        base_frame.initialize_using_bytearray(ba1, len(ba1))

        result = base_frame.copy_buffer()
        self.assertEqual(result[0], 0x01)
        self.assertEqual(result[1], 0x02)
        self.assertEqual(result[2], 0x03)
        self.assertEqual(result[3], 0x04)

        ba2 = bytearray('\xAA\xBB\xCC\xDD', encoding='latin-1')

        # Must not throw an exception (OverflowError, etc.)
        base_frame.initialize_using_bytearray(ba2, len(ba2))

        result = base_frame.copy_buffer()
        self.assertEqual(result[0], 0xAA)
        self.assertEqual(result[1], 0xBB)
        self.assertEqual(result[2], 0xCC)
        self.assertEqual(result[3], 0xDD)
