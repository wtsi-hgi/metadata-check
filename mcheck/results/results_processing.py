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

class CheckResultsProcessing:

    @staticmethod
    def filter_by_severity(check_results, lowest_severity):
        """
        Filters the check results by the severity of the check.
        It includes all the checks with severity higher than the lowest bound given as parameter.
        :param check_results: list of CheckResults
        :return: filtered list of CheckResults
        """
        pass

    @staticmethod
    def filter_by_result(check_results, result=RESULT.FAILURE):
        """
        Filters the check results by the result type and return only the check results that match the result parameter.
        :param check_results: a list of CheckResults
        :param result: string from RESULT class
        :return: filtered list of CheckResults
        """
        return [cr for cr in check_results if cr.result == result]

    @staticmethod
    def filter_executed(check_results):
        """
        Filters the check results and return only the checks that could be executed.
        :param check_results: list of CheckResults
        :return: filtered list of CheckResults
        """
        return [cr for cr in check_results if cr.executed is True]