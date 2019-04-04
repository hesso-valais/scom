# -*- coding: utf-8 -*-
# cython: language_level=3
#

import struct
from libc.stdint cimport uint16_t, uint32_t
from baseframe cimport BaseFrame
from baseFrame cimport scom_frame_t

# Include from libc.stdint does not work with recent VS compilers
#cdef extern from "vc_stdint.h":
#    ctypedef unsigned char      uint8_t
#    ctypedef unsigned           uint16_t
#    ctypedef unsigned long      uint32_t
#    ctypedef unsigned long long uint64_t
#    ctypedef   signed char      int8_t
#    ctypedef          int       int16_t
#    ctypedef          long      int32_t
#    ctypedef          long long int64_t

cdef extern from "scomlib/scom_property.h":
    ctypedef enum scom_object_type_t:
        SCOM_USER_INFO_OBJECT_TYPE
        SCOM_PARAMETER_OBJECT_TYPE

    ctypedef struct scom_property_t:
        scom_frame_t* frame
        scom_object_type_t object_type
        uint32_t object_id
        uint16_t property_id
        size_t value_length
        char* value_buffer
        size_t value_buffer_size

    # C-functions to be used in python code
    void scom_initialize_property(scom_property_t* cproperty, scom_frame_t* frame);
    void scom_encode_read_property(scom_property_t* cproperty);
    void scom_encode_write_property(scom_property_t* cproperty);
    void scom_decode_read_property(scom_property_t* cproperty);
    void scom_decode_write_property(scom_property_t* cproperty);

#
# Python class representing a SCOM property
#
cdef class Property:
    """Low-Level SCOM Property
    """
    cdef BaseFrame _frame
    cdef scom_property_t _cProperty

    def __init__(self, BaseFrame frame):
        self._frame = frame
        self._initialize(frame)

    def _initialize(self, BaseFrame frame):
        scom_initialize_property(&self._cProperty, &frame.cFrame)

    def set_object_read(self, object_type, object_id, property_id):
        self._cProperty.object_type = object_type
        self._cProperty.object_id = object_id
        self._cProperty.property_id = property_id

        # Write property into frame buffer (read command)
        encode_read_property(self)

        # Frame fileds need to be updated in frame buffer
        self._frame.encode_request()

    def set_object_write(self, object_type, object_id, property_id, property_data, property_data_length,
                         property_format='float'):
        self._cProperty.object_type = object_type
        self._cProperty.object_id = object_id
        self._cProperty.property_id = property_id

        # Add property data
        self._cProperty.value_length = property_data_length

        if property_data_length == 4 and property_format in ('int32', 'signal'):
            byte_array = struct.pack('I', property_data)      # Split uint32_t to byte array (4 bytes)
            self._cProperty.value_buffer[0] = ord(byte_array[0])  # LSB
            self._cProperty.value_buffer[1] = ord(byte_array[1])
            self._cProperty.value_buffer[2] = ord(byte_array[2])
            self._cProperty.value_buffer[3] = ord(byte_array[3])  # MSG
        elif property_data_length == 4 and property_format == 'float':
            byte_array = struct.pack('f', property_data)      # Split float to byte array (4 bytes)
            self._cProperty.value_buffer[0] = ord(byte_array[0])  # LSB
            self._cProperty.value_buffer[1] = ord(byte_array[1])
            self._cProperty.value_buffer[2] = ord(byte_array[2])
            self._cProperty.value_buffer[3] = ord(byte_array[3])  # MSG
        elif property_data_length == 2 and property_format == 'short-enum':
            byte_array = struct.pack('h', property_data)      # Split uin16_t to byte array (2 bytes)
            self._cProperty.value_buffer[0] = ord(byte_array[0])  # LSB
            self._cProperty.value_buffer[1] = ord(byte_array[1])  # MSG
        elif property_data_length == 1 and property_format == 'byte':
            byte_array = struct.pack('b', property_data)      # Split uint8_t to byte array (1 byte)
            self._cProperty.value_buffer[0] = ord(byte_array[0])
        elif property_data_length == 1 and property_format == 'bool':
            byte_array = struct.pack('b', property_data)      # Split uint8_t to byte array (1 byte)
            self._cProperty.value_buffer[0] = ord(byte_array[0])
        else:
            assert False, 'Not implemented yet!'

        # Write property into frame buffer (write command)
        encode_write_property(self)

        # Frame fields need to be updated in frame buffer
        self._frame.encode_request()

    def __str__(self):
        return str(self._cProperty.value_buffer_size)

    def print_attr(self):
        nl = '\n'
        string = ''
        string += 'object_type: ' + str(self._cProperty.object_type) + nl
        string += 'object_id: ' + str(self._cProperty.object_id) + nl
        string += 'property_id: ' + str(self._cProperty.property_id) + nl
        string += 'value_length: ' + str(self._cProperty.value_length) + nl
        string += 'value_buffer: ' + str(self._cProperty.value_buffer) + nl
        string += 'value_buffer_size: ' + str(self._cProperty.value_buffer_size) + nl
        print(string)

#
# Public/Exported python functions
#
def encode_read_property(Property cproperty):
    scom_encode_read_property(&cproperty._cProperty)

def encode_write_property(Property cproperty):
    scom_encode_write_property(&cproperty._cProperty)

def decode_read_property(Property cproperty):
    scom_decode_read_property(&cproperty._cProperty)

def decode_write_property(Property cproperty):
    scom_decode_write_property(&cproperty._cProperty)
