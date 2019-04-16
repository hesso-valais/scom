# -*- coding: utf-8 -*-

# Tell python that there are more sub-packages present, physically located elsewhere.
# See: https://stackoverflow.com/questions/8936884/python-import-path-packages-with-the-same-name-in-different-folders
import pkgutil
__path__ = pkgutil.extend_path(__path__, __name__)

# Bring version info into local namespace
from . import version
# Allow to use `print(sino.scom.version)` to get version information
version = version.__version__

from .defines import *       # To get defines like OBJECT_TYPE_READ_USER_INFO and PROPERTY_ID_READ into the scom namespace
from . import frame
from .scom import Scom
from . import dman
from . import device
from .device.scomdevice import ScomDevice as Device
from .device.devicefactory import DeviceFactory
