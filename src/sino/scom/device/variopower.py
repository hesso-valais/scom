# -*- coding: utf-8 -*-
#

import struct
import logging
from ..property import Property
from ..frame import BaseFrame
from ..device.scomdevice import ScomDevice


class VarioPower(ScomDevice):

    DEFAULT_RX_BUFFER_SIZE = 1024
    DEVICE_START_ADDRESS = 701              # 101: Extender, 301: Track, 701: String/Power
    DEVICE_MAX_ADDRESS = 705                # 109: Extender, 315: Track, 715: String/Power

    OBJECT_TYPE_READ_USER_INFO = 1
    OBJECT_TYPE_PARAMETER = 2
    OBJECT_TYPE_MESSAGE = 3
    OBJECT_TYPE_CUSTOM_DATALOG = 5
    OBJECT_TYPE_DATALOG_TX = 0x0101

    DEFAULT_VARIOPOWER_SEARCH_OBJ_ID = 15000

    PROPERTY_ID_READ = 0x01
    PROPERTY_VALUE_QSP = 0x05
    PROPERTY_MIN_QSP = 0x06
    PROPERTY_MAX_QSP = 0x07
    PROPERTY_LEVEL_QSP = 0x08               # To get access level: VIEW_ONLY, BASIC, EXPERT, etc.
    PROPERTY_UNSAVED_VALUE_QSP = 0x0D
    PROPERTY_LAST = 0xEE                    # Not Studer specific. Introduced for this project

    scom = None
    log = logging.getLogger(__name__)

    paramInfoTable = {'wiringTypeConfig': {'name': 'wiringTypeConfig', 'number': 14001,
                                           'propertyFormat': 'enum',  'default': 1,
                                           'studerName': 'Configuration of wiring type'},
                      'batteryMaximumVoltage': {'name': 'batteryMaximumVoltage', 'number': 14002,
                                                'propertyFormat': 'float', 'default': 48.0,
                                                'studerName': 'uBatMax'},
                      'batteryMinimumVoltage': {'name': 'batteryMinimumVoltage', 'number': 14003,
                                                'propertyFormat': 'float', 'default': 48.0,
                                                'studerName': 'uBatMin'},
                      'gridMaximumCurrent': {'name': 'gridMaximumCurrent', 'number': 14065, 'propertyFormat': 'float',
                                             'default': 2.0, 'studerName': 'iPvSMax'},
                      'gridMinimumCurrent': {'name': 'gridMinimumCurrent', 'number': 14066, 'propertyFormat': 'float',
                                             'default': -2.0, 'studerName': 'iPvSMin'},
                      'regulationMode': {'name': 'regulationMode', 'number': 14071,
                                         'propertyFormat': 'enum', 'default': 0,
                                         'studerName': 'regModeS'},
                      'gridReferenceCurrent': {'name': 'gridReferenceCurrent', 'number': 14073,
                                               'propertyFormat': 'float', 'default': 0.0,
                                               'studerName': 'iPvSConsigne'},
                      'batteryChargeReferenceCurrent': {'name': 'batteryChargeReferenceCurrent', 'number': 14075,
                                                        'propertyFormat': 'float', 'default': 0.0,
                                                        'studerName': 'iBatSConsigne'},
                      'iuCurveNoLoadVoltage': {'name': 'iuCurveNoLoadVoltage', 'number': 14076,
                                               'propertyFormat': 'float', 'default': 700,
                                               'studerName': 'no load voltage for IU curve (Series)'},
                      'iuCurveCurrentSlope': {'name': 'iuCurveCurrentSlope', 'number': 14077, 'propertyFormat': 'float',
                                              'default': 100, 'studerName': 'current slope for IU curve (Series)'},
                      'powerEnable': {'name': 'powerEnable', 'number': 14081,
                                      'propertyFormat': 'int32', 'default': 0,
                                      'studerName': 'ON of the VarioString'},
                      'powerDisable': {'name': 'powerDisable', 'number': 14082,
                                       'propertyFormat': 'int32', 'default': 0,
                                       'studerName': 'OFF of the VarioString'},
                      }

    userInfoTable = {'batteryVoltage':  {'name': 'batteryCurrent', 'number': 15000,
                                         'propertyFormat': 'float', 'default': 0.0,
                                         'studerName': 'Battery voltage'},
                     'batteryCurrent':  {'name': 'batteryCurrent', 'number': 15001,
                                         'propertyFormat': 'float', 'default': 0.0,
                                         'studerName': 'Battery current'},
                     'pvVoltage':       {'name': 'pvVoltage', 'number': 15004,
                                         'propertyFormat': 'float', 'default': 0.0,
                                         'studerName': 'PV voltage'},
                     'busVoltage':      {'name': 'busVoltage', 'number': 15004,
                                         'propertyFormat': 'float', 'default': 0.0,
                                         'studerName': 'PV voltage'},
                     'pvCurrent':       {'name': 'pvCurrent', 'number': 15007,
                                         'propertyFormat': 'float', 'default': 0.0,
                                         'studerName': 'PV current'},
                     'operatingMode':   {'name': 'operatingMode', 'number': 15013,
                                         'propertyFormat': 'enum',  'default': 0,
                                         'studerName': 'PV operating mode'},
                     'softVersionMsb':  {'name': 'softVersionMsb', 'number': 15077,
                                         'propertyFormat': 'float', 'default': 0.0,
                                         'studerName': 'ID SOFT msb'},
                     'softVersionLsb':  {'name': 'softVersionLsb', 'number': 15078,
                                         'propertyFormat': 'float', 'default': 0.0,
                                         'studerName': 'ID SOFT lsb'},
                     }

    opModeToStringTable = {0: u'Night',
                           1: u'Security',
                           2: u'OFF',
                           3: u'Charge',
                           4: u'limUBat',
                           5: u'limIBat',
                           6: u'limP',
                           7: u'limIPv',
                           8: u'limT',
                           9: u'---',
                           10: u'limIBsp',
                           11: u'limUPv'}

    stringToOpModeTable = {u'Night': 0,
                           u'Security': 1,
                           u'OFF': 2,
                           u'Charge': 3,
                           u'limUBat': 4,
                           u'limIBat': 5,
                           u'limP': 6,
                           u'limIPv': 7,
                           u'limT': 8,
                           u'---': 9,
                           u'limIBsp': 10,
                           u'limUPv': 11}

    def __init__(self, device_address):
        """
        :param device_address The device number on the SCOM interface. Own address of the device.
        :type device_address int
        """
        super(VarioPower, self).__init__(device_address)             # Call base class constructor
        self._add_instance(self.SD_VARIO_POWER)                      # Add this instance to the instance counter

        # Give paramInfoTable to ScomDevice base class
        super(VarioPower, self)._set_param_info_table(self.paramInfoTable)

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
        return self.SD_VARIO_POWER

    @property
    def software_version(self):
        """Implementation of ScomDevice interface.
        """
        return self.get_software_version()

    @classmethod
    def search_devices(cls):
        """Searches for VarioPower devices on the SCOM interface."""
        device_list = []

        request_frame = BaseFrame(cls.DEFAULT_RX_BUFFER_SIZE)

        device_index = cls.DEVICE_START_ADDRESS
        while device_index <= cls.DEVICE_MAX_ADDRESS:
            request_frame.initialize(srcAddr=1, destAddr=device_index)

            prop = Property(request_frame)
            prop.setObjectRead(cls.OBJECT_TYPE_READ_USER_INFO, cls.DEFAULT_VARIOPOWER_SEARCH_OBJ_ID,
                               cls.PROPERTY_ID_READ)

            if request_frame.is_valid():
                response_frame = cls.scom.writeFrame(request_frame, 0.5)    # Set a short timeout during search)

                if response_frame and response_frame.isValid():
                    cls.log.info('Found VarioPower on address: ' + str(device_index))
                    device_list.append(device_index)
            else:
                cls.log.warning('Frame with error: ' + request_frame.last_error())

            device_index += 1

        if len(device_list) == 0:
            cls.log.warning('No VarioPower devices found')

        return device_list

    @classmethod
    def _string_to_regulation_mode(cls, s):
        """Converts a human readable sting to regModeS.
        """
        reg_mode_s = 0

        if s == u'uPv':
            reg_mode_s = 1
        elif s == u'iPv':
            reg_mode_s = 2
        elif s == u'pPv':
            reg_mode_s = 4
        elif s == u'iBat':
            reg_mode_s = 8
        elif s == u'PVSim':
            reg_mode_s = 16
        elif s == u'IUcurve':
            reg_mode_s = 32

        return reg_mode_s

    @classmethod
    def _wiring_type_to_string(cls, wtc):
        result = ''
        if wtc == 1:
            result = 'independent'
        elif wtc == 2:
            result = 'serial'
        elif wtc == 4:
            result = 'parallel'
        return result

    def get_battery_voltage(self):
        """Reads and returns the actual battery voltage."""
        return self._read_user_info_ex(self.userInfoTable['batteryVoltage'])

    def get_battery_current(self):
        """Reads and returns the actual battery current."""
        return self._read_user_info_ex(self.userInfoTable['batteryCurrent'])

    def get_grid_current(self):
        """Reads and returns the actual grid current."""
        return self._read_user_info_ex(self.userInfoTable['pvCurrent'])

    def get_operating_mode(self):
        """Reads and returns the actual operating mode."""
        return self._read_user_info_ex(self.userInfoTable['operatingMode'])

    def get_grid_voltage(self):
        """Reads and returns the actual PV/grid voltage."""
        return self._read_user_info_ex(self.userInfoTable['busVoltage'])

    def get_software_version(self):
        id_soft_msb = self._read_user_info_ex(self.userInfoTable['softVersionMsb'])
        id_soft_lsb = self._read_user_info_ex(self.userInfoTable['softVersionLsb'])

        if id_soft_msb and id_soft_lsb:
            id_soft_major_version = int(id_soft_msb) >> 8
            id_soft_minor_version = int(id_soft_lsb) >> 8
            id_soft_revision = int(id_soft_lsb) & 0xFF

            return {'major': id_soft_major_version, 'minor': id_soft_minor_version, 'patch': id_soft_revision}
        return {'major': 0, 'minor': 0, 'patch': 0}

    def get_regulation_mode(self):
        """Reads and returns the actual regulation mode."""
        return self._read_parameter_info('regulationMode')

    def set_regulation_mode(self, regulation_mode):
        """Sets the regulation mode of the device.

        :param regulation_mode The regulation mode as string 'uPv, iPV, etc.'
        :type regulation_mode str
        :return True on success
        """
        reg_mode_s = self._string_to_regulation_mode(regulation_mode)

        if reg_mode_s != 0:
            return self._write_parameter_info('regulationMode', reg_mode_s, property_id=self.PROPERTY_VALUE_QSP)
        return False

    def get_battery_charge_current(self, property_id_name='value'):
        current = 0.0

        property_id = self.PROPERTY_VALUE_QSP
        if property_id_name == 'min':
            property_id = self.PROPERTY_MIN_QSP
        elif property_id_name == 'max':
            property_id = self.PROPERTY_MAX_QSP

        value = self._read_parameter(1138, property_id)   # 1138

        if value:
            current = struct.unpack('f', value[0:4])[0]

        return current

    def set_grid_reference_current(self, current):
        """Sets the grid reference current.

        Positive values for parameter 'current' means charging the battery!
        If you want to feed energy to the grid you need to give a negative
        value.
        Please take in mind that the battery may not be able to give the
        needed current as between the grid current and the battery current
        is about a factor of GridVoltage/BatteryVoltage (ex. 700V/50V=14).

        Takes only affect if the regulation mode is set to 'iPv'.
        """
        try:
            self._write_parameter_info('gridReferenceCurrent', current, property_id=self.PROPERTY_UNSAVED_VALUE_QSP)
        except:
            return False
        return True

    def set_battery_charge_reference_current(self, current, property_id=PROPERTY_UNSAVED_VALUE_QSP):
        """Sets the battery charge reference current.

        Takes only affect if the regulation mode is set to 'iBat'.
        """
        return self._write_parameter_info('batteryChargeReferenceCurrent', current, property_id=property_id)

    def get_battery_charge_reference_current(self, property_id=PROPERTY_LAST):
        """Returns the battery charge reference current.
        """
        return self._read_parameter_info('batteryChargeReferenceCurrent', property_id=property_id)

    def set_power_enable(self, enable) -> bool:
        """Enables/disables the VarioPower.
        """
        try:
            if enable:
                self._write_parameter_info('powerEnable', 1)
            else:
                self._write_parameter_info('powerDisable', 1)
        except:
            return False
        return True

    def get_wiring_type_config(self):
        return self._read_parameter_info('wiringTypeConfig')

    def set_wiring_type_config(self, new_value=2):
        """Set the wiring type of the device.

            1: Independent, 2: Serial, 3: Parallel
        """
        return self._write_parameter_info('wiringTypeConfig', new_value, self.PROPERTY_VALUE_QSP)

    def get_wiring_type_config_as_string(self):
        wtc = self.get_wiring_type_config()
        return self._wiring_type_to_string(wtc)

    def get_battery_maximum_voltage(self):
        return self._read_parameter_info('batteryMaximumVoltage')

    def set_battery_maximum_voltage(self, new_value):
        """Sets the maximum battery voltage.
        """
        return self._write_parameter_info('batteryMaximumVoltage', new_value, self.PROPERTY_UNSAVED_VALUE_QSP)

    def get_battery_minimum_voltage(self):
        return self._read_parameter_info('batteryMinimumVoltage')

    def set_battery_minimum_voltage(self, new_value):
        """Sets the minimum battery voltage.
        """
        return self._write_parameter_info('batteryMinimumVoltage', new_value, self.PROPERTY_UNSAVED_VALUE_QSP)

    def set_iu_curve_no_load_voltage(self, new_value=700.0):
        """Sets the no load voltage for IU curve.

            Only available in IUcurve regulation mode
        """
        return self._write_parameter_info('iuCurveNoLoadVoltage', new_value, self.PROPERTY_UNSAVED_VALUE_QSP)

    def get_iu_curve_no_load_voltage(self, property_id=PROPERTY_UNSAVED_VALUE_QSP):
        """Gets the no load voltage for IU curve.

            Only available in IUcurve regulation mode
        """
        return self._read_parameter_info('iuCurveNoLoadVoltage', property_id)

    def set_grid_maximum_current(self, new_value):
        """Sets the maximum allowable grid current.

        Scaling error: all demanded values has to be divided by a factor of 5.333
        """
        return self._write_parameter_info('gridMaximumCurrent', new_value, self.PROPERTY_UNSAVED_VALUE_QSP)

    def get_grid_maximum_current(self, property_id=PROPERTY_UNSAVED_VALUE_QSP):
        """Gets the allowable positive grid current limitation.
        By changing propertyIdName max and min values can be read.
        """
        return self._read_parameter_info('gridMaximumCurrent', property_id)

    def set_grid_minimum_current(self, new_value):
        """Sets the maximum allowable grid current.
        """
        return self._write_parameter_info('gridMinimumCurrent', new_value, self.PROPERTY_UNSAVED_VALUE_QSP)

    def get_grid_minimum_current(self, property_id=PROPERTY_UNSAVED_VALUE_QSP):
        """Gets the allowable negative grid current limitation.
        By changing propertyIdName max and min values can be read.
        """
        return self._read_parameter_info('gridMinimumCurrent', property_id)

    def set_iu_curve_slope(self, new_value):
        """Sets the maximum allowable grid current.
        """
        return self._write_parameter_info('iuCurveCurrentSlope', new_value, self.PROPERTY_UNSAVED_VALUE_QSP)

    def get_iu_curve_slope(self, property_id=PROPERTY_UNSAVED_VALUE_QSP):
        """Gets the IUcurve current slope.

        """
        return self._read_parameter_info('iuCurveCurrentSlope', property_id)
