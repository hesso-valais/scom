#!/usr/bin/env python
# -*- coding: utf-8 -*-


import unittest

from tests.sino.scom.paths import update_working_directory

update_working_directory()  # Needed when: 'pipenv run python -m unittest tests/sino/scom/{this_file}.py'


class TestScomBaseFrame(unittest.TestCase):
    """Tests BaseFrame class.
    """

    def test_object_creation(self):
        from sino.scom.baseframe import BaseFrame

        base_frame = BaseFrame(buffer_size=16)
        print(base_frame)
        self.assertEqual(0, base_frame.data_length())

        bf2 = BaseFrame(buffer_size=8)
        with self.assertRaises(AssertionError):
            bf2.initialize(12, 9, 7) # AssertionError: Buffer is too small!
        print(bf2)
        self.assertEqual(7, bf2.data_length())

        bf2.print_cframe()

        # buffer size of 18 is minimum for 2 bytes data
        bf3 = BaseFrame(buffer_size=18)
        bf3.set_data_length(2)
        print(bf3)

    def test_initialize_using_bytearray(self):
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

        base_frame.is_valid()
        base_frame.last_error()
