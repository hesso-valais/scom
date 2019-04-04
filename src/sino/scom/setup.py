#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

#
# Call in shell: python setup.py build_ext --inplace
#
setup(
    name="scomlib",
    ext_modules=[Extension("build.scom_baseframe_ext", ["src/sino/scom/baseframe.pyx", "src/sino/scom/scomlib/scom_data_link.c"]),
                 Extension("build.scom_property_ext", ["src/sino/scom/property.pyx", "src/sino/scom/scomlib/scom_property.c"])],
    include_dirs=['src/sino/scom', ],
    cmdclass={'build_ext': build_ext}
)
