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

This file has been created on Dec 01, 2015.
"""

import unittest

from mcheck.metadata.irods_metadata.file_replica import IrodsFileReplica


class TestIrodsFileReplica(unittest.TestCase):

    def test_is_replica_nr_valid_1(self):
        replica_nr = 1
        self.assertTrue(IrodsFileReplica._is_replica_nr_valid(replica_nr))

    def test_is_replica_nr_valid_2(self):
        replica_nr = '1'
        self.assertTrue(IrodsFileReplica._is_replica_nr_valid(replica_nr))

    def test_is_replica_nr_valid_3(self):
        replica_nr = 'blah123'
        self.assertFalse(IrodsFileReplica._is_replica_nr_valid(replica_nr))

    def test_is_replica_nr_valid_4(self):
        replica_nr = ''
        self.assertFalse(IrodsFileReplica._is_replica_nr_valid(replica_nr))

    def test_is_replica_nr_valid_5(self):
        self.assertRaises(TypeError, IrodsFileReplica._is_replica_nr_valid, None)

    def test_is_replica_nr_valid_6(self):
        self.assertRaises(TypeError, IrodsFileReplica._is_replica_nr_valid, [1,2,3])

    def test_is_replica_nr_valid_7(self):
        self.assertRaises(TypeError, IrodsFileReplica._is_replica_nr_valid, -1.2)



    def test_is_checksum_valid_1(self):
        checksum = '123acb'
        self.assertTrue(IrodsFileReplica._is_checksum_valid(checksum))

    def test_is_checksum_valid_2(self):
        checksum = 'AAAA'
        self.assertTrue(IrodsFileReplica._is_checksum_valid(checksum))

    def test_is_checksum_valid_3(self):
        checksum = None
        self.assertRaises(TypeError, IrodsFileReplica._is_checksum_valid, checksum)

    def test_is_checksum_valid_4(self):
        checksum = '12.24'
        self.assertFalse(IrodsFileReplica._is_checksum_valid(checksum))



    def test_validate_fields_1(self):
        replica = IrodsFileReplica(checksum='123abc', replica_nr=1)
        expected_result = []
        actual_result = replica.validate_fields()
        self.assertEqual(expected_result, actual_result)

    def test_validate_fields_2(self):
        replica = IrodsFileReplica(checksum='123abc', replica_nr=1)
        actual_result = replica.validate_fields()
        self.assertEqual(len(actual_result), 0)

    def test_validate_fields_3(self):
        replica = IrodsFileReplica(checksum='123abc', replica_nr=-1)
        actual_result = replica.validate_fields()
        self.assertEqual(1, len(actual_result))


