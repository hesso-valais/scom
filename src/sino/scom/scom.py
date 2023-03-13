#!/usr/bin/env python
# -*- coding: utf-8 -*-

from threading import Lock
import time
import serial
from serial.serialutil import SerialException, SerialTimeoutException
import logging
from .baseframe import BaseFrame
from .frame import Frame


class Scom(object):
    """Handles the SCOM serial connection.
    """

    SCOM_FRAME_HEADER_SIZE = 14
    SCOM_FRAME_TRAILER_SIZE = 2

    log = logging.getLogger(__name__)

    rxErrors = 0

    def __init__(self):
        super(Scom, self).__init__()
        self._ser = None  # type: serial.Serial or None
        self._mutex = Lock()
        self._rxBuffer = bytearray()     # All bytes received go in here

    def initialize(self, com_port: str, baudrate: str or int = '38400'):
        """Initializes the instance and connects to the given COM port.

        :param com_port Name of the COM port. Ex. '/dev/ttyUSB0', 'COM1', etc.
        :param baudrate Baud rate of the COM port. Default value is '38400'
        """
        try:
            self._ser = serial.Serial(port=com_port,
                                      baudrate=baudrate,
                                      parity=serial.PARITY_EVEN)
            # Set RX timeout
            self._ser.timeout = 1    # second
        except Exception as msg:
            self.log.info(msg)
            exit()

    def set_rx_timeout(self, seconds: int) -> bool:
        """Sets the time to wait for a message to be received."""
        if self._ser:
            self._ser.timeout = seconds
            return True
        return False

    def write_frame(self, frame: BaseFrame, rx_timeout_in_seconds=3.0) -> Frame or None:
        """Writes a frame to the SCOM interface

        :param frame Frame to send.
        :type frame Frame
        :param rx_timeout_in_seconds Maximum time to wait for the response frame.
        :type rx_timeout_in_seconds float
        """
        if not self._ser:
            return None

        self.log.debug('TX: ' + frame.buffer_as_hex_string())
        buffer = frame.copy_buffer()

        lock_acquired = self._mutex.acquire(blocking=True, timeout=10)        # lock
        response_frame = Frame()
        if lock_acquired:
            try:
                self.set_rx_timeout(int(rx_timeout_in_seconds))  # Set time to wait for the response
                self._ser.write(buffer)
            except SerialTimeoutException:
                self.log.error('Error writing frame!')
            finally:
                response_frame = self._read_frame()
                self._mutex.release()       # unlock
        else:
            self.log.error('Could not lock mutex!')
        return response_frame

    def _read_frame(self, wait_time=1.0) -> Frame or None:
        """Reads a frame from the SCOM interface

        :param wait_time Time in seconds to wait
        :type wait_time float
        """
        if not self._ser:
            return None

        response_frame = Frame()
        rx_data_size_total = 0          # Size of data received in this turn

        while wait_time > 0:
            fract_wait_time = 0.10
            time.sleep(fract_wait_time)         # Wait a bit to get data back from SCOM interface
            rx_data_size = self._ser.in_waiting  # Check how many bytes available

            if rx_data_size:
                try:
                    # Read the bytes and put it into rx buffer
                    self._rxBuffer += bytearray(self._ser.read(rx_data_size))
                    # Update size counter
                    rx_data_size_total += rx_data_size
                except SerialException:
                    self.log.error('Error reading serial buffer!')
                    return None

            if rx_data_size_total > Scom.SCOM_FRAME_HEADER_SIZE + Scom.SCOM_FRAME_TRAILER_SIZE:
                # Try to parse a frame for the rx buffer
                success, length = response_frame.parse_frame_from_string(self._rxBuffer)

                if success:
                    # Remove the size of the received frame for the rx buffer
                    self._rxBuffer = self._rxBuffer[length:]
                    self.log.debug('RX: ' + response_frame.as_hex_string())
                    return response_frame
                else:
                    self.rxErrors += 1
                    return None

            wait_time -= fract_wait_time

        if rx_data_size_total == 0:
            self.log.info('Warning: No response from device')

        return None

    def reset(self):
        """Resets/clears the input buffers.
        """
        # Reset RX buffers
        self._ser.reset_input_buffer()
        self._rxBuffer.clear()

    def close(self):
        if self._ser:
            self._ser.close()
            self._ser = None
