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

This file has been created on Nov 27, 2015.
"""

from hgijson import JsonPropertyMapping
from mcheck.results.constants import SEVERITY, RESULT


class CheckResult:

    def __init__(self, check_name, executed=True, result=RESULT.SUCCESS, severity=SEVERITY.IMPORTANT, error_message=None):
        self.check_name = check_name
        self.severity = severity
        self.error_message = error_message
        self.executed = executed
        self.result = result        # Can be: FAILURE, SUCCESSFUL, NONE - if the test wasn't executed

    def __str__(self):
        msg = "Check name: " + str(self.check_name) + ", severity = " + str(self.severity) + ", "
        msg = msg + " executed: " + str(self.executed) + ", result = "
        msg += str(self.result)
        msg = (msg + ": " + str(self.error_message)) if self.error_message else msg
        return msg

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        if not type(other) == type(self):
            return False
        return self.check_name == other.check_name and self.error_message == other.error_message and \
               self.severity == other.severity and self.executed == other.executed and self.result == other.result

    @classmethod
    def to_json_mapping(cls):
        return [
        JsonPropertyMapping("check_name", "check_name", "check_name"),
        JsonPropertyMapping("severity", "severity", optional=True),
        JsonPropertyMapping("error_message", "error_message", optional=True),
        JsonPropertyMapping("executed", "executed", optional=True),
        JsonPropertyMapping("result", "result", optional=True)
    ]

