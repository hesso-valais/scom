#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import logging
import unittest

from tests.sino.scom.paths import update_working_directory

update_working_directory()  # Needed when: 'pipenv run python -m unittest tests/sino/scom/{this_file}.py'


class TestScomClass(unittest.TestCase):
    """Tests Scom class.
    """

    INTERFACE = '/dev/ttyUSB0'
    BAUDRATE = '38400'
    VALID_FAME = b'\xaa"e\x00\x00\x00\x01\x00\x00\x00\x0c\x00\x93{\x03\x01\x01\x00\xb8\x0b\x00\x00' \
                 b'\x05\x00\x02\x00\xceR'

    log = logging.getLogger(__name__)

    def setUp(self) -> None:
        self.INTERFACE = os.environ.get('SINO_SCOM_TEST_INTERFACE', self.INTERFACE)
        self.BAUDRATE = os.environ.get('SINO_SCOM_TEST_BAUDRATE', self.BAUDRATE)

    def test_object_creation(self):
        from sino.scom import Scom

        scom = Scom()

    def test_bad_serial_conn(self):
        from sino.scom import Scom
        from sino.scom.frame import Frame

        scom = Scom()

        with self.assertRaises(SystemExit):
            scom.initialize('/dev/ttyUSB99')

        with self.assertRaises(AttributeError):
            scom.set_rx_timeout(3)

        tx_frame = Frame()

        with self.assertRaises(AttributeError):
            scom.write_frame(tx_frame)

    def test_valid_serial_conn(self):
        from sino.scom import Scom
        from sino.scom.frame import Frame

        logging.info(f'Test parameters: com: {self.INTERFACE}, baud: {self.BAUDRATE}')

        scom = Scom()
        scom.initialize(self.INTERFACE, int(self.BAUDRATE))  # If this line fails please provide correct INTERFACE and BAUDRATE

        tx_frame = Frame()
        tx_frame.parse_frame_from_string(self.VALID_FAME)

        scom.write_frame(tx_frame)


if __name__ == '__main__':

    # Enable logging
    logging.basicConfig(format='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)

    unittest.main()

