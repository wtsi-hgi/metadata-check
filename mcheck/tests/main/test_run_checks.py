"""
Copyright (C) 2016  Genome Research Ltd.

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

This file has been created on Jun 13, 2016.
"""

import unittest

from mcheck.check_names import CHECK_NAMES
from mcheck.main.run_checks import decide_exit_status
from mcheck.results.checks_results import CheckResult
from mcheck.results.constants import RESULT

class TestRunChecks(unittest.TestCase):

    def test_decide_exit_status_when_all_pass(self):
        results = {'/path': [CheckResult(CHECK_NAMES.check_all_id_types_present), CheckResult(CHECK_NAMES.check_for_samples_in_more_studies),
        CheckResult(CHECK_NAMES.check_all_replicas_same_checksum), CheckResult(CHECK_NAMES.check_entities_in_seqscape_fetched_by_different_ids)]}
        self.assertEqual(decide_exit_status(results), 0)

    def test_decide_exit_status_when_some_failed(self):
        results = {'path': [CheckResult(CHECK_NAMES.check_all_id_types_present), CheckResult(CHECK_NAMES.check_all_id_types_present, result=RESULT.FAILURE)]}
        self.assertEqual(decide_exit_status(results), 1)

    def test_decide_exit_status_when_failed_irrelevant_tests(self):
        results = {'path': [CheckResult(CHECK_NAMES.check_all_id_types_present), CheckResult(CHECK_NAMES.check_for_samples_in_more_studies, result=RESULT.FAILURE)]}
        self.assertEqual(decide_exit_status(results), 0)






