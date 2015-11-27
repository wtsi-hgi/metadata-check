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



# each checking function returns the same type of namedtuple/whatnot with:
# -error severity, or error type, or error group, or something like that
# -the source (for sorting?)
# -the actual human readable error message string
#
# the collecting part just has to understand how to present all those to the user


from results.constants import SEVERITY

class CheckResult:

    def __init__(self, severity=SEVERITY.IMPORTANT, error_message=None, source=None):
        self.severity = severity
        self.error_message = error_message
        self.source = source

    def __str__(self):
        msg = "Severity = " + self.severity + ", "
        msg = (msg + " source: " + self.source + ", ") if self.source else msg
        msg = (msg + " error message: " + self.error_message + ", ") if self.error_message else msg
        return msg

    def __repr__(self):
        return self.__str__()




