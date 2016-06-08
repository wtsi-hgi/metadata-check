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

This file has been created on May 26, 2016.
"""

from mcheck.results.checks_results import RESULT, SEVERITY
from mcheck.results.checks_results import CheckResult
from collections import defaultdict

class CheckResultsProcessing:

    @staticmethod
    def group_by_executed(check_results):
        """
        Filters the check results and return only the checks that could be executed.
        :param check_results: list of CheckResults
        :return: filtered list of CheckResults
        """
        exec_dict = defaultdict(list)
        for result in check_results:
            exec[result.executed].append(result)
        return exec_dict

    @staticmethod
    def group_by_severity(check_results):
        """
        This method groups the check results by severity, and returns them in a dict,
        where key=severity, value = list of CheckResults with that severity.
        :param check_results: list of CheckResults
        :return: dict with key = severity, value = list of CheckResults
        """
        severity_dict = defaultdict(list)
        for result in check_results:
            severity_dict[result.severity].append(result)
        return severity_dict

    @staticmethod
    def group_by_result(check_results):
        """
        This method is meant to group the result within the CheckResults by whether the test was passed or failed
        :param check_results: list of CheckResults
        :return: list of CheckResults
        """
        result_dict = defaultdict(list)
        for result in check_results:
            result_dict[result.result].append(result)
        return result_dict