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
                    [Extension("baseframe",
                               ["src/sino/scom/baseframe.pyx", "src/sino/scom/scomlib/scom_data_link.c"],
                               language="c++",),
                     Extension("property",
                               ["src/sino/scom/property.pyx", "src/sino/scom/scomlib/scom_property.c"],
                               language="c++",)]
                        ),
    include_dirs=['sino/scom', ],
    cmdclass={'build_ext': build_ext}
)
