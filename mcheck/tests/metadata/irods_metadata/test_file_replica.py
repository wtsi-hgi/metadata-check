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
from mcheck.results.checks_results import SEVERITY, RESULT
from mcheck.check_names import CHECK_NAMES


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


    def test_validate_fields_when_all_ok(self):
        replica = IrodsFileReplica(checksum='123abc', replica_nr=1)
        actual_result = replica.validate_fields()
        self.assertEqual(len(actual_result), 2)
        for result in actual_result:
            if result.check_name == CHECK_NAMES.check_replica_checksum:
                self.assertEqual(result.result, RESULT.SUCCESS)
            if result.check_name == CHECK_NAMES.check_replica_number:
                self.assertEqual(result.result, RESULT.SUCCESS)

    def test_validate_fields_when_replica_nr_wrong(self):
        replica = IrodsFileReplica(checksum='123abc', replica_nr=-1)
        actual_result = replica.validate_fields()
        self.assertEqual(2, len(actual_result))
        for result in actual_result:
            if result.check_name == CHECK_NAMES.check_replica_checksum:
                self.assertEqual(result.result, RESULT.SUCCESS)
            if result.check_name == CHECK_NAMES.check_replica_number:
                self.assertEqual(result.result, RESULT.FAILURE)


    # def validate_fields(self):
        # check_results = []
        # checksum_check_result = CheckResult(check_name="Check that the replica checksum field is valid",
        #                                     severity=SEVERITY.IMPORTANT)
        # if not self._is_checksum_valid(self.checksum):
        #     checksum_check_result.result = RESULT.FAILURE
        #     checksum_check_result.error_message = "The checksum looks invalid: " + str(self.checksum)
        #
        # valid_replicas_check_result = CheckResult(check_name="Check that the replica nr is valid",
        #                                           severity=SEVERITY.WARNING)
        # if not self._is_replica_nr_valid(self.replica_nr):
        #     valid_replicas_check_result.result = RESULT.FAILURE
        #     valid_replicas_check_result.error_message = "The replica number looks invalid: " + str(self.replica_nr)
        #
        # check_results.append(checksum_check_result)
        # check_results.append(valid_replicas_check_result)
        # return check_results



