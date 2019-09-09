#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
from Cython.Build import cythonize

#
# To build C libraries manually after package installation go
# into the Python's site-packages directory and call:
# python ./sino/scom/setup.py build_ext --inplace
#
# Move then the 'property' and 'baseframe' library into the sino/scom
# folder (example):
# mv property.*.so sino/scom/
# mv baseframe.*.so sino/scom/
#
setup(
    name="scomlib",
    ext_modules=cythonize(
                    [Extension("baseframe",
                               ["sino/scom/baseframe.pyx", "sino/scom/scomlib/scom_data_link.c"],
                               language="c++",),
                     Extension("property",
                               ["sino/scom/property.pyx", "sino/scom/scomlib/scom_property.c"],
                               language="c++",)]
                        ),
    include_dirs=['sino/scom', ],
    cmdclass={'build_ext': build_ext}
)
