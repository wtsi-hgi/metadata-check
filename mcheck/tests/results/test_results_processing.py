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

This file has been created on Jun 08, 2016.
"""
import unittest

from mcheck.results.results_processing import CheckResultsProcessing
from mcheck.results.checks_results import CheckResult
from mcheck.results.constants import SEVERITY, RESULT

class CheckResultsProcessingGroupedByExecutedTest(unittest.TestCase):

    def test_group_by_executed_when_all_executed(self):
        check_res1 = CheckResult(check_name="Some check", executed=True, result=RESULT.SUCCESS, severity=SEVERITY.IMPORTANT)
        check_res2 = CheckResult(check_name="Some check", executed=True, result=RESULT.SUCCESS, severity=SEVERITY.IMPORTANT)
        check_results = [check_res1, check_res2]
        res = CheckResultsProcessing.group_by_executed(check_results)
        expected = {True: check_results}
        self.assertSetEqual(set(res), set(expected))

    def test_group_by_executed_when_some_executed(self):
        check_res1 = CheckResult(check_name="Some check", executed=True, result=RESULT.SUCCESS, severity=SEVERITY.IMPORTANT)
        check_res2 = CheckResult(check_name="Some check", executed=False, result=None, severity=SEVERITY.IMPORTANT)
        check_results = [check_res1, check_res2]
        executed = [check_res1]
        not_executed = [check_res2]
        res = CheckResultsProcessing.group_by_executed(check_results)
        expected = {True: executed, False: not_executed}
        self.assertDictEqual(res, expected)

    def test_group_by_executed_when_no_result(self):
        check_results = []
        res = CheckResultsProcessing.group_by_executed(check_results)
        expected = {}
        self.assertDictEqual(res, expected)


class CheckResultsProcessingGroupedBySeverityTest(unittest.TestCase):

    def test_group_by_severity(self):
        check_res1 = CheckResult(check_name='Some check1', executed=True, result=RESULT.SUCCESS, severity=SEVERITY.CRITICAL)
        check_res2 = CheckResult(check_name='Some check1', executed=False, result=RESULT.SUCCESS, severity=SEVERITY.WARNING)
        check_res3 = CheckResult(check_name='Some check1', executed=True, result=RESULT.FAILURE, severity=SEVERITY.IMPORTANT)
        check_results = [check_res1, check_res2, check_res3]
        res = CheckResultsProcessing.group_by_severity(check_results)
        expected = {SEVERITY.IMPORTANT : [check_res3], SEVERITY.WARNING: [check_res2], SEVERITY.CRITICAL: [check_res1]}
        self.assertDictEqual(res, expected)



class CheckResultsProcessingGroupByResultTest(unittest.TestCase):

    def test_group_by_result(self):
        check_res1 = CheckResult(check_name='Some check1', executed=False, result=RESULT.SUCCESS, severity=SEVERITY.WARNING)
        check_res2 = CheckResult(check_name='Some check1', executed=True, result=RESULT.FAILURE, severity=SEVERITY.IMPORTANT)
        check_results = [check_res1, check_res2]
        res = CheckResultsProcessing.group_by_result(check_results)
        expected = {RESULT.SUCCESS : [check_res1], RESULT.FAILURE: [check_res2]}
        self.assertDictEqual(res, expected)








