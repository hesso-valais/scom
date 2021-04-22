#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import struct
from .exeptions import ResponseFrameException
from .baseframe import *


class Frame(BaseFrame):
    """High Level SCOM frame providing a better python like style.
    """

    log = logging.getLogger(__name__)

    def __init__(self, buffer_size: int = 1024):
        super(Frame, self).__init__(buffer_size=buffer_size)

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
            self.log.warning('Error parsing RX frame')
            return False, frame_length

    def as_hex_string(self):
        return self.buffer_as_hex_string()

    def is_request(self):
        return not self.is_response()

    def is_response(self):
        self._sync_attributes()

        if self.dataLength < 1:
            raise ValueError('DataLength is to small')

        if len(self._buffer) < 14:
            raise ValueError('Buffer size is to small')

        is_a_response = True if self._buffer[14] & 0b10 else False
        return is_a_response

    def is_data_error_flag_set(self):
        if self.dataLength < 1:
            raise ValueError('DataLength is to small')

        if len(self._buffer) < 14:
            raise ValueError('Buffer size is to small')

        err = True if self._buffer[14] & 0b01 else False
        return err

    def is_valid(self):
        if not super(Frame, self).is_valid():
            return False

        try:
            self.is_request()
        except ValueError:
            return False

        if self.is_response():
            if self.is_data_error_flag_set():
                return False

        return True

    def __getitem__(self, item): return self._buffer[item]

    def _sync_attributes(self):
        """Syncs scom.Frame attributes using the cFrame attributes if necessary
        """
        # Check if data length size of cFrame differs from dataLength
        if self.dataLength != super(Frame, self).data_length():
            # OK. Need to update attributes
            self._buffer = super(Frame, self).copy_buffer()
            self.dataLength = super(Frame, self).data_length()

    def response_value_size(self):
        if not self.is_response():
            raise ResponseFrameException('Not a response frame')
        return self.dataLength - 10
