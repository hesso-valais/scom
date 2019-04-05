#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from distutils.extension import Extension
from Cython.Distutils import build_ext
import os
import sys

sys.path.append(os.path.abspath('./src'))
from sino.scom.version import __version__


setup(
    name="sino.scom",
    version=__version__,
    description='Studer devices control library',
    url='https://www.studer-innotec.com',

    packages=find_packages('src'),
    package_dir={'': 'src'},

    ext_modules=[Extension("sino.scom.baseframe", ["src/sino/scom/baseframe.pyx",
                                                   "src/sino/scom/scomlib/scom_data_link.c"],
                           include_dirs=['src/sino/scom'],),
                 Extension("sino.scom.property", ["src/sino/scom/property.pyx",
                                                  "src/sino/scom/scomlib/scom_property.c"],
                           include_dirs=['src/sino/scom'],)],

    include_dirs=['src/sino/scom', ],

    cmdclass={'build_ext': build_ext},

    package_data={},

    data_files=[
        # First parameter is where it should be installed (relative paths or abs paths possible)
        # Second parameter is which files (from inside the project) should be taken into the dist package.
        ('sino.scom',
         ['src/sino/scom/scomlib/scom_data_link.h',
          'src/sino/scom/scomlib/scom_port_c99.h',
          'src/sino/scom/scomlib/scom_property.h']),
    ],

    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',

        'Operating System :: OS Independent',
    ],

    maintainer='HES-SO Valais, School of Engineering, Sion',
    maintainer_email='thomas.sterren@hevs.ch',
)
