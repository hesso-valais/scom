# -*- coding: utf-8 -*-
#

import sys
from threading import Thread
import time
import logging
import gc

from sino.scom import defines as define
from sino.scom import device
from ..scom import Scom
from ..frame import BaseFrame as ScomBaseFrame
from ..property import Property
from ..device.scomdevice import ScomDevice
from .devicenotifier import DeviceNotifier


class DeviceManager(DeviceNotifier):
    """Manages the Devices found on the SCOM bus.

    Requirements:
    - The DeviceManager scans regularly for Devices on the SCOM bus and notifies
      the DeviceObservers about changes.
    - The DeviceManager is responsible to create an instance for every SCOM device found.
    - The Device Manager needs to hold a list of present devices.
    - In case a device appears on the SCOM bus it notifies the concerning observers with on_device_connected.
    - In case a device disappears, it notifies the observers with onDeviceDisconnect.
    - Scom RX errors are checked regularly and after too many errors the application gets terminated.
    """

    # References single instance of this class.
    _instance = None            # type: DeviceManager

    log = logging.getLogger(__name__)

    _deviceAddressCategory = ('xtender', 'vario_power', 'rcc', 'bsp')
    DEFAULT_RX_BUFFER_SIZE = 1024

    def __init__(self, scom=None, config=None, address_scan_info=None, thread_monitor=None):
        """"""

        if self._instance:
            assert False, 'Only one instance of this class is allowed'
        else:
            self._set_instance(self)

        # Attribute initialization
        self._threadShouldRun = True            # type: bool
        self._subscribers = []                  # type: [dict]
        self._device = {}                       # type: {str, scom.Device}
        self._scomRxErrorMessageSend = False    # type: bool

        if scom:
            self._scom = scom
        else:
            assert config, 'In case \'scom\' is not set the parameter config must be given!'

            studer_com = Scom()
            studer_com.initialize(config['scom']['interface'],
                                  config['scom']['baudrate'] if 'baudrate' in config['scom'] else '38400')

            self._scom = studer_com

        if address_scan_info:
            self._addressScanInfo = address_scan_info
        else:
            assert config, 'In case \'address_scan_info\' is not set the parameter config must be given!'
            assert config.get('scom-device-address-scan'), 'Missing section \'scom-device-address-scan\' in config'

            # Load device address to scan
            self._addressScanInfo = {}
            for deviceTypeName in self._deviceAddressCategory:
                # deviceTypeName ex. 'vario_power' or 'rcc'
                if deviceTypeName in config['scom-device-address-scan']:
                    self._addressScanInfo[deviceTypeName] = config['scom-device-address-scan'][deviceTypeName]
                    assert len(self._addressScanInfo[deviceTypeName]) == 2, 'Need two values for scan info'

        self._thread = Thread(target=self._run_with_exception_logging, name=self.__class__.__name__)
        # Close thread as soon as main thread exits
        self._thread.setDaemon(True)

        if thread_monitor:
            # Register thread for later monitor of itself. Thread monitor allows to take action
            # in case the thread crashes.
            thread_monitor.register(self._thread)

        self._thread.start()

    @classmethod
    def instance(cls):
        """Returns the single instance of this class.
        """
        assert cls._instance, 'Create an instance of this class first'
        return cls._instance

    @classmethod
    def _set_instance(cls, instance):
        assert cls._instance is None, 'Only one instance of this class allowed'
        cls._instance = instance

    def subscribe(self, device_subscriber, filter_policy=('all',)):
        """Reimplementation of DeviceNotifier::subscribe method.
        """
        # Subscribe the info about the new subscriber
        self._subscribers.append({'subscriber': device_subscriber, 'filterPolicy': filter_policy})

        # Notify already present devices to new subscriber
        self._notify_subscriber(device_subscriber, device_category=filter_policy)
        return True

    def unsubscribe(self, device_subscriber):
        """Reimplementation of DeviceNotifier::unsubscribe method.
        """
        # super(DeviceManager, self).unsubscribe(device_subscriber)
        for index, subscriber in enumerate(self._subscribers):
            if subscriber == device_subscriber:
                self._subscribers.pop(index)
                return True
        return False

    def _notify_subscriber(self, device_subscriber, device_category=('all',)):
        """Used to notify new subscribers about already present devices.
        """
        subscriber_info = {'subscriber': device_subscriber, 'device_category': device_category}

        for deviceAddress, the_device in self._device.items():
            device_category = self.get_device_category_by_device(the_device)
            if device_category in subscriber_info['device_category'] or 'all' in subscriber_info['device_category']:
                # Notify subscriber
                subscriber_info['subscriber'].on_device_connected(the_device)

    def _notify_subscribers(self, device, device_category='all', connected=True):
        """Notifies connect/disconnect of a device to all subscribers with the according filter policy.
        """
        # Notify subscribers about the device found
        for subscriberInfo in self._subscribers:
            # Apply subscribers filter policy
            if device_category in subscriberInfo['filterPolicy'] or 'all' in subscriberInfo['filterPolicy']:
                # Notify subscriber
                if connected:
                    subscriberInfo['subscriber'].on_device_connected(device)
                else:
                    subscriberInfo['subscriber'].on_device_disconnected(device)

    @classmethod
    def get_device_category_by_device(cls, device):
        """Returns the device category as string of a given SCOM device.
        """
        device_type = device.device_type
        if device_type == ScomDevice.SD_XTENDER:
            return 'xtender'
        elif device_type == ScomDevice.SD_COMPACT:
            return 'compact'
        elif device_type == ScomDevice.SD_VARIO_TRACK:
            return 'vario_track'
        elif device_type == ScomDevice.SD_VARIO_STRING:
            return 'vario_string'
        elif device_type == ScomDevice.SD_VARIO_POWER:
            return 'vario_power'
        elif device_type == ScomDevice.SD_RCC:
            return 'rcc'
        elif device_type == ScomDevice.SD_BSP:
            return 'bsp'
        else:
            assert False

    def stop(self):
        self._threadShouldRun = False

    @classmethod
    def get_number_of_instances(cls, device_category):
        return ScomDevice.get_number_of_instances(device_category)

    def _run_with_exception_logging(self):
        """Same as _run but logs exceptions to the console or log file.

        This is necessary when running in testing/production environment.
        In case of an exception thrown, the stack trace can be seen in the
        log file. Otherwise there is no info why the thread did stop.
        """
        try:
            self._run()
        except Exception as e:
            logging.error(e, exc_info=True)
        finally:
            # Wait here for a while. If leaving the method directly, the thread
            # gets deleted and the is_alive() method won't work any more!
            time.sleep(5)
            return

    def _run(self):

        self.log.info(type(self).__name__ + ' thread running...')

        while self._threadShouldRun:

            self._search_devices()

            self._check_scom_rx_errors()

