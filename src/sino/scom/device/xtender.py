# -*- coding: utf-8 -*-
#

import struct
import logging
from ..defines import *
from ..property import Property
from ..frame import Frame as ScomFrame
from .scomdevice import ScomDevice
from .common.paramproxycontainer import ParamProxyContainer


class Xtender(ScomDevice):
    """Provides access to an Xtender.
    """
    scom = None
    log = logging.getLogger(__name__)

    paramInfoTable = {
        'powerOnXtender': {'name': 'powerOnXtender', 'number': 1576,
                                   'propertyFormat': 'bool', 'default': False,
                                   'studerName': 'ON/OFF command'},
        'powerOnAllXtenders': {'name': 'powerOnAllXtenders', 'number': 1415,
                               'propertyFormat': 'signal', 'default': False,
                               'studerName': 'ON of the Xtenders'},
        'powerOffAllXtenders': {'name': 'powerOffAllXtenders', 'number': 1399,
                                'propertyFormat': 'signal', 'default': False,
                                'studerName': 'ON of the Xtenders'},
        'resetAllInverters': {'name': 'resetAllInverters', 'number': 1468,
                              'propertyFormat': 'signal', 'default': False,
                              'studerName': 'Reset all of the inverters'},
        'maximumAcInputCurrent': {'name': 'maximumAcInputCurrent', 'number': 1107,
                                  'propertyFormat': 'float', 'default': 0.0,
                                  'studerName': 'Maximum current of AC source (input limit)'},
        'allowInverter': {'name': 'allowInverter', 'number': 1124, 'propertyFormat': 'bool', 'default': True,
                          'studerName': 'Inverter allowed'},
        'allowCharger': {'name': 'allowCharger', 'number': 1125, 'propertyFormat': 'bool', 'default': True,
                         'studerName': 'Charger allowed'},
        'batteryChargeReferenceCurrent': {'name': 'batteryChargeReferenceCurrent', 'number': 1138,
                                          'propertyFormat': 'float', 'default': 0.0,
                                          'studerName': 'Battery charge current'},
        'standbyPowerLevel': {'name': 'standbyPowerLevel', 'number': 1187,
                              'propertyFormat': 'float', 'default': 0.0, 'studerName': 'Standby level'},
        'restoreDefaultSettings': {'name': 'restoreDefaultSettings', 'number': 1395,
                                   'propertyFormat': 'signal', 'default': False,
                                   'studerName': 'Restore Default Settings'},
        'restoreFactorySettings': {'name': 'restoreFactorySettings', 'number': 1287,
                                   'propertyFormat': 'signal', 'default': False,
                                   'studerName': 'Restore Factory Settings'},
        'batteryMinimumVoltageWithoutLoad': {'name': 'batteryMinimumVoltageWithoutLoad', 'number': 1108,
                                             'propertyFormat': 'float', 'default': 0.0,
                                             'studerName': 'Battery undervoltage level without load'},
        'batteryMinimumVoltageWithLoad': {'name': 'batteryMinimumVoltageWithLoad', 'number': 1109,
                                          'propertyFormat': 'float', 'default': 0.0,
                                          'studerName': 'Battery undervoltage level without load'},
        'batteryMaximumVoltage': {'name': 'batteryMaximumVoltage', 'number': 1121,
                                  'propertyFormat': 'float', 'default': 0.0,
                                  'studerName': 'Battery overvoltage level'},
        'floatingVoltage': {'name': 'floatingVoltage', 'number': 1140,
                            'propertyFormat': 'float', 'default': 0.0, 'studerName': 'Floating voltage'},
        'forceFloatingPhase': {'name': 'forceFloatingPhase', 'number': 1467,
                               'propertyFormat': 'signal', 'default': False, 'studerName': 'Force phase of floating'},
        'forceNewChargeCycle': {'name': 'forceNewChargeCycle', 'number': 1142,
                                'propertyFormat': 'signal', 'default': False, 'studerName': 'Force a new cycle'},
        'autoAcInputCurrentReduction': {'name': 'autoAcInputCurrentReduction', 'number': 1527,
                                        'propertyFormat': 'bool', 'default': False,
                                        'studerName': 'Decrease max input limit current with AC-In voltage'},
        'boostPhaseAllowed': {'name': 'boostPhaseAllowed', 'number': 1155,
                              'propertyFormat': 'bool', 'default': True, 'studerName': 'Absorption phase allowed'},
        'boostVoltage': {'name': 'boostVoltage', 'number': 1156,
                         'propertyFormat': 'float', 'default': 0.0, 'studerName': 'Absorption voltage'},
        'inputCurrentAdaptionRange': {'name': 'inputCurrentAdaptionRange', 'number': 1433,
                                      'propertyFormat': 'float', 'default': 0.0, 'studerName':
                                      'Adaptation range of the input current according to the input voltage'},
        # GRID-FEEDING
        'gridFeedingAllowed': {'name': 'gridFeedingAllowed', 'number': 1127,
                               'propertyFormat': 'bool', 'default': False, 'studerName': 'Grid feeding allowed'},
        'gridFeedingMaximumCurrent': {'name': 'gridFeedingMaximumCurrent', 'number': 1523,
                                      'propertyFormat': 'float', 'default': 0.0,
                                      'studerName': 'Max grid feeding current'},
        'gridFeedingBatteryVoltage': {'name': 'gridFeedingBatteryVoltage', 'number': 1524,
                                      'propertyFormat': 'float', 'default': 0.0,
                                      'studerName': 'Battery voltage target for forced grid feeding'},
        'gridFeedingStartTime': {'name': 'gridFeedingStartTime', 'number': 1525,
                                 'propertyFormat': 'int32', 'default': 0,
                                 'studerName': 'Forced grid feeding start time'},
        'gridFeedingStopTime': {'name': 'gridFeedingStopTime', 'number': 1526,
                                'propertyFormat': 'int32', 'default': 0,
                                'studerName': 'Forced grid feeding stop time'},
        'frequencyControlEnabled': {'name': 'frequencyControlEnabled', 'number': 1627,
                                    'propertyFormat': 'bool', 'default': False,
                                    'studerName': 'ARN4105 frequency control enabled'},
        # Battery Priority
        'batteryPriorityAsEnergySource': {'name': 'batteryPriorityAsEnergySource', 'number': 1296,
                                          'propertyFormat': 'bool', 'default': False,
                                          'studerName': 'Batteries priority as energy source'},
        'batteryPriorityVoltage': {'name': 'batteryPriorityVoltage', 'number': 1297,
                                   'propertyFormat': 'float', 'default': 0.0,
                                   'studerName': 'Battery priority voltage'},
        }

    userInfoTable = {
        'batteryVoltage': {'name': 'batteryVoltage', 'number': 3000, 'propertyFormat': 'float', 'default': 0.0,
                           'studerName': 'Battery voltage'},
        'batteryChargeReferenceCurrent': {'name': 'batteryChargeReferenceCurrent',
                                          'number': 3004, 'propertyFormat': 'float', 'default': 0.0,
                                          'studerName': 'Wanted battery charge current'},
        'batteryCurrent': {'name': 'batteryCurrent', 'number': 3005, 'propertyFormat': 'float', 'default': 0.0,
                           'studerName': 'Battery charge current'},
        'soc': {'name': 'soc', 'number': 3007, 'propertyFormat': 'float', 'default': 0.0,
                'studerName': 'State of charge'},
        'batteryCyclePhase': {'name': 'batteryCyclePhase', 'number': 3010, 'propertyFormat': 'enum',
                              'default': 0, 'studerName': 'Battery cycle phase'},
        'pvVoltage': {'name': 'pvVoltage', 'number': 3011, 'propertyFormat': 'float', 'default': 0.0,
                      'studerName': 'Input voltage'},
        'inputVoltage': {'name': 'inputVoltage', 'number': 3011, 'propertyFormat': 'float', 'default': 0.0,
                         'studerName': 'Input voltage'},
        'inputCurrent': {'name': 'inputCurrent', 'number': 3012, 'propertyFormat': 'float', 'default': 0.0,
                         'studerName': 'Input current'},
        'busVoltage': {'name': 'busVoltage', 'number': 3021, 'propertyFormat': 'float', 'default': 0.0,
                       'studerName': 'Output voltage'},
        'outputVoltage': {'name': 'outputVoltage', 'number': 3021, 'propertyFormat': 'float', 'default': 0.0,
                          'studerName': 'Output voltage'},
        'outputCurrent': {'name': 'outputCurrent', 'number': 3022, 'propertyFormat': 'float', 'default': 0.0,
                          'studerName': 'Output current'},
        'operatingMode': {'name': 'operatingMode', 'number': 3028, 'propertyFormat': 'enum', 'default': 0,
                          'studerName': 'Operating state'},
        'inputFrequency': {'name': 'inputFrequency', 'number': 3084, 'propertyFormat': 'float', 'default': 0.0,
                           'studerName': 'Input frequency'},

        'inverterEnabled': {'name': 'inverterEnabled', 'number': 3049, 'propertyFormat': 'enum',
                            'default': 0, 'studerName': 'State of the inverter'},
        'lockingsFlag': {'name': 'lockingsFlag', 'number': 3056, 'propertyFormat': 'float', 'default': 0.0,
                         'studerName': 'LockingsFlag'},

        'softVersionMsb': {'name': 'softVersionMsb', 'number': 3130, 'propertyFormat': 'float', 'default': 0.0,
                           'studerName': 'ID SOFT msb'},
        'softVersionLsb': {'name': 'softVersionLsb', 'number': 3131, 'propertyFormat': 'float', 'default': 0.0,
                           'studerName': 'ID SOFT lsb'},

        'acInjectionCurrentLimitation': {'name': 'acInjectionCurrentLimitation', 'number': 3158,
                                         'propertyFormat': 'float', 'default': 0.0,
                                         'studerName': 'AC injection current limited (ARN4105)'},
        'acInjectionCurrentLimitationReason': {'name': 'acInjectionCurrentLimitationReason', 'number': 3159,
                                               'propertyFormat': 'enum', 'default': 0,
                                               'studerName': 'AC injection current, type of limitation (ARN4105)'},
        'sourceOfLimitation': {'name': 'sourceOfLimitation', 'number': 3160, 'propertyFormat': 'enum',
                               'default': 0, 'studerName': 'Source of limitation in charger and injector mode'},
        'batteryPriorityActive': {'name': 'batteryPriorityActive', 'number': 3161, 'propertyFormat': 'enum',
                                  'default': 0, 'studerName': 'Battery priority active'},
        'forcedGridFeedingActive': {'name': 'forcedGridFeedingActive', 'number': 3162, 'propertyFormat': 'enum',
                                    'default': 0, 'studerName': 'Forced grid feeding active'},
        }

    opModeToStringTable = {0: u'Invalid',
                           1: u'Inverter',
                           2: u'Charger',
                           3: u'Boost',
                           4: u'Injection'}

    stringToOpModeTable = {u'Invalid': 0,
                           u'Inverter': 1,
                           u'Charger': 2,
                           u'Boost': 3,
                           u'Injection': 4}

    batteryCyclePhaseToStringTable = {0: u'Invalid',
                                      1: u'Bulk',
                                      2: u'Absorption',
                                      3: u'Equalise',
                                      4: u'Floating',
                                      5: u'R.float.',
                                      6: u'Per.abs.',
                                      7: u'Mixing',
                                      8: u'Forming'}

    stringToBatteryCyclePhaseTable = {u'Invalid': 0,
                                      u'Bulk': 1,
                                      u'Absorption': 2,
                                      u'Equalise': 3,
                                      u'Floating': 4,
                                      u'R.float.': 5,
                                      u'Per.abs.': 6,
                                      u'Mixing': 7,
                                      u'Forming': 8}

    def __init__(self, device_address, **kwargs):
        """
        :param device_address The device number on the SCOM interface. Own address of the device.
        :type device_address int
        """
        super(Xtender, self).__init__(device_address, **kwargs)      # Call base class constructor
        self._add_instance(self.SD_XTENDER)                          # Add this instance to the instance counter

        # Give paramInfoTable to ScomDevice base class
        super(Xtender, self)._set_param_info_table(self.paramInfoTable)

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
        return self.SD_XTENDER

    @property
    def software_version(self):
        """Implementation of ScomDevice interface.
        """
        return self.get_software_version()

    def set_power_enable(self, enable):
        """Enables/disables the device
        """
        try:
            if enable:
                self._write_parameter_info('powerOnAllXtenders', True, property_id=PROPERTY_VALUE_QSP)
            else:
                self._write_parameter_info('powerOffAllXtenders', True, property_id=PROPERTY_VALUE_QSP)
        except:
            return False
        return True

    def get_battery_voltage(self):
        """Reads and returns the actual battery voltage."""
        return self._read_user_info_ex(self.userInfoTable['batteryVoltage'])

    def get_battery_current(self):
        """Reads and returns the actual battery current."""
        return self._read_user_info_ex(self.userInfoTable['batteryCurrent'])

    def get_battery_charge_reference_current(self, property_id=PROPERTY_LAST):
        return self._read_parameter_info(param_info_name='batteryChargeReferenceCurrent',
                                         property_id=property_id)

    def set_battery_charge_reference_current(self, value, property_id=PROPERTY_LAST):
        """
        Battery charge current value needs to be 0 or higher. Negative values are not allowed.

        To discharge battery the 'grid-feed' feature needs to be used.
        """
        return self._write_parameter_info('batteryChargeReferenceCurrent', value,
                                          property_id=PROPERTY_UNSAVED_VALUE_QSP)

    def get_battery_minimum_voltage_without_load(self):
        return self._read_parameter_info('batteryMinimumVoltageWithoutLoad')

    def get_battery_minimum_voltage_with_load(self):
        return self._read_parameter_info('batteryMinimumVoltageWithLoad')

    def set_battery_minimum_voltage(self, value):
        return self._write_parameter_info('batteryMinimumVoltageWithLoad', value,
                                          property_id=PROPERTY_UNSAVED_VALUE_QSP)

    def get_battery_maximum_voltage(self, property_id=PROPERTY_LAST):
        return self._read_parameter_info(param_info_name='batteryMaximumVoltage', property_id=property_id)

    def set_battery_maximum_voltage(self, value):
        return self._write_parameter_info('batteryMaximumVoltage', value, property_id=PROPERTY_UNSAVED_VALUE_QSP)

    def get_software_version(self):
        id_soft_msb = self._read_user_info_ex(self.userInfoTable['softVersionMsb'])
        id_soft_lsb = self._read_user_info_ex(self.userInfoTable['softVersionLsb'])

        if id_soft_msb and id_soft_lsb:
            id_soft_major_version = int(id_soft_msb) >> 8
            id_soft_minor_version = int(id_soft_lsb) >> 8
            id_soft_revision = int(id_soft_lsb) & 0xFF

            return {'major': id_soft_major_version, 'minor': id_soft_minor_version, 'patch': id_soft_revision}
        return {'major': 0, 'minor': 0, 'patch': 0}

    def get_input_voltage(self):
        return self._read_user_info_ex(self.userInfoTable['inputVoltage'])

    def get_input_current(self):
        return self._read_user_info_ex(self.userInfoTable['inputCurrent'])

    def get_output_voltage(self):
        return self._read_user_info_ex(self.userInfoTable['outputVoltage'])

    def get_output_current(self):
        return self._read_user_info_ex(self.userInfoTable['outputCurrent'])

    def get_operating_mode(self):
        """Reads and returns the actual operating mode."""
        return self._read_user_info_ex(self.userInfoTable['operatingMode'])

    def get_input_frequency(self):
        return self._read_user_info_ex(self.userInfoTable['inputFrequency'])

    def get_standby_power_level(self):
        return self._read_parameter_info('standbyPowerLevel', property_id=PROPERTY_VALUE_QSP)

    def set_standby_power_level(self, value):
        return self._write_parameter_info('standbyPowerLevel', value, property_id=PROPERTY_VALUE_QSP)

    def set_restore_default_settings(self, value):
        value = True    # Parameter is of type signal. Fore value to true
        return self._write_parameter_info('restoreDefaultSettings', value, property_id=PROPERTY_VALUE_QSP)

    def set_restore_factory_settings(self, value):
        value = True  # Parameter is of type signal. Fore value to true
        return self._write_parameter_info('restoreFactorySettings', value, property_id=PROPERTY_VALUE_QSP)

    def set_reset_all_inverters(self, value):
        value = True  # Parameter is of type signal. Fore value to true
        return self._write_parameter_info('resetAllInverters', value, property_id=PROPERTY_VALUE_QSP)

    def get_floating_voltage(self):
        return self._read_parameter_info('floatingVoltage', property_id=PROPERTY_VALUE_QSP)

    def set_floating_voltage(self, value):
        return self._write_parameter_info('floatingVoltage', value, property_id=PROPERTY_VALUE_QSP)

    def set_force_floating_phase(self, value=True):
        value = True  # Parameter is of type signal. Fore value to true
        return self._write_parameter_info('forceFloatingPhase', value, property_id=PROPERTY_VALUE_QSP)

    def set_force_new_charge_cycle(self, value=True):
        value = True  # Parameter is of type signal. Fore value to true
        return self._write_parameter_info('forceNewChargeCycle', value, property_id=PROPERTY_UNSAVED_VALUE_QSP)

    def get_maximum_ac_input_current(self):
        return self._read_parameter_info('maximumAcInputCurrent')

    def set_maximum_ac_input_current(self, value):
        """
        Minimum value allowed by the Xtender is 2 [A].
        """
        return self._write_parameter_info('maximumAcInputCurrent', value, property_id=PROPERTY_UNSAVED_VALUE_QSP)

    def get_auto_ac_input_current_reduction(self):
        return self._read_parameter_info('autoAcInputCurrentReduction')

    def get_boost_phase_allowed(self):
        return self._read_parameter_info('boostPhaseAllowed')

    def get_boost_voltage(self):
        return self._read_parameter_info('boostVoltage')

    def set_boost_voltage(self, value):
        return self._write_parameter_info('boostVoltage', value, property_id=PROPERTY_UNSAVED_VALUE_QSP)

    def get_input_current_adaption_range(self):
        return self._read_parameter_info('inputCurrentAdaptionRange', property_id=PROPERTY_UNSAVED_VALUE_QSP)

    def set_input_current_adaption_range(self, value):
        return self._write_parameter_info('inputCurrentAdaptionRange', value, property_id=PROPERTY_UNSAVED_VALUE_QSP)

    def get_grid_feeding_allowed(self):
        return self._read_parameter_info('gridFeedingAllowed', property_id=PROPERTY_UNSAVED_VALUE_QSP)

    def set_allow_grid_feeding(self, value):
        return self._write_parameter_info('gridFeedingAllowed', value, property_id=PROPERTY_UNSAVED_VALUE_QSP)

    def get_grid_feeding_maximum_current(self):
        return self._read_parameter_info('gridFeedingMaximumCurrent', property_id=PROPERTY_UNSAVED_VALUE_QSP)

    def set_grid_feeding_maximum_current(self, value):
        return self._write_parameter_info('gridFeedingMaximumCurrent', value, property_id=PROPERTY_UNSAVED_VALUE_QSP)

    def get_grid_feeding_battery_voltage(self):
        return self._read_parameter_info('gridFeedingBatteryVoltage', property_id=PROPERTY_VALUE_QSP)

    def set_grid_feeding_battery_voltage(self, value):
        return self._write_parameter_info('gridFeedingBatteryVoltage', value, property_id=PROPERTY_VALUE_QSP)

    def get_grid_feeding_start_time(self):
        return self._read_parameter_info('gridFeedingStartTime')

    def set_grid_feeding_start_time(self, value):
        return self._write_parameter_info('gridFeedingStartTime', value)

    def get_grid_feeding_stop_time(self):
        return self._read_parameter_info('gridFeedingStopTime')

    def set_grid_feeding_stop_time(self, value):
        return self._write_parameter_info('gridFeedingStopTime', value)

    def get_frequency_control_enabled(self):
        return self._read_parameter_info('frequencyControlEnabled')

    def get_allow_inverter(self):
        return self._read_parameter_info('allowInverter', property_id=PROPERTY_UNSAVED_VALUE_QSP)

    def set_allow_inverter(self, value):
        return self._write_parameter_info('allowInverter', value, property_id=PROPERTY_UNSAVED_VALUE_QSP)

    def get_allow_charger(self):
        return self._read_parameter_info('allowCharger', property_id=PROPERTY_UNSAVED_VALUE_QSP)

    def set_allow_charger(self, value):
        return self._write_parameter_info('allowCharger', value, property_id=PROPERTY_UNSAVED_VALUE_QSP)

    def get_battery_priority_as_energy_source(self):
        return self._read_parameter_info('batteryPriorityAsEnergySource', property_id=PROPERTY_UNSAVED_VALUE_QSP)

    def set_battery_priority_as_energy_source(self, value):
        return self._write_parameter_info('batteryPriorityAsEnergySource', value,
                                          property_id=PROPERTY_UNSAVED_VALUE_QSP)

    def get_battery_priority_voltage(self):
        return self._read_parameter_info('batteryPriorityVoltage', property_id=PROPERTY_UNSAVED_VALUE_QSP)

    def set_battery_priority_voltage(self, value):
        return self._write_parameter_info('batteryPriorityVoltage', value, property_id=PROPERTY_UNSAVED_VALUE_QSP)

    def get_soc(self):
        return self._read_user_info_ex(self.userInfoTable['soc'])

    def get_battery_cycle_phase(self):
        return self._read_user_info_ex(self.userInfoTable['batteryCyclePhase'])

    def get_inverter_enabled(self):
        return self._read_user_info_ex(self.userInfoTable['inverterEnabled'])

    def get_lockings_flag(self):
        return self._read_user_info_ex(self.userInfoTable['lockingsFlag'])

    def get_ac_injection_current_limitation(self):
        return self._read_user_info_ex(self.userInfoTable['acInjectionCurrentLimitation'])

    def get_ac_injection_current_limitation_reason(self):
        return self._read_user_info_ex(self.userInfoTable['acInjectionCurrentLimitationReason'])

    def get_source_of_limitation(self):
        return self._read_user_info_ex(self.userInfoTable['sourceOfLimitation'])

    def get_battery_priority_active(self):
        return self._read_user_info_ex(self.userInfoTable['batteryPriorityActive'])

    def get_forced_grid_feeding_active(self):
        return self._read_user_info_ex(self.userInfoTable['forcedGridFeedingActive'])
