# -*- coding: utf-8 -*-
#

import logging
from abc import ABCMeta, abstractproperty, abstractmethod
from weakref import WeakValueDictionary
import struct

from ..property import Property
from ..frame import Frame as ScomFrame
from ..defines import *
from .common.paramproxycontainer import ParamProxyContainer
from ..exception import ReadException, WriteException


# Links:
# - Object counter: http://python-3-patterns-idioms-test.readthedocs.io/en/latest/InitializationAndCleanup.html
#
class ScomDevice(object):
    """Base class for all SCOM devices.
    """

    __metaclass__ = ABCMeta

    # SCOM device types:
    SD_UNKNOWN = 0
    SD_XTENDER = 1          # Inverter / Charger
    SD_COMPACT = 2          # Inverter / Charger
    SD_VARIO_TRACK = 3      # MPPT Solar charge controller
    SD_VARIO_STRING = 4     # MPPT Solar charge controller
    SD_VARIO_POWER = 5      # Battery Charge Controller
    SD_RCC = 6              # Remote Control Unit
    SD_BSP = 7              # Battery Status Processor
    SD_MAX = 8

    __instanceCounter = {SD_XTENDER: WeakValueDictionary(),
                         SD_COMPACT: WeakValueDictionary(),
                         SD_VARIO_TRACK: WeakValueDictionary(),
                         SD_VARIO_STRING: WeakValueDictionary(),
                         SD_VARIO_POWER: WeakValueDictionary(),
                         SD_RCC: WeakValueDictionary(),
                         SD_BSP: WeakValueDictionary()}

    device_categories = {'xtender': SD_XTENDER,
                         'compact': SD_COMPACT,
                         'vario-track': SD_VARIO_TRACK,
                         'vario-string': SD_VARIO_STRING,
                         'vario-power': SD_VARIO_POWER,
                         'rcc': SD_RCC,
                         'bsp': SD_BSP
                         }

    log = logging.getLogger(__name__)

    def __init__(self, device_address):
        super(ScomDevice, self).__init__()
        self._deviceAddress = device_address

    def _add_instance(self, device_type):
        """Adds the instance to the instance counter.

        The instance to add is not given via parameter list, because the instance to
        add is always 'self'.

        This method needs to be called by the deriving classes.

        :param device_type The device type to which to add the the instance (itself).
        :type device_type enumerate
        """
        self.__instanceCounter[device_type][id(self)] = self
        self._param_info_table = {}
        self._paramMirror = None

    def _set_param_info_table(self, param_info_table):
        self._param_info_table = param_info_table

        self._paramMirror = ParamProxyContainer(self._param_info_table,
                                                self._read_attribute)   # ParamMirror to handle UNSAVED_VALUE_QSP values

    @classmethod
    def get_device_type_by_device_category(cls, device_category: str):
        """Convert from device category to device type.

        Example:
            'xtender' -> SD_XTENDER

        :return The device type
        """
        device_category = device_category.lower()

        if device_category in 'xtender':
            return cls.SD_XTENDER
        elif device_category in 'compact':
            return cls.SD_COMPACT
        elif device_category in ('vario-track', 'vario_track'):
            return cls.SD_VARIO_TRACK
        elif device_category in ('vario-string', 'vario_string'):
            return cls.SD_VARIO_STRING
        elif device_category in ('vario-power', 'vario_power'):
            return cls.SD_VARIO_POWER
        elif device_category in 'rcc':
            return cls.SD_RCC
        elif device_category in 'bsp':
            return cls.SD_BSP
        else:
            assert False, 'Device category not found!'

    @classmethod
    def get_number_of_instances(cls, device_category):
        """Returns the actual number of instances of a device category.
        """
        return len(cls.__instanceCounter[cls.get_device_type_by_device_category(device_category)])

    @classmethod
    def get_instances_of_category(cls, device_category: str):
        """Returns a list of weak pointers to instances of a category.
        """
        return cls.__instanceCounter[cls.get_device_type_by_device_category(device_category)]

    @classmethod
    def _get_scom(cls):
        """Returns the SCOM interface on which the device can be reached.

        There may be more then on SCOM interface connected to the system.
        This method is used by the base class (ScomDevice) to receive the right
        SCOM interface.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def device_type(self):
        """Returns the device type.

        See 'SD_XTENDER' and following constants.

        :return The device type.
        :rtype enumerate
        """
        raise NotImplementedError

    @property
    def device_address(self):
        """Returns the device address.

        :return The device address
        :rtype int
        """
        return self._deviceAddress

    @property
    @abstractmethod
    def software_version(self):
        """Returns the software version.

        :return The Software version as dict {major, minor, patch}
        :rtype dict
        """
        raise NotImplementedError

    @classmethod
    def _property_format_to_value_size(cls, property_format):
        """Returns the size in byte of the expected value according to the property format.

        :param property_format The property format ('float', 'int32', 'enum', 'byte', 'bool')
        :type property_format str
        :return The size of the expected value
        :type return int
        """
        if property_format in ('float', 'int32', 'signal'):
            value_size = 4
        elif property_format in ('enum', 'short-enum'):
            value_size = 2
        elif property_format in ('byte', 'bool'):
            value_size = 1
        else:
            assert False

        return value_size

    def _write_parameter(self, parameter_id, value, property_format='float', property_id=PROPERTY_VALUE_QSP):
        """Writes a new value to the given parameter id.

        Ex.:
         - self._writeParameter(14081, 1, propertyFormat='int32')
         - self._writeParameter(1138, current, propertyFormat='float')
         - self._writeParameter(paramInfo['number'], newValue, propertyFormat=paramInfo['propertyFormat'],
                                propertyId=propertyId)
        """
        request_frame = ScomFrame()
        request_frame.initialize(src_addr=1, dest_addr=self.device_address)

        value_size = self._property_format_to_value_size(property_format)

        prop = Property(request_frame)
        prop.set_object_write(OBJECT_TYPE_PARAMETER, parameter_id,
                              property_id, value, value_size,
                              property_format=property_format)

        if request_frame.is_valid():
            response_frame = self._get_scom().write_frame(request_frame)  # Method call is blocking

            if response_frame is not None and response_frame.is_valid():
                value_size = response_frame.response_value_size()
                value = response_frame[24:24 + value_size]
            else:
                msg = 'Response frame not valid!'
                self.log.warning(msg)
                raise WriteException(msg)
        else:
            msg = 'Request frame not valid!'
            self.log.warning(msg)
            raise WriteException(msg)

        return value

    def _write_parameter_info(self, param_info_name, value, property_id=PROPERTY_UNSAVED_VALUE_QSP):
        """Writes a new value to the device parameter using the given 'parameter info name'
        """
        assert property_id in (PROPERTY_UNSAVED_VALUE_QSP, PROPERTY_VALUE_QSP)

        # Get the parameter info needed from the table
        param_info = self._param_info_table[param_info_name]
        assert param_info is not None, 'Parameter info name not found!'

        try:
            # Write parameter using the parameter info
            self._write_parameter(param_info['number'],
                                  value,
                                  property_format=param_info['propertyFormat'],
                                  property_id=property_id)
        except Exception as e:
            self.log.warning('Parameter \'%s\' not set!' % param_info_name)
            return False

        # Save written value to mirror
        if property_id == PROPERTY_UNSAVED_VALUE_QSP:
            self._paramMirror.save(param_info, value)

        return True

    def _read_parameter_info(self, param_info_name, property_id=PROPERTY_LAST):
        """ Reads and returns the device parameter identified using the 'parameter info name'
        """
        param_info = self._param_info_table[param_info_name]
        returned_value = param_info.get('default', 0.0)
        success = False
        value = None

        if property_id == PROPERTY_LAST:
            (success, value) = self._paramMirror.read(param_info, property_id=property_id)
        elif property_id == PROPERTY_UNSAVED_VALUE_QSP:
            (success, value) = self._paramMirror.read(param_info, property_id=property_id)

        if property_id == PROPERTY_VALUE_QSP or not success:
            value = self._read_attribute(param_info, property_id=property_id)
            success = True

        if success and value is not None:
            returned_value = value
        else:
            msg = 'Could not read parameter \'%s\'' % param_info['name']
            self.log.warning(msg)
            raise ReadException(msg)

        return returned_value

    def _read_parameter(self, parameter_id, property_id=PROPERTY_VALUE_QSP):
        """Reads a parameter on the device.
        Return:
            value : bytearray
                Parameter read.
        """
        value = bytearray()
        request_frame = ScomFrame()

        request_frame.initialize(src_addr=1, dest_addr=self.device_address, data_length=99)

        prop = Property(request_frame)
        prop.set_object_read(OBJECT_TYPE_PARAMETER, parameter_id, property_id)

        if request_frame.is_valid():
            response_frame = self._get_scom().write_frame(request_frame)  # Method call is blocking

            if response_frame:
                if response_frame.is_valid():
                    value_size = response_frame.response_value_size()
                    value = response_frame[24:24 + value_size]
                elif response_frame.is_data_error_flag_set():
                    msg = 'Error flag set in response frame!'
                    self.log.warning(msg)
                    raise ReadException(msg)
            else:
                msg = 'No response frame received!'
                self.log.warning(msg)
                raise ReadException(msg)
        else:
            msg = 'Request frame not valid'
            self.log.warning(msg)
            ReadException(msg)

        return value

    def _read_attribute(self, param_info, property_id=PROPERTY_UNSAVED_VALUE_QSP):
        value = param_info['default']
        byte_array = self._read_parameter(param_info['number'], property_id=property_id)

        if byte_array:
            if param_info['propertyFormat'] == 'float':
                assert len(byte_array) == 4
                value = struct.unpack('f', byte_array[0:4])[0]
            elif param_info['propertyFormat'] == 'int32':
                assert len(byte_array) == 4
                value = struct.unpack('I', byte_array[0:4])[0]
            elif param_info['propertyFormat'] == 'enum':
                assert len(byte_array) == 4
                value = struct.unpack('H', byte_array[0:2])[0]
            elif param_info['propertyFormat'] == 'byte':
                assert len(byte_array) == 1
                value = struct.unpack('B', byte_array[0:1])[0]
            elif param_info['propertyFormat'] == 'bool':
                assert len(byte_array) == 1
                value = struct.unpack('B', byte_array[0:1])[0]
            else:
                assert False

        return value

    def _read_user_info_by_parameter_id(self, parameter_id):
        """Reads a user info on the device.

        :param parameter_id
        :type parameter_id int
        :return The parameter read
        :type return bytearray
        """
        value = bytearray()
        request_frame = ScomFrame()

        request_frame.initialize(src_addr=1, dest_addr=self.device_address, data_length=99)

        prop = Property(request_frame)
        prop.set_object_read(OBJECT_TYPE_READ_USER_INFO, parameter_id, PROPERTY_ID_READ)

        if request_frame.is_valid():
            response_frame = self._get_scom().write_frame(request_frame)  # Method call is blocking

            if response_frame:
                if response_frame.is_valid():
                    value_size = response_frame.response_value_size()
                    value = response_frame[24:24 + value_size]
                elif response_frame.is_data_error_flag_set():
                    msg = 'Error flag set in response frame!'
                    self.log.warning(msg)
                    raise ReadException(msg)
            else:
                msg = 'No response frame received!'
                self.log.warning(msg)
                raise ReadException(msg)
        else:
            msg = 'Request frame not valid'
            self.log.warning(msg)
            ReadException(msg)

        return value

    def _read_user_info_ex(self, user_info):
        """Uses the userInfoTable to access the needed user info.

        :return The value received from the device
        :type return float, int, enum, etc.
        """
        default_value = user_info['default']
        value = self._read_user_info_by_parameter_id(user_info['number'])

        if value:
            if user_info['propertyFormat'] == 'float':
                assert len(value) == 4
                value = struct.unpack('f', value[0:4])[0]
            elif user_info['propertyFormat'] == 'enum':
                assert len(value) == 2
                value = struct.unpack('H', value[0:2])[0]  # Read 'ENUM' format as unsigned int (H)
            elif user_info['propertyFormat'] == 'short enum':
                length = len(value)
                assert len(value) == 4, 'Expected 4 got %d' % len(value)
                if length == 1:
                    value = struct.unpack('B', value[0:4])[0]
                elif length == 4:
                    value = struct.unpack('L', value[0:4])[0]
            else:
                assert False    # Support for given type not supported yet!

            return value
        else:
            msg = 'Could not read user info \'%s\'' % user_info['name']
            self.log.warning(msg)
            raise ReadException(msg)
            return default_value
