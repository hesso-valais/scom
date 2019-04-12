#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
from Cython.Build import cythonize

#
# Call in shell: python setup.py build_ext --inplace
#
setup(
    name="scomlib",
    ext_modules=cythonize(
                    [Extension("sino.scom.baseframe", ["sino/scom/baseframe.pyx", "sino/scom/scomlib/scom_data_link.c"]),
                     Extension("sino.scom.property", ["sino/scom/property.pyx", "sino/scom/scomlib/scom_property.c"])]
                        ),
    include_dirs=['sino/scom', ],
    cmdclass={'build_ext': build_ext}
)
