#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools import Extension
from Cython.Distutils import build_ext
from Cython.Build import cythonize

#
# Call in shell: python setup.py build_ext --inplace
#
setup(
    name="scomlib",
    ext_modules=cythonize(
                    [Extension("sino.scom.baseframelib", ["sino/scom/baseframe.pyx",
                                                          "sino/scom/scomlib/scom_data_link.c"],
                               include_dirs=['sino/scom', ],
                               language="c++",
                               libraries=['stdc++']),
                     Extension("sino.scom.propertylib", ["sino/scom/property.pyx",
                                                         "sino/scom/scomlib/scom_property.c"],
                               include_dirs=['sino/scom'],
                               language="c++",)],
                    include_path=['sino/scom'],     # Include paths to let cython find .pxd files
                        ),
    include_dirs=['sino/scom', ],
#    cmdclass={'build_ext': build_ext},
)
