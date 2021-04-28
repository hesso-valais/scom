#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import logging
import time
import unittest

import gc

from tests.sino.scom.paths import update_working_directory

update_working_directory()  # Needed when: 'pipenv run python -m unittest tests/sino/scom/{this_file}.py'


class TestDeviceManagerObjectCreation(unittest.TestCase):
    """Tests dman.DeviceManager object creation.
    """

    INTERFACE = '/dev/ttyUSB0'
    BAUDRATE = '38400'

    log = logging.getLogger(__name__)

    def setUp(self) -> None:
        from sino.scom import dman
        from sino.scom.device import ScomDevice

        self.INTERFACE = os.environ.get('SINO_SCOM_TEST_INTERFACE', self.INTERFACE)
        self.BAUDRATE = os.environ.get('SINO_SCOM_TEST_BAUDRATE', self.BAUDRATE)

        logging.basicConfig(level=logging.INFO)

        # Delete any previously created DeviceManager
        dman.DeviceManager.destroy()

    def test_object_creation(self):
        from sino.scom import dman

        config = {'scom': {'interface': self.INTERFACE, 'baudrate': self.BAUDRATE},
                  'scom-device-address-scan': {'xtender': [101, 105]}
                  }

        device_manager = dman.DeviceManager(config=config)

        time.sleep(1)

        xtenders = device_manager.get_number_of_instances('xtender')
        if xtenders:
            self.log.info(f'Found {xtenders} Xtenders')
        else:
            self.log.info('Did not find any Xtenders')

        device_manager.stop()
        time.sleep(1)

        del device_manager
        gc.collect()


class TestDeviceManagerClass(unittest.TestCase):
    """Tests dman.DeviceManager class.
    """

    INTERFACE = '/dev/ttyUSB0'
    BAUDRATE = '38400'

    log = logging.getLogger(__name__)

    def setUp(self) -> None:
        from sino.scom import dman
        from sino.scom.device import ScomDevice

        self.INTERFACE = os.environ.get('SINO_SCOM_TEST_INTERFACE', self.INTERFACE)
        self.BAUDRATE = os.environ.get('SINO_SCOM_TEST_BAUDRATE', self.BAUDRATE)

        logging.basicConfig(level=logging.INFO)

        config = {'scom': {'interface': self.INTERFACE, 'baudrate': self.BAUDRATE},
                  'scom-device-address-scan': {'xtender': [101, 105]}
                  }

        # Delete any previously created DeviceManager
        dman.DeviceManager.destroy()

        # Wait for previous ScomDevices to disappear
        while ScomDevice.get_number_of_instances('xtender') > 0:
            self.log.info('Waiting for Xtenders to disappear...')
            time.sleep(0.5)
            gc.collect()

        self.device_manager = dman.DeviceManager(config=config)

    def tearDown(self) -> None:
        # Delete device manager so the internally used serial communication gets closed
        del self.device_manager
        # Force garbage collection
        gc.collect()

    def test_get_number_of_instances_no_wait_time(self):

        xtenders = self.device_manager.get_number_of_instances('xtender')
        if xtenders:
            self.log.info(f'Found {xtenders} Xtenders')
        else:
            self.log.info('Did not find any Xtenders')

    def test_get_number_of_instances_wait_second(self):
        time.sleep(1)
        xtenders = self.device_manager.get_number_of_instances('xtender')
        if xtenders:
            self.log.info(f'Found {xtenders} Xtenders')
        else:
            self.log.info('Did not find any Xtenders')
