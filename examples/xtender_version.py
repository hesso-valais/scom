#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import time
import sys
import os

# In case 'scom' package is not installed, try to work with local source files.
# You may need to build extension modules 'baseframe' and 'property' using the
# 'scripts/build-scomlib.sh' script.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '../src')))

from sino import scom

"""
Example showing how to use the SCOM DeviceManager to find Studer devices
on the SCOM bus.

The following Example tries to detect some Xtender's. For each
Xtender device found the software version is then print out.
"""

# SCOM configuration
config = {'scom': {'interface': '/dev/ttyUSB0',
                   'baudrate': '38400'},
          'scom-device-address-scan': {'xtender': [101, 105]}
          }


class ScomDevicesObserver(scom.dman.DeviceSubscriber):
    """Receives device notifications if DeviceManager finds Studer devices.
    """
    def __init__(self):
        super(ScomDevicesObserver, self).__init__()

        scom.dman.DeviceManager.instance().subscribe(self)

    def on_device_connected(self, device):

        # Check if it is an Xtender
        if device.device_type == scom.Device.SD_XTENDER:
            print('Xtender found!')
            software_version = device.software_version
            print('Xtender Version: %d.%d.%d' % (software_version['major'],
                                                 software_version['minor'],
                                                 software_version['patch'])
                  )
        else:
            print('Other device type detected')


def main():
    # Create device manager detecting devices on the SCOM bus
    device_manager = scom.dman.DeviceManager(config=config)

    # Create observer waiting for DeviceManager notifications
    devices_observer = ScomDevicesObserver()

    # Wait a bit. Things gets done in the on_device_connected() method
    # of the ScomDevicesObserver class
    time.sleep(5)
    print('Done')


if __name__ == '__main__':
    main()
