# -*- coding: utf-8 -*-
# cython: language_level=3
# distutils: language = c++
#

from libc.stdlib cimport malloc, free
from baseframe cimport *

#
# Python class representing low-level functionality for an SCOM Frame
#
# Python Frame class declared as cdef. This allows to use C types in python code.
# Implementation part
#
cdef class BaseFrame:
    """Provides low-level functionality for an SCOM Frame
    """

    def __init__(self, size_t buffer_size):
        #super(BaseFrame, self).__init__()
        self._initialize(buffer_size)

    def _initialize(self, size_t buffer_size):
        self.cFrame.buffer = <char *>malloc(sizeof(char) * buffer_size)
        self.cFrame.buffer_size = buffer_size

    def initialize(self, src_addr, dest_addr, data_length=0):
        self.cFrame.src_addr = src_addr
        self.cFrame.dst_addr = dest_addr
        self.cFrame.data_length = data_length

        # Write frame attributes into buffer
        self.encode_request()

    def encode_request(self):
        """Writes the frame attributes into the buffer."""
        # Call c library to do it
        encode_request_frame(self)

    def initialize_using_bytearray(self, byte_array, array_size):
        """Initializes the frame using the content of a byte array."""
        index = 0
        # Copy byte array into c array
        while index < array_size:
            self.cFrame.buffer[index] = byte_array[index]
            index += 1

        decode_frame_header(self)
        pass

    def __dealloc__(self):
        if self.cFrame.buffer:
            free(self.cFrame.buffer)

    def __str__(self):
        # Cast c-string to python string: http://docs.cython.org/src/tutorial/strings.html
        if self.cFrame.buffer:
            return 'src_addr: ' + str(self.cFrame.src_addr) + ',' + \
                   'dst_addr: ' + str(self.cFrame.dst_addr) + ',' + \
                   'service_id: ' + str(self.cFrame.service_id) + ',' + \
                   'data_length: ' + str(self.cFrame.data_length) + \
                   'buff:' + <bytes>self.cFrame.buffer + ', ' + str(self.cFrame.buffer_size)
        else:
            return 'NULL, ' + str(self.cFrame.buffer_size)

    def buffer_as_hex_string(self):
        """Returns frame buffer as HEX string"""
        frame_size  = SCOM_FRAME_HEADER_SIZE
        frame_size += self.cFrame.data_length + 2
        index = 0
        string = ''
        while index < frame_size:
            # Convert each byte in buffer to hex
            string += format(self.cFrame.buffer[index], '02x') + ' '
            index += 1
        return string

    def set_data_length(self, data_length):
        """Sets the data_length field of the frame"""
        self.cFrame.data_length = data_length
        encode_request_frame(self)

    def data_length(self):
        return self.cFrame.data_length

    def print_cframe(self):
        print(self.cFrame)

    def copy_buffer(self):
        """Copies the frame buffer into a python byte array"""
        frame_size  = SCOM_FRAME_HEADER_SIZE
        frame_size += self.cFrame.data_length + 2
        index = 0
        buffer = bytearray()
        while index < frame_size:
            buffer.append(self.cFrame.buffer[index])
            index += 1
        return buffer

    def is_valid(self):
        if self.last_error() == SCOM_ERROR_NO_ERROR:
            return True
        return False

    def last_error(self):
        return self.cFrame.last_error

#
# Public/Exported python functions
#
def encode_request_frame(BaseFrame frame_obj):
    scom_encode_request_frame(&frame_obj.cFrame)

def decode_frame_header(BaseFrame frame_obj):
    scom_decode_frame_header(&frame_obj.cFrame)

def decode_frame_data(BaseFrame frame_obj):
    scom_decode_frame_data(&frame_obj.cFrame)

def frame_length(BaseFrame frame_obj):
    return scom_frame_length(&frame_obj.cFrame)
