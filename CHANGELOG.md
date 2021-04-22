# Changelog

## 0.7.2 - (2021-04-22)
- Added tests
- Updated C library code to support newer MSVC compilers under Windows
- Removed Python 2.x support

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
