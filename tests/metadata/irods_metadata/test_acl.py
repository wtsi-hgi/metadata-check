"""
Copyright (C) 2015  Genome Research Ltd.

Author: Irina Colgiu <ic4@sanger.ac.uk>

This program is part of meta-check

meta-check is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.
You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

This file has been created on Nov 30, 2015.
"""


import unittest
from metadata.irods_metadata.acl import IrodsACL
from irods.constants import IrodsPermission

class TestIrodsACL(unittest.TestCase):

    def test_provides_public_access_1(self):
        acl = IrodsACL(access_group='hgi', zone='seq', permission='read')
        self.assertFalse(acl.provides_public_access())

    def test_provides_public_access_2(self):
        acl = IrodsACL(access_group='public', zone='humgen', permission='read')
        self.assertTrue(acl.provides_public_access())



    def test_provides_access_for_ss_group_1(self):
        acl = IrodsACL(access_group='hgi', zone='seq', permission='own')
        self.assertFalse(acl.provides_access_for_ss_group())

    def test_provides_access_for_ss_group_2(self):
        acl = IrodsACL(access_group='ss_1234', zone='seq', permission='read')
        self.assertTrue(acl.provides_access_for_ss_group())




    def test_provides_read_permission_1(self):
        acl = IrodsACL(access_group='hgi', zone='seq', permission='read')
        self.assertTrue(acl.provides_read_permission())

    def test_provides_read_permission_2(self):
        acl = IrodsACL(access_group='hgi', zone='seq', permission='own')
        self.assertFalse(acl.provides_read_permission())


    def test_provides_write_permission_1(self):
        acl = IrodsACL(access_group='hgi', zone='seq', permission='write')
        self.assertTrue(acl.provides_write_permission())

    def test_provides_write_permission_2(self):
        acl = IrodsACL(access_group='hgi', zone='seq', permission='own')
        self.assertFalse(acl.provides_write_permission())


    def test_provides_own_permission_1(self):
        acl = IrodsACL(access_group='hgi', zone='seq', permission='own')
        self.assertTrue(acl.provides_own_permission())

    def test_provides_own_permission_2(self):
        acl = IrodsACL(access_group='hgi', zone='seq', permission='read')
        self.assertFalse((acl.provides_own_permission()))

    def test_provides_own_permission_3(self):
        acl = IrodsACL(access_group='hgi', zone='blah', permission='blah')
        self.assertRaises(ValueError, acl.provides_own_permission)

    def test_provides_own_permission_4(self):
        acl = IrodsACL(access_group='hgi', zone='blah', permission='my_own_permission')
        self.assertRaises(ValueError, acl.provides_own_permission)

    def test_is_permission_valid_1(self):
        acl = IrodsACL(access_group='hgi', zone='seq', permission='read')
        self.assertTrue(IrodsACL._is_permission_valid(acl.permission))

    def test_is_permission_valid_2(self):
        acl = IrodsACL('hgi', 'seq', 'tralalala')
        actual_result = acl._is_permission_valid(acl.permission)
        expected_result = False
        self.assertEqual(actual_result, expected_result)

    def test_is_permission_valid_3(self):
        self.assertFalse(IrodsACL._is_permission_valid(''))


    def test_is_irods_zone_valid_1(self):
        self.assertTrue(IrodsACL._is_irods_zone_valid('seq'))

    def test_is_irods_zone_valid_2(self):
        self.assertTrue(IrodsACL._is_irods_zone_valid('humgen'))

    def test_is_irods_zone_valid_3(self):
        self.assertFalse(IrodsACL._is_irods_zone_valid(''))

    def test_is_irods_zone_valid_4(self):
        self.assertFalse(IrodsACL._is_irods_zone_valid('blah'))

    def test_is_irods_zone_valid_5(self):
        self.assertFalse(IrodsACL._is_irods_zone_valid('seqseqseq'))



    def test_validate_fields_1(self):
        acl = IrodsACL(access_group='hgi', zone='seq', permission='read')
        self.assertEqual([], acl.validate_fields())

    def test_validate_fields_2(self):
        acl = IrodsACL(access_group='hgi', zone='seqhumgen', permission='read')
        self.assertEqual(len(acl.validate_fields()), 1)

    # def test_validate_fields_3(self):
    #     acl = IrodsACL(access_group='hgi', zone='seqhumgen', permission='smthelse')
    #     self.assertEqual(len(acl.validate_fields()), 2)
    #
    # def test_validate_fields_4(self):
    #     acl = IrodsACL(access_group='hgi', zone='seq', permission='')
    #     self.assertRaises(ValueError, acl.validate_fields)
    #

