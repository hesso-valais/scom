# -*- coding: utf-8 -*-
#

import logging
from ..device.scomdevice import ScomDevice


class Bsp(ScomDevice):
    """Provides access to a Battery Status Processor (BSP).
    """

    DEVICE_START_ADDRESS = 601
    DEVICE_MAX_ADDRESS = 615

    PROPERTY_VALUE_QSP = 0x05

    scom = None
    log = logging.getLogger(__name__)

    paramInfoTable = {
        'voltageOfTheSystem': {'name': 'voltageOfTheSystem', 'number': 6057,
                               'propertyFormat': 'enum', 'default': 0x01,
                               'studerName': 'Voltage of the system'},
        'nominalCapacity': {'name': 'nominalCapacity', 'number': 6001,
                            'propertyFormat': 'float', 'default': 110,
                            'studerName': 'Nominal capacity'},
        'nominalDischargeDuration': {'name': 'nominalDischargeDuration', 'number': 6002,
                                     'propertyFormat': 'float', 'default': 20,
                                     'studerName': 'Nominal discharge duration (C-rating)'},
        'nominalShuntCurrent': {'name': 'nominalShuntCurrent', 'number': 6017,
                                'propertyFormat': 'float', 'default': 500,
                                'studerName': 'Nominal shunt current'},
        'nominalShuntVoltage': {'name': 'nominalShuntVoltage', 'number': 6018,
                                'propertyFormat': 'float', 'default': 50,
                                'studerName': 'Nominal shunt voltage'},
        'manufacturer_soc_zero': {'name': 'manufacturer_soc_zero', 'number': 6055, 'propertyFormat': 'float',
                                  'default': 30, 'studerName': 'Manufacturer SOC for 0 % displayed'},
        'manufacturer_soc_hundred': {'name': 'manufacturer_soc_hundred', 'number': 6056, 'propertyFormat': 'float',
                                     'default': 100, 'studerName': 'Manufacturer SOC for 100 % displayed'},
    }

    userInfoTable = {
        'batteryVoltage': {'name': 'batteryVoltage', 'number': 7000, 'propertyFormat': 'float', 'default': 0.0,
                           'studerName': 'Battery voltage'},
        'batteryCurrent': {'name': 'batteryCurrent', 'number': 7001, 'propertyFormat': 'float', 'default': 0.0,
                           'studerName': 'Battery current'},
        'soc': {'name': 'soc', 'number': 7002, 'propertyFormat': 'float', 'default': 0.0,
                'studerName': 'State of Charge'},
        'power': {'name': 'power', 'number': 7003, 'propertyFormat': 'float', 'default': 0.0,
                  'studerName': 'Power'},
        'remainingAutonomy': {'name': 'remainingAutonomy', 'number': 7004, 'propertyFormat': 'float', 'default': 0.0,
                              'studerName': 'Remaining autonomy'},

        'softVersionMsb': {'name': 'softVersionMsb', 'number': 7037, 'propertyFormat': 'float', 'default': 0.0,
                           'studerName': 'ID SOFT msb'},
        'softVersionLsb': {'name': 'softVersionLsb', 'number': 7038, 'propertyFormat': 'float', 'default': 0.0,
                           'studerName': 'ID SOFT lsb'},
    }

    systemVoltageToStringTable = {0: u'Invalid',
                                  1: u'Automatic',
                                  2: u'12V',
                                  4: u'24V',
                                  8: u'48V'}

    def __init__(self, device_address):
        """
        :param device_address The device number on the SCOM interface. Own address of the device.
        :type device_address int
        """
        super(Bsp, self).__init__(device_address)                   # Call base class constructor
        self._add_instance(self.SD_BSP)                             # Add this instance to the instance counter

        # Give paramInfoTable to ScomDevice base class
        super(Bsp, self)._set_param_info_table(self.paramInfoTable)

    @classmethod
    def class_initialize(cls, scom):
        """Tells devices with which SCOM interface to communicate."""
        cls.scom = scom

    @classmethod
    def _get_scom(cls):
        """Implementation of ScomDevice interface.
        """
        return cls.scom

    @property
    def device_type(self):
        """Implementation of ScomDevice interface.
        """
        return self.SD_BSP

    @property
    def software_version(self):
        """Implementation of ScomDevice interface.
        """
        return self.get_software_version()

    def get_software_version(self):
        id_soft_msb = self._read_user_info_ex(self.userInfoTable['softVersionMsb'])
        id_soft_lsb = self._read_user_info_ex(self.userInfoTable['softVersionLsb'])

        if id_soft_msb and id_soft_lsb:
            id_soft_major_version = int(id_soft_msb) >> 8
            id_soft_minor_version = int(id_soft_lsb) >> 8
            id_soft_revision = int(id_soft_lsb) & 0xFF

            return {'major': id_soft_major_version, 'minor': id_soft_minor_version, 'patch': id_soft_revision}
        return {'major': 0, 'minor': 0, 'patch': 0}

    def get_battery_voltage(self):
        """Reads and returns the actual battery voltage."""
        return self._read_user_info_ex(self.userInfoTable['batteryVoltage'])

    def get_battery_current(self):
        """Reads and returns the actual battery current [A]."""
        return self._read_user_info_ex(self.userInfoTable['batteryCurrent'])

    def get_soc(self):
        """Reads and returns the actual state of charge [%]."""
        return self._read_user_info_ex(self.userInfoTable['soc'])

    def get_power(self):
        """Reads and returns the actual power [W]."""
        return self._read_user_info_ex(self.userInfoTable['power'])

    def get_remaining_autonomity(self):
        """Reads and returns the remaining autonomity in minutes."""
        return self._read_user_info_ex(self.userInfoTable['remainingAutonomy'])

    def get_voltage_of_the_system(self):
        return self._read_parameter_info('voltageOfTheSystem')

    def get_nominal_capacity(self):
        return self._read_parameter_info('nominalCapacity')

    def setNominalCapacity(self, value):
        """Sets the nominal battery capacity.

        Caution:
        Should be used with care. Calling this method too often
        will damage the Flash of the device!
        """
        return self._write_parameter_info('nominalCapacity', value, property_id=self.PROPERTY_VALUE_QSP)

    def get_nominal_discharge_duration(self):
        return self._read_parameter_info('nominalDischargeDuration')

    def set_nominal_discharge_duration(self, value):
        """Sets the nominal discharge duration.

        Caution:
        Should be used with care. Calling this method too often
        will damage the Flash of the device!
        """
        return self._write_parameter_info('nominalDischargeDuration', value, property_id=self.PROPERTY_VALUE_QSP)

    def get_nominal_shunt_current(self):
        return self._read_parameter_info('nominalShuntCurrent')

    def get_nominal_shunt_voltage(self):
        return self._read_parameter_info('nominalShuntVoltage')

    def set_manufacturer_soc_zero(self, value):
        return self._write_parameter_info('manufacturer_soc_zero', value, property_id=self.PROPERTY_VALUE_QSP)

    def set_manufacturer_soc_hundred(self, value):
        return self._write_parameter_info('manufacturer_soc_hundred', value, property_id=self.PROPERTY_VALUE_QSP)

    def _test(self):
        # self.setNominalCapacity(900)
        # self.setNominalDischargeDuration(10)

        value = self.software_version
        value = self.get_battery_voltage()
        value = self.get_battery_current()
        value = self.get_soc()
        value = self.get_power()
        value = self.get_remaining_autonomity()
        value = self.get_voltage_of_the_system()
        value = self.get_nominal_capacity()
        value = self.get_nominal_discharge_duration()
        value = self.get_nominal_shunt_current()
        value = self.get_nominal_shunt_voltage()
        value = value
