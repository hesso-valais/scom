# -*- coding: utf-8 -*-
#

import logging
from sino.scom import defines as define

logging.getLogger(__name__).setLevel(logging.INFO)  # DEBUG, INFO, WARNING, ERROR, CRITICAL


class ParamProxyContainer(object):
    """Parameter proxy holding Studer device parameters.

    Some parameters written to the Studer devices (with property id PROPERTY_UNSAVED_VALUE_QSP)
    cannot be read back from the device. The ParamProxyContainer takes the role of returning
    the previous written value.

    For the moment only PROPERTY_UNSAVED_VALUE_QSP and PROPERTY_LAST values can be stored and
    returned. The idea is, that finally also parameters/user_infos with PROPERTY_VALUE_QSP
    can be accessed, by directly using the instance representing the Studer device.
    """

    log = logging.getLogger(__name__)

    def __init__(self, param_info_table, read_parameter_method):
        super(ParamProxyContainer, self).__init__()
        # Parameter description table
        self.paramInfoTable = param_info_table      # type: dict
        # Container holding parameters
        self.params = {}                            # type: {str, _Param}
        self._readParameterMethod = read_parameter_method

    def read(self, param_info, property_id=define.PROPERTY_LAST):
        """Reads the value of a parameter."""
        success = False

        # For the moment allowing only to read parameters with property UNSAVED_VALUE or LAST
        if property_id in (define.PROPERTY_UNSAVED_VALUE_QSP, define.PROPERTY_LAST):
            # Check if parameters was already saved once
            if self.param_info_in_params(param_info):
                # OK get it and return it
                param = self.get_param(param_info)
                return True, param.value
            else:
                # Get the value using PROPERTY_VALUE_QSP
                value = self._readParameterMethod(param_info, propertyId=define.PROPERTY_VALUE_QSP)
                # but do not save it
                # self.save(paramInfo, value, propertyId=studer.PROPERTY_VALUE_QSP)
                return True, value

        if not success:
            self.log.warning(u'Parameter %s not found in mirror!' % param_info['name'])
            return False, 0

    def save(self, param_info, new_value):
        if self.param_info_in_params(param_info):
            param = self.get_param(param_info)  # Get param from dictionary
        else:
            param = _Param(param_info['name'])
            self.params[param_info['name']] = param  # Add it to the list

        param.value = new_value

    def param_info_in_params(self, param_info):
        """Checks if param related to the paramInfo is present.
        """
        return True if param_info and param_info['name'] in self.params else False

    def get_param(self, param_info):
        """Returns parameter from internal dictionary.
        """
        assert param_info and self.param_info_in_params(param_info)
        return self.params[param_info['name']]


class _Param(object):
    """Holds the name and the actual value of a parameter/user_info of a Studer device
    """
    def __init__(self, name):
        self.name = name        # Internal name of the parameter
        # The actual value of the parameter
        self._value = 0         # type: any

    @property
    def value(self): return self._value

    @value.setter
    def value(self, new_value): self._value = new_value
