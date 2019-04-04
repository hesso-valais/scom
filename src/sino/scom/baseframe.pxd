# -*- coding: utf-8 -*-
# cython: language_level=3
#

from libc.stdint cimport uintptr_t

cdef extern from "scomlib/scom_data_link.h":
    cdef int SCOM_FRAME_HEADER_SIZE

    ctypedef enum scom_error_t:
        SCOM_ERROR_NO_ERROR
        SCOM_ERROR_INVALID_FRAME
        SCOM_ERROR_DEVICE_NOT_FOUND
        SCOM_ERROR_RESPONSE_TIMEOUT
        SCOM_ERROR_SERVICE_NOT_SUPPORTED
        SCOM_ERROR_INVALID_SERVICE_ARGUMENT
        SCOM_ERROR_GATEWAY_BUSY
        SCOM_ERROR_TYPE_NOT_SUPPORTED
        SCOM_ERROR_OBJECT_ID_NOT_FOUND
        SCOM_ERROR_PROPERTY_NOT_SUPPORTED
        SCOM_ERROR_INVALID_DATA_LENGTH
        SCOM_ERROR_PROPERTY_IS_READ_ONLY
        SCOM_ERROR_INVALID_DATA
        SCOM_ERROR_DATA_TOO_SMALL
        SCOM_ERROR_DATA_TOO_BIG
        SCOM_ERROR_WRITE_PROPERTY_FAILED
        SCOM_ERROR_READ_PROPERTY_FAILED
        SCOM_ERROR_ACCESS_DENIED
        SCOM_ERROR_OBJECT_NOT_SUPPORTED
        SCOM_ERROR_MULTICAST_READ_NOT_SUPPORTED
        SCOM_ERROR_INVALID_SHELL_ARG
        SCOM_ERROR_STACK_PORT_NOT_FOUND
        SCOM_ERROR_STACK_PORT_INIT_FAILED
        SCOM_ERROR_STACK_PORT_WRITE_FAILED
        SCOM_ERROR_STACK_PORT_READ_FAILED
        SCOM_ERROR_STACK_BUFFER_TOO_SMALL
        SCOM_ERROR_STACK_PROPERTY_HEADER_DOESNT_MATCH

    ctypedef enum scom_service_t:
        SCOM_READ_PROPERTY_SERVICE
        SCOM_WRITE_PROPERTY_SERVICE

    ctypedef struct scom_frame_flags_t:
        int reserved7to5
        int is_new_datalogger_file_present
        int is_sd_card_full
        int is_sd_card_present
        int was_rcc_reseted
        int is_message_pending

    ctypedef struct scom_service_flags_t:
        int reserved7to2
        int is_response
        int error

    ctypedef struct scom_frame_t:
        scom_frame_flags_t frame_flags
        unsigned int src_addr
        unsigned int dst_addr
        scom_service_flags_t service_flags
        scom_service_t service_id
        size_t data_length
        scom_error_t last_error
        char * buffer
        size_t buffer_size

    # C-functions to be used in python code
    void scom_initialize_frame(scom_frame_t* frame, char* buffer, size_t buffer_size)
    void scom_encode_request_frame(scom_frame_t* frame);
    void scom_decode_frame_header(scom_frame_t* frame);
    void scom_decode_frame_data(scom_frame_t* frame);
    size_t scom_frame_length(scom_frame_t* frame);

#
# Python class representing low-level functionality for an SCOM Frame
#
# Python Frame class declared as cdef. This allows to use C types in python code.
# Definition part (other part is in the *.pyx file)
#
cdef class BaseFrame:
    cdef scom_frame_t cFrame
