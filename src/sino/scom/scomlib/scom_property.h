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
 * \file scom_property.h interface to access to the object property of objects
 */

#ifndef SCOM_PROPERTY_H
#define SCOM_PROPERTY_H

#include "scom_data_link.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * \brief different values that object_type in scom_property_t can take
 */
typedef enum {
    SCOM_USER_INFO_OBJECT_TYPE = 0x1,
    SCOM_PARAMETER_OBJECT_TYPE = 0x2,
} scom_object_type_t;


/**
 * \brief structure to manipulate a property with the serial protocol
 */
typedef struct {
    /** \brief frame in which the operation are performed */
    scom_frame_t* frame;

    /** \brief type (info, param, ...) of the object manipulated */
    scom_object_type_t object_type;

    /** \brief identifier of the object in is type */
    uint32_t object_id;

    /** \brief identifier of the property we want to access for this particular object */
    uint16_t property_id;

    /** \brief length of the data (4 for INT32, ...) */
    size_t value_length;

    /** \brief pointer with the begining of the value */
    char* value_buffer;

    /** \brief maximum size that value_length can take */
    size_t value_buffer_size;
} scom_property_t;


void scom_initialize_property(scom_property_t* property, scom_frame_t* frame);

void scom_encode_read_property(scom_property_t* property);
void scom_encode_write_property(scom_property_t* property);

void scom_decode_read_property(scom_property_t* property);
void scom_decode_write_property(scom_property_t* property);

#ifdef __cplusplus
}
#endif

#endif
