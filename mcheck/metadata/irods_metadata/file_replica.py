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

import re

import mcheck.metadata.irods_metadata.constants as irods_consts
from mcheck.results.checks_results import CheckResult
from mcheck.results.constants import SEVERITY
from mcheck.com import utils


class IrodsFileReplica:
    def __init__(self, checksum: str, replica_nr: int):
        self.checksum = checksum
        self.replica_nr = replica_nr

    @staticmethod
    def from_baton_wrapper(replica):
        return IrodsFileReplica(checksum=replica.checksum, replica_nr=replica.number)

    @staticmethod
    def _is_replica_nr_valid(replica_nr):
        if not type(replica_nr) in [str, int]:
            raise TypeError("WRONG type of parameter: replica_nr should be a digit and is: " + str(replica_nr))
        if type(replica_nr) is str:
            if not replica_nr.isdigit():
                return False
        if int(replica_nr) >= 0:
            return True
        return False

    @staticmethod
    def _is_checksum_valid(checksum):
        if not type(checksum) is str:
            raise TypeError("WRONG TYPE: the checksum must be a string, and is: " + str(type(checksum)))
        return utils.is_hexadecimal_string(checksum)

    def validate_fields(self):
        problems = []
        if not self._is_checksum_valid(self.checksum):
            problems.append(
                CheckResult(check_name="Check that the replica checksum field is valid", severity=SEVERITY.IMPORTANT,
                            error_message="The checksum looks invalid: " + str(self.checksum)))
        if not self._is_replica_nr_valid(self.replica_nr):
            problems.append(CheckResult(check_name="Check that the replica nr is valid", severity=SEVERITY.WARNING,
                                        error_message="The replica number looks invalid: " + str(self.replica_nr)))
        return problems

    def __eq__(self, other):
        return self.checksum == other.checksum and self.replica_nr == other.replica_nr

    def __str__(self):
        return "Replica nr =  " + str(self.replica_nr) + ", checksum = " + str(self.checksum)

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.checksum) + hash(self.replica_nr)

# EXAMPLE OF FILE REPLICAS:
# OWNED:
# {"collection": "/seq/10080", "data_object": "10080_8#64.bam",
# "replicate": [{"checksum": "dd6163040f095c571f714169e079f50d", "number": 0, "valid": true},
# {"checksum": "dd6163040f095c571f714169e079f50d", "number": 1, "valid": true}],
# "checksum": "dd6163040f095c571f714169e079f50d",
# "access": [{"owner": "trace", "zone": "Sanger1", "level": "read"},
# {"owner": "ss_2034", "zone": "seq", "level": "read"}, {"owner": "srpipe", "zone": "Sanger1", "level": "own"},
# {"owner": "rodsBoot", "zone": "seq", "level": "own"}, {"owner": "irods_metadata-g1", "zone": "seq", "level": "own"},
# {"owner": "psdpipe", "zone": "Sanger1", "level": "read"}]}

