# Changelog

## 0.7.4 - (2023-03-13)
- Added `ReadException` and `WriteException`
- Added `reset()` method to `Scom` class
- Bugfixes in `dman.DeviceManager` class

## 0.7.3 - (2021-04-28)
- Added tests for `dman.DeviceManager` class
- Bugfixes in `dman.DeviceManager` class

## 0.7.2 - (2021-04-22)
- Added tests
- Updated C library code to support newer MSVC compilers under Windows
- Removed Python 2.x support
- Adjusted logging configuration according to a library

## 0.7.1 - (2019-09-12)
- Added timeout to mutex. SCOM library will no more accidentally block
- Removed assert's and replaced them with Exceptions

## 0.7.0 - (2019-08-28)
- Extended functionality of VarioPower device (Thanks to Lino)
- Fixed issue #1

## 0.6.0 - (2019-05-24)
- Added VarioPower device

## 0.5.3 - (2019-04-18)
- Fixed project description display problem

## 0.5.2 - (2019-04-18)
- Added project description
- Installing package even if Cython is not installed (needs manual post-install step)

## 0.5.1 - (2019-04-17)
- Added 'Xtender read version' example
- Bugfix: Package installation now also works in a non-virtual environment

## 0.5.0 - (2019-04-16)
- First release
- Added DeviceManager
- Added DeviceFactory
- Added basic support for Xtender devices
