/*
Copyright (c) 2014 Studer Innotec SA

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
*/

/**
 * \file scom_data_link.h interface to send and receive scom frames (the Data Link Layer)
 */

#ifndef SCOM_DATA_LINK_H
#define SCOM_DATA_LINK_H

#ifdef __cplusplus
extern "C" {
#endif

/* ---------- code to work on different compilers and architectures -------------------- */

#if defined(__GNUC__)  /* current gcc and g++ have enough C99 support to use this port */ \
   || (defined(_MSC_VER)) /* Microsoft Visual Studio as a C++ compiler supports enough C99 to compile */

#include "scom_port_c99.h"
#else
#error "target or compiler not supported"
#endif


/* ------------------------- helper macros -------------------------------------- */

/**
 * \def SCOM_NBR_ELEMENTS(array)
 * \brief return the number of elements of an array (index max + 1)
 * \param array  variable of array type
 */
#define SCOM_NBR_ELEMENTS(array) (sizeof(array)/sizeof((array)[0]))

/**
 * \def SCOM_MIN(a, b)
 * \brief return the minimum from two values
 */
#define SCOM_MIN(a, b) ((a) < (b) ? (a) : (b))

/**
 * \def SCOM_MAX(a, b)
 * \brief return the maximum from two values
 */
#define SCOM_MAX(a, b) ((a) > (b) ? (a) : (b))


/* ------------------------- helper macros -------------------------------------- */

/**
 * \def SCOM_FRAME_HEADER_SIZE
 * \brief the size of the frame header
 */
#define SCOM_FRAME_HEADER_SIZE 14

/**
 * \brief scom error types
 */
typedef enum {
    SCOM_ERROR_NO_ERROR = 0x0000,                 /**< \brief a value to indicate not error occurred */

    /* data link errors */
    SCOM_ERROR_INVALID_FRAME = 0x0001,            /**< \brief malformed frame on the datalink layer */
    SCOM_ERROR_DEVICE_NOT_FOUND = 0x0002,         /**< \brief wrong dst_addr field */
    SCOM_ERROR_RESPONSE_TIMEOUT = 0x0003,         /**< \brief no response of the server */

    /* service errors */
    SCOM_ERROR_SERVICE_NOT_SUPPORTED = 0x0011,        /**< \brief wrong service_id field */
    SCOM_ERROR_INVALID_SERVICE_ARGUMENT = 0x0012,     /**< \brief wrong service_data */
    SCOM_ERROR_GATEWAY_BUSY = 0x0013,                 /**< \brief gateway (for example XCOM-232i) busy */

    /* read/write property errors */
    SCOM_ERROR_TYPE_NOT_SUPPORTED = 0x0021,       /**< \brief the object_type requested doesn't exist */
    SCOM_ERROR_OBJECT_ID_NOT_FOUND = 0x0022,      /**< \brief not object with this object_id was found */
    SCOM_ERROR_PROPERTY_NOT_SUPPORTED = 0x0023,   /**< \brief the property identified by property_id doesn't exist */
    SCOM_ERROR_INVALID_DATA_LENGTH = 0x0024,      /**< \brief the field property_data has an invalid number of bytes */

    /* write property errors */
    SCOM_ERROR_PROPERTY_IS_READ_ONLY = 0x0025,    /**< \brief a write to this property is not allowed */
    SCOM_ERROR_INVALID_DATA = 0x0026,             /**< \brief this value is impossible for this property */
    SCOM_ERROR_DATA_TOO_SMALL = 0x0027,           /**< \brief the value is below the minimum limit */
    SCOM_ERROR_DATA_TOO_BIG = 0x0028,             /**< \brief the value is above the maximum limit */
    SCOM_ERROR_WRITE_PROPERTY_FAILED = 0x0029,    /**< \brief write is possible, but failed */
    SCOM_ERROR_READ_PROPERTY_FAILED = 0x002A,     /**< \brief read is possible, but failed */
    SCOM_ERROR_ACCESS_DENIED = 0x002B,            /**< \brief insufficient user access */
    SCOM_ERROR_OBJECT_NOT_SUPPORTED = 0x002C,     /**< \brief this object id, through existent, is not supported by the current implementation of the gateway */
    SCOM_ERROR_MULTICAST_READ_NOT_SUPPORTED = 0x002D,  /**< Read operation is not supported when used on multicast addresses */

    /* error in the client application */
    SCOM_ERROR_INVALID_SHELL_ARG = 0x0081,        /**< \brief the command line tool used received the wrong arguments */
    SCOM_ERROR_STACK_PORT_NOT_FOUND = 0x0082,     /**< \brief the port configured to be used doesn't exist or it is not possible to open it */
    SCOM_ERROR_STACK_PORT_INIT_FAILED =  0x0083,  /**< \brief the initialization of the port failed */
    SCOM_ERROR_STACK_PORT_WRITE_FAILED = 0x0084,  /**< \brief a write operation on the port failed */
    SCOM_ERROR_STACK_PORT_READ_FAILED = 0x0085,   /**< \brief a read operation on the port failed */
    SCOM_ERROR_STACK_BUFFER_TOO_SMALL = 0x0086,   /**< \brief the buffer provided to the client stack are too small to handle the operation */
    SCOM_ERROR_STACK_PROPERTY_HEADER_DOESNT_MATCH = 0x0087 /**< \brief the header of a property access response is not equal the response */

} scom_error_t;


/**
 * \brief service identifier of service_id
 */
typedef enum {
    SCOM_READ_PROPERTY_SERVICE = 0x1,
    SCOM_WRITE_PROPERTY_SERVICE = 0x2
} scom_service_t;

/**
 * \brief data format
 * \see Xtender serial protocol technical specification
 */
typedef enum {
    SCOM_FORMAT_INVALID_FORMAT = 0,

    /* 1 byte */
    SCOM_FORMAT_BOOL            = 1,

    /* 2 bytes */
    SCOM_FORMAT_FORMAT          = 2,
    SCOM_FORMAT_ENUM            = 3,
    SCOM_FORMAT_ERROR           = 4,

    /* 4 bytes */
    SCOM_FORMAT_INT32           = 5,
    SCOM_FORMAT_FLOAT           = 6,

    /* n bytes */
    SCOM_FORMAT_STRING          = 7,
    SCOM_FORMAT_DYNAMIC         = 8,
    SCOM_FORMAT_BYTE_STREAM     = 9

} scom_format_t;


/**
 * \brief decoded content of frame_flags byte
 */
typedef struct {
    int reserved7to5:3;
    int is_new_datalogger_file_present:1;
    int is_sd_card_full:1;
    int is_sd_card_present:1;
    int was_rcc_reseted:1;
    int is_message_pending:1;
} scom_frame_flags_t;


/**
 * \brief decoded content of service_flags byte
 */
typedef struct {
    int reserved7to2:6;
    int is_response:1;
    int error:1;
} scom_service_flags_t;


/**
 * \brief a structure representing a frame
 *
 * The data buffer is variable and specified by the user with scom_initialize_frame().
 */
typedef struct {
    scom_frame_flags_t frame_flags; /**< \brief flags specific to the datalink layer */
    uint32_t src_addr;              /**< \brief source address of this frame */
    uint32_t dst_addr;              /**< \brief destination address of this frame */

    scom_service_flags_t service_flags; /**< \brief flags specific to the service layer */
    scom_service_t service_id;          /**< \brief identifier of the service used by this frame */

    /** \brief length of the data payload of the frame without header and checksum */
    size_t data_length;

    /** \brief last error that occurred in the frame processing */
    scom_error_t last_error;

    char* buffer;           /**< \brief buffer where the frame is build */
    size_t buffer_size;     /**< \brief maximum usable size of the buffer */
} scom_frame_t;


void scom_initialize_frame(scom_frame_t* frame, char* buffer, size_t buffer_size);
void scom_encode_request_frame(scom_frame_t* frame);
void scom_decode_frame_header(scom_frame_t* frame);
void scom_decode_frame_data(scom_frame_t* frame);

size_t scom_frame_length(scom_frame_t* frame);

#ifdef __cplusplus
}
#endif

#endif









