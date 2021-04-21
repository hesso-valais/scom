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

#include "scom_data_link.h"

/**
 * \mainpage Studer Innotec Xtender Serial Communication C Library
 *
 * This library is a reference implementation for the serial protocol for Xtender systems from Studer Innotec SA.
 *
 * The protocol specification could be found in the document "Technical specification - Xtender serial protocol".
 * The latest version of the specification could be found under "SOFTWARES AND UPDATES" at:
 *
 * http://www.studer-innotec.com/?n_ulang=en&cat=download_center
 *
 *
 * \section sec_structure Library structure
 * - The porting layer is defined in scom_port_TARGET_NAME.h, for a C99 compiler scom_port_c99.h.
 * - scom_data_link.h implements the exchange of frames that is independent of the service.
 * - scom_property.h implements the READ_PROPERY and WRITE_PROPERTY services on top of scom_data_link.h
 * - usage_examples.c provides a simple test implementation using a serial port viewed as a file object from stdio library.
 *
 * \section sec_portability Portability
 * The library is written in a non-blocking way that allows its use in synchronous, pooling or event-driven architectures.
 * It is the responsibility of the user code to handle the access to the serial port and implement delays and timeouts.
 * The library has a low memory footprint with configurable buffers and the possibility to
 * use the same buffer for request and response. It is written in a very portable way and should be usable
 * from small microcontrollers to a PC system.
 *
 * The library targets platforms with the following requirements:
 *  - truly ANSI C89 compiler
 *  - big/little or mixed endianness
 *  - 8 to 64 bit architectures
 *  - No requirement for heap allocation functions
 *  - no standard C library function call
 *  - works with C++
 *
 * All files apart from the scom_port_*.h must respect these requirements, but it doesn't mean it has to be tested for it.
 * Patches that don't respect these requirements will usually be rejected.
 *
 * The correct porting file is included at the top of scom_data_link.h. Currently there is only a port for C99 compiler in scom_port_c99.h
 * that has been tested on MS Windows x86 with GCC and Microsoft Visual Studio (compiled in C++).
 *
 * Because of the interface with the serial port, execution environment, and build files are different for each target and toolchain, we
 * do not provide any working example. However, usage_examples.c is a good base to understand how to use the library.
 *
 * Studer Innotec will not respond to any questions regarding the library porting, IDE set-up, toolchain, compiler problems, etc.
 *
 */


/* ----------- private definitions ---------------- */
static uint16_t scom_calc_checksum(    const unsigned char *data,
                                       uint_fast16_t length);

#define SCOM_START_BYTE 0xAA


/* ---------------------- public function implementations ---------------------- */

/**
 * \brief initialize a frame structure
 * \param frame the structure to initialize
 * \param buffer the buffer used to encode the data
 * \param buffer_size the size of a buffer, allowing user defined size
 */
void scom_initialize_frame(scom_frame_t* frame, unsigned char* buffer, size_t buffer_size)
{
    frame->last_error = SCOM_ERROR_NO_ERROR;
    frame->buffer = buffer;
    frame->buffer_size = buffer_size;
}


/**
 * \brief encode a frame in its buffer
 *
 * The frame must have been initialized with scom_initialize_frame().
 * The frame fields src_addr, dst_addr, service_id and data_length must have a valid value.
 */
void scom_encode_request_frame(scom_frame_t* frame)
{
    uint16_t checksum;

    frame->buffer[0] = (unsigned char)SCOM_START_BYTE;

    /* the frame flag of a request must always be 0 */
    frame->buffer[1] = 0;

    scom_write_le32(&frame->buffer[2], frame->src_addr);
    scom_write_le32(&frame->buffer[6], frame->dst_addr);
    scom_write_le16(&frame->buffer[10], (uint16_t)frame->data_length);


    /* write header checksum calculated without start_byte and checksum */
    checksum = scom_calc_checksum(&frame->buffer[1], SCOM_FRAME_HEADER_SIZE - 1 - 2);
    scom_write_le16(&frame->buffer[12], checksum);

    /* frame->service_flags is not encoded, because
     * reserved7to2, is_response and has_error, should always be 0 for a request
     */
    frame->buffer[SCOM_FRAME_HEADER_SIZE] = 0;

    frame->buffer[SCOM_FRAME_HEADER_SIZE + 1] = frame->service_id;

    /* write data checksum */
    if(scom_frame_length(frame) <= frame->buffer_size) {
        checksum = scom_calc_checksum(&frame->buffer[SCOM_FRAME_HEADER_SIZE], (uint_fast16_t)frame->data_length);
        scom_write_le16(&frame->buffer[SCOM_FRAME_HEADER_SIZE + frame->data_length], checksum);
    }
    else {
        frame->last_error = SCOM_ERROR_STACK_BUFFER_TOO_SMALL;
    }

}


