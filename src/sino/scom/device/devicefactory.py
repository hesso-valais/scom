# -*- coding: utf-8 -*-
#

from .scomdevice import ScomDevice
from .variopower import VarioPower
from .xtender import Xtender
from .bsp import Bsp


class DeviceFactory(object):
    """Creates Studer device representations.
    """

    @classmethod
    def create(cls, device_category, device_address):
        """Creates a new studer device according to the category given.
        """
        dev_cat = device_category.lower()

        if dev_cat == 'vario_power':
            new_device = VarioPower(device_address)
        elif dev_cat == 'xtender':
            new_device = Xtender(device_address)
        elif dev_cat == 'bsp':
            new_device = Bsp(device_address)
        else:
            assert False

        return new_device

    @classmethod
    def get_number_of_instances(cls, device_category):
        """Wrapper method to same method of ScomDevice."""
        return ScomDevice.get_number_of_instances(device_category)

    @classmethod
    def get_instances_of_category(cls, device_category):
        """Wrapper method to same method of ScomDevice."""
        return ScomDevice.get_instances_of_category(device_category)
