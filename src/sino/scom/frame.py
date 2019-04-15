#!/usr/bin/env python
# -*- coding: utf-8 -*-

import struct

from .baseframe import *


class Frame(BaseFrame):
    """High Level SCOM frame providing a better python like style.
    """
    def __init__(self):
        super(Frame, self).__init__(1024)

        self._buffer = bytearray()
        self.dataLength = 0

    def parse_frame_from_string(self, rx_buffer):
        from .scom import Scom

        frame_length = 0

        if len(rx_buffer) < 12:
            return False, frame_length

        # Extract the 'data_length' field
        data_length = struct.unpack('<H', rx_buffer[10:10 + 2])[0]
        self.dataLength = data_length

        if len(rx_buffer) >= Scom.SCOM_FRAME_HEADER_SIZE + data_length + Scom.SCOM_FRAME_TRAILER_SIZE:
            frame_length = Scom.SCOM_FRAME_HEADER_SIZE + data_length + Scom.SCOM_FRAME_TRAILER_SIZE
            self.initialize_using_bytearray(rx_buffer, len(rx_buffer))

            # Copy frame buffer into own buffer
            self._buffer = rx_buffer[0:frame_length]

            return True, frame_length
        else:
            print('Error parsing RX frame')
            return False, frame_length

    def as_hex_string(self):
        return self.buffer_as_hex_string()

    def is_request(self):
        return not self.is_response()

    def is_response(self):
        self._synch_attributes()

        assert self.dataLength >= 1
        is_response = True if self._buffer[14] & 0b10 else False
        return is_response

    def is_data_error_flag_set(self):
        assert self.dataLength >= 1
        error = True if self._buffer[14] & 0b01 else False
        return error

    def is_valid(self):
        if not super(Frame, self).is_valid():
            return False

        if self.is_request():
            pass

        if self.is_response():
            if self.is_data_error_flag_set():
                return False

        return True

    def __getitem__(self, item): return self._buffer[item]

    def _synch_attributes(self):
        """Syncs scom.Frame attributes using the cFrame attributes if necessary
        """
        # Check if data length size of cFrame differs from dataLength
        if self.dataLength != super(Frame, self).data_length():
            # OK. Need to update attributes
            self._buffer = super(Frame, self).copy_buffer()
            self.dataLength = super(Frame, self).data_length()

    def response_value_size(self):
        assert self.is_response()
        return self.dataLength - 10