/**
 * \brief decode the frame header from its buffer
 *
 * This function call be called after the reception of SCOM_FRAME_HEADER_SIZE byte in frame->buffer.
 * frame->last_error will contain SCOM_ERROR_INVALID_FRAME if the checksum is invalid or the header
 * is misformed.
 */
void scom_decode_frame_header(scom_frame_t* frame)
{
    uint8_t flags;
    uint16_t sent_checksum;
    uint16_t calculated_checksum;

    flags = frame->buffer[1];

    frame->frame_flags.reserved7to5 =                   (flags >> 5) & 0x7;
    frame->frame_flags.is_new_datalogger_file_present = (flags >> 4) & 0x1;
    frame->frame_flags.is_sd_card_full =                (flags >> 3) & 0x1;
    frame->frame_flags.is_sd_card_present =             (flags >> 2) & 0x1;
    frame->frame_flags.was_rcc_reseted =                (flags >> 1) & 0x1;
    frame->frame_flags.is_message_pending =             (flags >> 0) & 0x1;


    if(((uint8_t)frame->buffer[0]) != SCOM_START_BYTE) {
        frame->last_error = SCOM_ERROR_INVALID_FRAME;
        /* continue to decode for debug purpose */
    }

    frame->buffer[1] = flags;

    frame->src_addr = scom_read_le32(&frame->buffer[2]);
    frame->dst_addr = scom_read_le32(&frame->buffer[6]);
    frame->data_length = scom_read_le16(&frame->buffer[10]);

    if(frame->data_length < 2 ||
       scom_frame_length(frame) > frame->buffer_size) {
        /* the data must contain at least the service_flags and service_id
         * and pass in the buffer
         */
        frame->last_error = SCOM_ERROR_INVALID_FRAME;
        /* continue to decode for debug purpose */
    }

    sent_checksum = scom_read_le16(&frame->buffer[12]);

    calculated_checksum = scom_calc_checksum(&frame->buffer[1], SCOM_FRAME_HEADER_SIZE - 1 - 2);

    if(sent_checksum != calculated_checksum) {
        frame->last_error = SCOM_ERROR_INVALID_FRAME;
    }
}

/**
 * \brief decode the frame data from its buffer
 *
 * This function call be called after the reception of frame->data_length byte in frame->buffer.
 * frame->last_error will contain SCOM_ERROR_INVALID_FRAME if the data checksum is invalid or the frame
 * is misformed.
 */
void scom_decode_frame_data(scom_frame_t* frame)
{
    uint8_t flags;
    uint16_t sent_checksum;
    uint16_t calculated_checksum;

    if(frame->last_error == SCOM_ERROR_NO_ERROR) {

        calculated_checksum = scom_calc_checksum(&frame->buffer[SCOM_FRAME_HEADER_SIZE],
                                                 (uint_fast16_t)frame->data_length);

        sent_checksum = scom_read_le16(&frame->buffer[SCOM_FRAME_HEADER_SIZE + frame->data_length]);

        if(calculated_checksum != sent_checksum) {
            frame->last_error = SCOM_ERROR_INVALID_FRAME;
            /* continue to decode for debug purpose */
        }

        flags = frame->buffer[SCOM_FRAME_HEADER_SIZE];
        frame->service_flags.reserved7to2 = (flags >> 2) & 0x3F;
        frame->service_flags.is_response = (flags >> 1) & 0x1;
        frame->service_flags.error = (flags >> 0) & 0x1;

        if(!frame->service_flags.is_response) {
            frame->last_error = SCOM_ERROR_INVALID_FRAME;
            /* continue to decode for debug purpose */
        }

        frame->service_id = (scom_service_t)frame->buffer[SCOM_FRAME_HEADER_SIZE + 1];
    }
    else {
        /* We decode the frame only if the header was valid.
         * But the code integrating the library in the platform
         * should timeout and not call this function in this case, anyway.
         */
    }

}


/**
 * \brief return the total frame length
 *
 * This function can be called after scom_decode_frame_header() to know how many
 * bytes we expect to receive.
 */
size_t scom_frame_length(scom_frame_t* frame)
{
    return SCOM_FRAME_HEADER_SIZE + frame->data_length + 2;
}


/* --------------------- private implementation ---------------------*/

/**
 * \brief calculate the checksum on a buffer
 * based on RFC1146, Appendix I
 *
 * @param checksum a pointer to the 2 bytes of the checksum
 * @param length number of byte of the data
 * @return the checksum value
 *
 * @see http://tools.ietf.org/html/rfc1146
 */
uint16_t scom_calc_checksum(    const unsigned char *data,
                                uint_fast16_t length)
{
        uint_fast8_t A = 0xFF, B = 0;

        while (length--) {
            A = (A + *data++) & 0xFF;
            B = (B + A) & 0xFF;
        }

        return (B & 0xFF) << 8 | (A & 0xFF);
}



