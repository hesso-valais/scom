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

/*
 * This file implements the needed porting functions and macros on a C99 compiler. It as been tested
 * with gcc on x86 (32 bit, little endian).
 * The float conversion functions are not totally portable.
 */

#ifndef SCOM_PORT_C99_H


#define SCOM_PORT_C99_H

#ifdef __cplusplus
extern "C" {
#endif

/* for size_t and NULL */
#include <stddef.h>

/* for uint16_t, uint32_t, etc. */
#if defined(__GNUC__)
    #include <stdint.h>
#endif
#if defined(_MSC_VER)
    #if (_MSC_VER >= 1600)
        #include <stdint.h>
    #else
        #include "vc_stdint.h"
    #endif
#endif

#ifdef _MSC_VER
#define INLINE __inline
#else
#define INLINE inline
#endif


/* ----- write and read access to raw buffer data ---------------
 * These functions allow the read and write in a portable way
 * independent of the processor byte order in a buffer.
 * "le" stands for little endian, i.e. LSB byte first.
 * They should be portable, were tested on little endian platform and should
 * also work on big or mixed endian platforms.
 * Float conversion functions are not portable but they are only
 * used in the examples.
 */

static INLINE void scom_write_le32(unsigned char *const p, const uint32_t data)
{
    *(p) = (data) & 0xFF;
    *(p+1) = (data >> 8) & 0xFF;
    *(p+2) = (data >> 16) & 0xFF;
    *(p+3) = (data >> 24) & 0xFF;
}


static INLINE uint32_t scom_read_le32(const unsigned char *const p)
{
    return  ((*p) & 0xFF) | ((*(p+1) & 0xFF) << 8) |
            ((*(p+2) & 0xFF)<< 16) | ((*(p+3) & 0xFF) << 24) ;
}


static INLINE void scom_write_le16(unsigned char *const p, const uint16_t data)
{
    *(p) = (data) & 0xFF;
    *(p+1) = (data >> 8) & 0xFF;
}


static INLINE uint16_t scom_read_le16(const unsigned char *const p)
{
    return ((*(p)) & 0xFF) | ((*(p+1) & 0xFF) << 8) ;
}


static INLINE float scom_read_le_float(const unsigned char *const p)
{
    /* this way of doing it is not portable.
       The union may not be aligned correctly.
       The float type on the architecture may not be IEEE754. */
    union {
        float floating;
        uint32_t integer;
    } val;

    /* use the endian independent function */
    val.integer = scom_read_le32(p);

    return val.floating;
}


static INLINE void scom_write_le_float(unsigned char *const p, float data)
{
    /* this way of doing it is not portable.
       The union may not be aligned correctly.
       The float type on the architecture may not be IEEE754. */
    union {
        float floating;
        uint32_t integer;
    } val;

    val.floating = data;

    /* use the endian independent function */
    scom_write_le32(p, val.integer);

}

#ifdef __cplusplus
}
#endif

#endif
