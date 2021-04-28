#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import logging
import time
import unittest

import gc

from tests.sino.scom.paths import update_working_directory

update_working_directory()  # Needed when: 'pipenv run python -m unittest tests/sino/scom/{this_file}.py'


class ScomDeviceHelper(object):
    def __init__(self):
        super(ScomDeviceHelper, self).__init__()

    log = logging.getLogger(__name__)

    @classmethod
    def wait_devices_disappeared(cls):
        from sino.scom.device import ScomDevice

        # Wait for previous ScomDevices to disappear
        while ScomDevice.get_number_of_instances('xtender') > 0:
            cls.log.info('Waiting for Xtenders to disappear...')
            time.sleep(0.5)
            gc.collect()


class TestDeviceManagerObjectCreation(unittest.TestCase):
    """Tests dman.DeviceManager object creation.
    """

    INTERFACE = '/dev/ttyUSB0'
    BAUDRATE = '38400'
    CONFIG = {'scom': {'interface': INTERFACE, 'baudrate': BAUDRATE},
              'scom-device-address-scan': {'xtender': [101, 105]}
              }

    log = logging.getLogger(__name__)

    def setUp(self) -> None:
        from sino.scom import dman

        self.INTERFACE = os.environ.get('SINO_SCOM_TEST_INTERFACE', self.INTERFACE)
        self.BAUDRATE = os.environ.get('SINO_SCOM_TEST_BAUDRATE', self.BAUDRATE)

        logging.basicConfig(level=logging.INFO)

        # Delete any previously created DeviceManager
        dman.DeviceManager.destroy()

        ScomDeviceHelper.wait_devices_disappeared()

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

    def test_scom_already_present(self):
        from sino.scom import Scom
        from sino.scom import dman

        scom = Scom()
        scom.initialize(self.INTERFACE, int(self.BAUDRATE))

        dman.DeviceManager(scom=scom, config=self.CONFIG, address_scan_info=self.CONFIG['scom-device-address-scan'])

        dman.DeviceManager.destroy()
        scom.close()

    def test_thread_monitor(self):

        class ThreadMon(object):
            def register(self, instance):
                pass

        from sino.scom import Scom
        from sino.scom import dman

        scom = Scom()
        scom.initialize(self.INTERFACE, int(self.BAUDRATE))

        device_manager = dman.DeviceManager(scom=scom, config=self.CONFIG, thread_monitor=ThreadMon())

        # Check instance getter
        self.assertTrue(device_manager == dman.DeviceManager.instance())

        dman.DeviceManager.destroy()
        scom.close()


class TestDeviceManagerClassForceDelete(unittest.TestCase):
    """Tests dman.DeviceManager class.

    Note: DeviceManager instance is deleted after test
    """

    INTERFACE = '/dev/ttyUSB0'
    BAUDRATE = '38400'

    log = logging.getLogger(__name__)

    def setUp(self) -> None:
        from sino.scom import dman

        self.INTERFACE = os.environ.get('SINO_SCOM_TEST_INTERFACE', self.INTERFACE)
        self.BAUDRATE = os.environ.get('SINO_SCOM_TEST_BAUDRATE', self.BAUDRATE)

        logging.basicConfig(level=logging.INFO)

        config = {'scom': {'interface': self.INTERFACE, 'baudrate': self.BAUDRATE},
                  'scom-device-address-scan': {'xtender': [101, 105]}
                  }

        # Delete any previously created DeviceManager
        dman.DeviceManager.destroy()

        ScomDeviceHelper.wait_devices_disappeared()

        # Create new device manager
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


class TestDeviceManagerClass(unittest.TestCase):
    """Tests dman.DeviceManager class.

    Note: DeviceManager instance is properly destroyed after test.
    """

    INTERFACE = '/dev/ttyUSB0'
    BAUDRATE = '38400'

    log = logging.getLogger(__name__)

    def setUp(self) -> None:
        from sino.scom import dman

        self.INTERFACE = os.environ.get('SINO_SCOM_TEST_INTERFACE', self.INTERFACE)
        self.BAUDRATE = os.environ.get('SINO_SCOM_TEST_BAUDRATE', self.BAUDRATE)

        logging.basicConfig(level=logging.INFO)

        config = {'scom': {'interface': self.INTERFACE, 'baudrate': self.BAUDRATE},
                  'scom-device-address-scan': {'xtender': [101, 105]}
                  }

        # Delete any previously created DeviceManager
        dman.DeviceManager.destroy()

        ScomDeviceHelper.wait_devices_disappeared()

        # Create new device manager
        self.device_manager = dman.DeviceManager(config=config)

    def tearDown(self) -> None:
        self.device_manager.destroy()
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

    def test_additional_instance(self):
        from sino.scom import dman

        config = {'scom': {'interface': self.INTERFACE, 'baudrate': self.BAUDRATE},
                  'scom-device-address-scan': {'xtender': [101, 105]}
                  }

        # Create new device manager
        with self.assertRaises(AssertionError):
            dman.DeviceManager(config=config)

    def test_subscribe_unsubscribe(self):
        from sino import scom

        class ScomDevicesObserver(scom.dman.DeviceSubscriber):
            """Receives device notifications if DeviceManager finds Studer devices.
            """

            log = logging.getLogger(__name__)

            def __init__(self):
                super(ScomDevicesObserver, self).__init__()

            def on_device_connected(self, device):

                # Check if it is an Xtender
                if device.device_type == scom.Device.SD_XTENDER:
                    self.log.info('Xtender found!')
                    software_version = device.software_version
                    self.log.info('Xtender Version: %d.%d.%d' % (software_version['major'],
                                                                 software_version['minor'],
                                                                 software_version['patch'])
                                  )
                else:
                    print('Other device type detected')

            def on_device_disconnected(self, device):
                pass
        observer = ScomDevicesObserver()
        orphaned = ScomDevicesObserver()

        scom.dman.DeviceManager.instance().subscribe(observer)

        time.sleep(1)
        scom.dman.DeviceManager.instance().unsubscribe(observer)
        scom.dman.DeviceManager.instance().unsubscribe(orphaned)
