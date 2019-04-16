# -*- coding: utf-8 -*-
#

from abc import ABCMeta, abstractmethod
from sino.scom.device.scomdevice import ScomDevice


class DeviceSubscriber(object):
    """Subscriber interface to get notified about an SCOM device of interest.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def on_device_connected(self, device):
        """Called whenever the DeviceManager detects a new SCOM device (of interest).

        :param device:
        :type device ScomDevice
        :return: None
        """
        pass

    @abstractmethod
    def on_device_disconnected(self, device):
        """Called whenever the DeviceManager detects the disappearance of an SCOM device (of interest).

        :param device:
        :type device ScomDevice
        :return: None
        """