#            if self._device[601]:
#                bsp = self._device[601]
#                bsp._test()

            # Wait until next interval begins
            if self._threadShouldRun:
                self._thread_sleep_interval(5)

    def _thread_sleep_interval(self, sleep_interval_in_seconds, decr_value=0.2):
        """Tells the executing thread how long to sleep while being still reactive on _threadShouldRun attribute.
        """
        wait_time = sleep_interval_in_seconds

        while wait_time > 0:
            time.sleep(decr_value)
            wait_time -= decr_value
            # Check if thread should leave run loop
            if not self._threadShouldRun:
                break

    def _get_device_by_address(self, device_address):
        """Returns the studer device instance based on the device address.
        """
        return self._device[device_address] if device_address in self._device else None

    def _search_devices(self):
        """Searches on the SCOM bus for devices.
        """
        assert len(self._addressScanInfo), 'No device categories to scan found!'
        need_garbage_collect = False

        for deviceCategory, addressScanRange in self._addressScanInfo.items():
            device_list = self._search_device_category(deviceCategory, addressScanRange)

            nbr_of_devices_found = len(device_list) if device_list else 0

            if device_list:
                for deviceAddress in device_list:
                    # Check if device is present in device dict
                    if deviceAddress in self._device:
                        pass
                    else:
                        # Let the factory create a new SCOM device representation
                        self._device[deviceAddress] = device.DeviceFactory.create(deviceCategory, deviceAddress)
                        self._device[deviceAddress].class_initialize(self._scom)

                        self.log.info('Found new studer device: %s #%d' % (deviceCategory, deviceAddress))

                        # Notify subscribers about the device found
                        self._notify_subscribers(device=self._device[deviceAddress],
                                                 device_category=deviceCategory,
                                                 connected=True)

            # Compare number of instantiated devices (per category/group) and remove disappeared devices from list
            if nbr_of_devices_found < self.get_number_of_instances(deviceCategory):
                self.log.warning(u'Some ScomDevices seem to be disappeared!')
                missing_device_address_list = self._get_missing_device_addresses(deviceCategory, device_list)

                for missingDeviceAddress in missing_device_address_list:
                    missing_device = self._get_device_by_address(missingDeviceAddress)
                    assert missing_device

                    self.log.info('Studer device disappeared: %s #%d' % (deviceCategory, missingDeviceAddress))

                    # Notify subscribers about the disappeared device
                    self._notify_subscribers(device=missing_device,
                                             device_category=deviceCategory,
                                             connected=False)

                    # Remove studer device from list
                    self._device.pop(missingDeviceAddress)
                    need_garbage_collect = True

        if need_garbage_collect:  # Garbage collect to update WeakValueDictionarys
            gc.collect()

    def _search_device_category(self, device_category, address_scan_range):
        """Searches for devices of a specific category on the SCOM interface.

        :return A list of device address found.
        :type [int]
        """
        device_list = []
        device_start_address = int(address_scan_range[0])
        device_stop_address = int(address_scan_range[1])

        self.log.info('Searching devices in group \'%s\'...' % device_category)

        request_frame = ScomBaseFrame(self.DEFAULT_RX_BUFFER_SIZE)

        device_index = device_start_address
        while device_index <= device_stop_address:
            request_frame.initialize(src_addr=1, dest_addr=device_index)

            prop = Property(request_frame)
            # TODO For some devices 'parameter' value must be read instead of 'user info' (ex. RCC device)
            prop.set_object_read(define.OBJECT_TYPE_READ_USER_INFO,
                                 self._get_search_object_id(device_category),
                                 define.PROPERTY_ID_READ)

            if request_frame.is_valid():
                response_frame = self._scom.write_frame(request_frame, 0.5)    # Set a short timeout during search

                if response_frame and response_frame.is_valid():
                    self.log.info('Found device on address: ' + str(device_index))
                    device_list.append(device_index)
            else:
                self.log.warning('Frame with error: ' + request_frame.last_error())

            device_index += 1

        if len(device_list) == 0:
            self.log.warning('No devices in group \'%s\' found' % device_category)

        return device_list

    def _get_search_object_id(self, device_category):
        """Returns the object id to be used to search for a device.
        """
        assert device_category in self._deviceAddressCategory, 'Category name not in list!'

        if device_category in ('xtender',):
            search_object_id = 3000      # User info: Battery voltage
        elif device_category in ('vario_string', 'vario_power'):
            search_object_id = 15000      # User info: Battery voltage
        elif device_category == 'rcc':
            search_object_id = 5000       # Parameter: Language
        elif device_category == 'bsp':
            search_object_id = 7002       # User info: State of Charge
        else:
            assert False, 'Search object id for device category not set!'

        return search_object_id

    @classmethod
    def _get_missing_device_addresses(cls, device_category, device_address_list):
        """"Searches in actually instantiated devices list (of a category) for devices not found in given device list.

        :param device_category The device category in which to search for devices
        :type device_category str
        :param device_address_list List containing device address (which are still present and not missed)
        :type device_address_list
        """
        missing_device_address_list = []

        device_list = ScomDevice.get_instances_of_category(device_category)

        for device in device_list:
            if device.device_address not in device_address_list:
                missing_device_address_list.append(device.device_address)

        return missing_device_address_list

    def _check_scom_rx_errors(self):
        """Checks how many times there was an RX error on the SCOM bus.

        After a few RX errors are detected, first a message is send (logged) and
        after still more errors the application gets terminated.
        """
        msg = u'Scom bus no more responding!'
        if self._scom.rxErrors > 50 and not self._scomRxErrorMessageSend:
            self.log.critical(msg)
            self._scomRxErrorMessageSend = True

        if self._scom.rxErrors > 100:
            sys.exit(msg)
