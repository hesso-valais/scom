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


#include "scom_property.h"

/* -------- private definitions -------------------- */

#define SCOM_SERVICE_HEADER_SIZE 2
#define SCOM_PROPERTY_HEADER_SIZE 8

#define SCOM_PROPERTY_HEADER_OFFSET (SCOM_FRAME_HEADER_SIZE + SCOM_SERVICE_HEADER_SIZE)
#define SCOM_PROPERTY_VALUE_OFFSET (SCOM_FRAME_HEADER_SIZE + SCOM_SERVICE_HEADER_SIZE + SCOM_PROPERTY_HEADER_SIZE)

static void scom_encode_property_header(scom_property_t* property);
static void scom_decode_property_header(scom_property_t* property);
static void scom_decode_property_error_response(scom_property_t* property, ptrdiff_t length);

/* ----------------- implementation ------------------ */


/**
 * \brief initialize a scom_property_t before use
 * \param property the structure to initialize
 * \param frame an initialized scom_frame_t this will be used by the property
 */
void scom_initialize_property(scom_property_t* property, scom_frame_t* frame)
{
    property->frame = frame;
    property->value_buffer = frame->buffer + SCOM_PROPERTY_VALUE_OFFSET;
    property->value_buffer_size = frame->buffer_size - SCOM_PROPERTY_VALUE_OFFSET;
}


/* internal function to encode the property info in the frame */
static void scom_encode_property_header(scom_property_t* property)
{
    char* header =  property->frame->buffer + SCOM_PROPERTY_HEADER_OFFSET;

    scom_write_le16(&header[0], property->object_type);
    scom_write_le32(&header[2], property->object_id);
    scom_write_le16(&header[6], property->property_id);
}


/* internal function to decode a frame transporting an error */
static void scom_decode_property_error_response(scom_property_t* property, ptrdiff_t length)
{
    if(length == 2) {
        scom_decode_property_header(property);

        /* decode the error */
        property->value_length = length;
        property->frame->last_error = (scom_error_t)scom_read_le16(property->value_buffer);
    }
    else {
        property->value_length = 0;
        property->frame->last_error = SCOM_ERROR_INVALID_FRAME;
    }
}


/* internal function to decode the values that identify a property */
static void scom_decode_property_header(scom_property_t* property)
{
    char* header =  property->frame->buffer + SCOM_PROPERTY_HEADER_OFFSET;

    property->object_type = (scom_object_type_t)scom_read_le16(&header[0]);
    property->object_id = scom_read_le32(&header[2]);
    property->property_id = scom_read_le16(&header[6]);
}


/**
 * \brief encode a property read request before sending it
 *
 * The fields src_addr, dst_addr must be defined in property->frame.
 * object_type, object_id and property_id should be defined in property.
 */
void scom_encode_read_property(scom_property_t* property)
{
    property->frame->service_id = SCOM_READ_PROPERTY_SERVICE;
    property->value_length = 0;
    property->frame->data_length = SCOM_SERVICE_HEADER_SIZE + SCOM_PROPERTY_HEADER_SIZE;

    scom_encode_property_header(property);
}


/**
 *  \brief encode a property write request before sending it
 *
 * The fields src_addr, dst_addr must be defined in property->frame.
 * object_type, object_id and property_id, value_length and value_buffer should be defined in property.
 */
void scom_encode_write_property(scom_property_t* property)
{
    property->frame->service_id = SCOM_WRITE_PROPERTY_SERVICE;
    property->frame->data_length =  SCOM_SERVICE_HEADER_SIZE + SCOM_PROPERTY_HEADER_SIZE + property->value_length;

    scom_encode_property_header(property);
}


/**
 *  \brief decode a property read response after reception
 */
void scom_decode_read_property(scom_property_t* property)
{
    ptrdiff_t length;

    length = (ptrdiff_t)property->frame->data_length - SCOM_SERVICE_HEADER_SIZE - SCOM_PROPERTY_HEADER_SIZE;

    if(!property->frame->service_flags.error
       && length >= 0
       && length <= (ptrdiff_t)property->value_buffer_size) {
            property->value_length = length;
            scom_decode_property_header(property);
    }
    else if(property->frame->service_flags.error) {
       /* if we have an application error */
        scom_decode_property_error_response(property, length);
    }
    else {
        property->value_length = 0;
        property->frame->last_error = SCOM_ERROR_STACK_BUFFER_TOO_SMALL;
    }
}


/**
 *  \brief decode a property write response after reception
 */
void scom_decode_write_property(scom_property_t* property)
{
    ptrdiff_t length;

    length = (ptrdiff_t)property->frame->data_length - SCOM_SERVICE_HEADER_SIZE - SCOM_PROPERTY_HEADER_SIZE;

    if(!property->frame->service_flags.error && length == 0) {
        /* normal frame */
        property->value_length = length;
        scom_decode_property_header(property);
    }
    /* if we have an application error */
    else if(property->frame->service_flags.error) {
        scom_decode_property_error_response(property, length);
    }
    else {
        property->value_length = 0;
        property->frame->last_error = SCOM_ERROR_STACK_BUFFER_TOO_SMALL;
    }

}
