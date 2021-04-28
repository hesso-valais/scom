#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import logging
import time
import unittest
import gc

from tests.sino.scom.paths import update_working_directory
from sino import scom

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


class FakeScomDevice(object):
    def __init__(self, device_type=None):
        super(FakeScomDevice, self).__init__()
        self.device_type = device_type

    def set_device_type(self, device_type):
        self.device_type = device_type


class ScomDevicesObserver(scom.dman.DeviceSubscriber):
    """Receives device notifications if DeviceManager finds Studer devices.
    """

    log = logging.getLogger(__name__)

    def __init__(self):
        super(ScomDevicesObserver, self).__init__()

        self.device_disconnected = False
        self.device_disconnected_device_address = 0

    def on_device_connected(self, device):
        from sino import scom

        # Check if it is an Xtender
        if device.device_type == scom.Device.SD_XTENDER:
            self.log.info('Xtender found!')
            software_version = device.software_version
            self.log.info('Xtender Version: %d.%d.%d' % (software_version['major'],
                                                         software_version['minor'],
                                                         software_version['patch'])
                          )
        else:
            self.log.info('Other device type detected')

    def on_device_disconnected(self, device):
        self.device_disconnected = True
        self.device_disconnected_device_address = device.device_address


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

    def test_get_device_category_by_device(self):
        from sino.scom import dman
        from sino.scom.device import ScomDevice

        for device_name, device_type in ScomDevice.device_categories.items():
            dman.DeviceManager.get_device_category_by_device(FakeScomDevice(device_type))

        with self.assertRaises(AssertionError):
            dman.DeviceManager.get_device_category_by_device(FakeScomDevice(ScomDevice.SD_UNKNOWN))

        with self.assertRaises(AssertionError):
            dman.DeviceManager.get_device_category_by_device(FakeScomDevice(ScomDevice.SD_MAX))


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
                  'scom-device-address-scan': {'xtender': [101, 105],
                                               'vario_power': [4240, 4242]      # Fake devices (added manually)
                                               }
                  }

        # Delete any previously created DeviceManager
        dman.DeviceManager.destroy()

        ScomDeviceHelper.wait_devices_disappeared()

        # Create new device manager
        self.device_manager = dman.DeviceManager(config=config, control_interval_in_seconds=1.0)

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

        observer = ScomDevicesObserver()
        orphaned = ScomDevicesObserver()

        scom.dman.DeviceManager.instance().subscribe(observer)

        time.sleep(1)
        self.assertTrue(scom.dman.DeviceManager.instance().unsubscribe(observer))
        self.assertFalse(scom.dman.DeviceManager.instance().unsubscribe(orphaned))

    def test_scomdevice_disappeared(self):
        from sino import scom

        observer = ScomDevicesObserver()

        self.device_manager._add_new_device('vario_power', 4242)

        # Note: Subscribe after adding new device
        scom.dman.DeviceManager.instance().subscribe(observer)

        time.sleep(2)

        self.assertTrue(observer.device_disconnected)
        self.assertEqual(observer.device_disconnected_device_address, 4242)

