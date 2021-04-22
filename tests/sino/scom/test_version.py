#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging
import unittest

from tests.sino.scom.paths import update_working_directory

update_working_directory()  # Needed when: 'pipenv run python -m unittest tests/sino/scom/{this_file}.py'


class TestSinoScomVersion(unittest.TestCase):
    """Tests package version.
    """

    log = logging.getLogger(__name__)
    versions = []

    def test_version_01(self):
        from sino import scom

        print(scom.version)
        self.versions.append(scom.version)

        self.assertTrue(isinstance(scom.version, str))
        self.assertIsNot(scom.version, '')
        self.assertTrue(len(scom.version.split('.')) == 3)  # Want to see 'x.y.z'

    def test_version_02(self):
        from sino.scom import version

        print(version)
        self.versions.append(version)

        self.assertTrue(isinstance(version, str))
        self.assertIsNot(version, '')
        self.assertTrue(len(version.split('.')) == 3)  # Want to see 'x.y.z'

    def test_version_03(self):
        import types
        import sino.scom.version as version

        # Why is 'version' in some circumstances the module and otherwise the version string!?
        if isinstance(version, types.ModuleType):
            version = version.__version__

        self.versions.append(version)

        self.assertTrue(isinstance(version, str))
        self.assertIsNot(version, '')
        self.assertTrue(len(version.split('.')) == 3)  # Want to see 'x.y.z'

    def test_versions_equal(self):
        # Should have 3 times a version
        self.assertEqual(len(self.versions), 3)
        # Should be every time the same value
        self.assertTrue(all(map(lambda v: v == self.versions[0], self.versions[1:])))


class TestSinoScomGlueVersionMain(unittest.TestCase):
    """Test call version.py.

    - https://medium.com/opsops/how-to-test-if-name-main-1928367290cb
    - https://stackoverflow.com/questions/5850268/how-to-test-or-mock-if-name-main-contents
    """

    log = logging.getLogger(__name__)

    def setUp(self):
        self.version = __import__('sino.scom.version', globals(), locals(), [''], 0)

    def tearDown(self):
        import sys
        del sys.modules[self.version.__name__]

    def test_version_04(self):
        self.log.info('Calling version.py\'s main():')
        self.version.main()


if __name__ == '__main__':
    # Enable logging
    logging.basicConfig(format='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)

    unittest.main()
