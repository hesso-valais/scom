#!/usr/bin/env python
# -*- coding: utf-8 -*-


import unittest

from tests.sino.scom.paths import update_working_directory

update_working_directory()  # Needed when: 'pipenv run python -m unittest tests/sino/scom/{this_file}.py'


class TestScomFrame(unittest.TestCase):
    """Tests BaseFrame class.
    """

    VALID_FAME_BYTES = b'\xaa"e\x00\x00\x00\x01\x00\x00\x00\x0c\x00\x93{\x03\x01\x01\x00\xb8\x0b\x00\x00' \
                       b'\x05\x00\x02\x00\xceR'
    VALID_FAME_BYTEARRAY = bytearray(VALID_FAME_BYTES)

    def test_object_creation(self):
        from sino.scom.frame import Frame

        frame = Frame(buffer_size=32)

        valid_frame = self.VALID_FAME_BYTEARRAY
        (result, length) = frame.parse_frame_from_string(valid_frame)
        self.assertTrue(result)
        self.assertEqual(length, 28)

        bad_frame = bytearray(b'\xaa"e\x00\x05\x00\x02\x00\xceR')
        (result, length) = frame.parse_frame_from_string(bad_frame)
        self.assertFalse(result)
        self.assertEqual(length, 0)

    def test_methods_valid_frame(self):
        from sino.scom.frame import Frame

        frame = Frame(buffer_size=64)
        (result, length) = frame.parse_frame_from_string(self.VALID_FAME_BYTES)
        self.assertTrue(result)

        hex_string = frame.buffer_as_hex_string()
        self.assertEqual(hex_string[0], 'A')
        self.assertEqual(hex_string[1], 'A')

        self.assertFalse(frame.is_request())
        self.assertTrue(frame.is_response())
        self.assertEqual(frame.response_value_size(), 2)

        frame.is_valid()
        frame.is_data_error_flag_set()
        frame.response_value_size()

    def test_methods_bad_frame(self):
        from sino.scom.frame import Frame
        from sino.scom.exeptions import ResponseFrameException

        frame = Frame(buffer_size=64)

        bad_frame = bytearray(b'\xBC"e\x00\x05\x00\x02\x00\xceR\x02\x00\x02\x00\x02\x00')
        (result, length) = frame.parse_frame_from_string(bad_frame)
        self.assertFalse(result)
        self.assertEqual(length, 0)

        self.assertFalse(frame.is_valid())

        frame.as_hex_string()

        with self.assertRaises(ValueError):
            frame.response_value_size()

        frame.set_data_length(0)
        with self.assertRaises(ValueError):
            frame.is_response()

        with self.assertRaises(ValueError):
            frame.is_data_error_flag_set()

        small_buffer_frame = Frame(8)
        small_buffer_frame.dataLength = 2
        with self.assertRaises(ValueError):
            small_buffer_frame.is_response()

        valid_request_frame = bytearray(b'\xaa\x00\x01\x00\x00\x00e\x00\x00\x00\n\x00oq\x00\x01\x01'
                                        b'\x00\xb8\x0b\x00\x00\x01\x00\xc5\x90')

        tx_frame = Frame()
        tx_frame.parse_frame_from_string(valid_request_frame)

        self.assertTrue(tx_frame.is_request())

        with self.assertRaises(ResponseFrameException):
            tx_frame.response_value_size()
