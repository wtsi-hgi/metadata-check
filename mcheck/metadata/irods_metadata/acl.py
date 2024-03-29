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
from mcheck.results.constants import SEVERITY, RESULT
from mcheck.check_names import CHECK_NAMES


class IrodsACL:
    def __init__(self, access_group: str, zone: str, permission: str):
        self.access_group = access_group
        self.zone = zone
        self.permission = permission
        # TODO: this should be self._is_permission_valid()
        # try:
        #     print("PERMISSION before except : %s " % permission)
        #     self.permission = irods_consts.IrodsPermission(permission)
        # except KeyError:
        #     raise ValueError("The permission is not right: %s " % permission)


    @staticmethod
    def from_baton_wrapper(acl_item):
        def get_corresponding_permission(perm):
            if perm == 'READ':
                return irods_consts.IrodsPermission.READ
            elif perm == 'WRITE':
                return irods_consts.IrodsPermission.WRITE
            elif perm == 'OWN':
                return irods_consts.IrodsPermission.OWN
            elif perm == 'null':
                return irods_consts.IrodsPermission.NULL
            else:
                raise ValueError("This permission %s is not recognized." % perm)

        permission = get_corresponding_permission(acl_item.level.name)
        return IrodsACL(access_group=acl_item.user.name, zone=acl_item.user.zone, permission=permission)

    def provides_public_access(self):
        return self.access_group.startswith(irods_consts.IrodsGroups.PUBLIC.value)

    def provides_access_for_ss_group(self):
        r = re.compile(irods_consts.IrodsGroups.SS_GROUP_REGEX.value)
        if r.match(self.access_group):
            return True
        return False

    def provides_read_permission(self):
        return irods_consts.IrodsPermission(self.permission) == irods_consts.IrodsPermission.READ

    def provides_write_permission(self):
        return irods_consts.IrodsPermission(self.permission) == irods_consts.IrodsPermission.WRITE

    def provides_own_permission(self):
        return irods_consts.IrodsPermission(self.permission) == irods_consts.IrodsPermission.OWN

    @staticmethod
    def _is_permission_valid(permission: str):
        # if permission and not type(permission) in [enum, str]:
        #     raise TypeError("This permission is not a string, it is a %s" % str(type(permission)))
        try:
            irods_consts.IrodsPermission(permission)
        except KeyError:
            raise TypeError("This permission is not correct: " + str(permission))
        except ValueError:
            return False
        else:
            return True

    @staticmethod
    def _is_irods_zone_valid(zone):
        # Dirty hack to get over the issue of not getting the zone from baton
        if not zone:
            return True
        if zone and not type(zone) is str:
            raise TypeError("This zone is not a string, it is a: %s " % str(type(zone)))
        try:
            irods_consts.IrodsZones(zone)
        except ValueError:
            return False
        else:
            return True

    def validate_fields(self):
        check_results = []
        zone_check_result = CheckResult(check_name=CHECK_NAMES.check_irods_zone_within_acl, severity=SEVERITY.WARNING)
        if not self._is_irods_zone_valid(self.zone):
            zone_check_result.result = RESULT.FAILURE
            zone_check_result.error_message="The iRODS zone seems wrong: " + str(self.zone) + " in acl = " + str(self)
        check_results.append(zone_check_result)

        permission_check_result = CheckResult(check_name=CHECK_NAMES.check_irods_permission_within_acl, severity=SEVERITY.WARNING)
        if not self._is_permission_valid(self.permission):
            permission_check_result.result = RESULT.FAILURE
            permission_check_result.error_message = "The iRODS permission seems wrong: " + str(self.permission) + " in  acl = " + str(self)
        check_results.append(permission_check_result)
        return check_results

    def __eq__(self, other):
        return self.access_group == other.access_group and self.zone == other.zone and \
               self.permission == other.permission

    def __str__(self):
        return "Access group = " + str(self.access_group) + ", zone: " + \
               str(self.zone) + ", permission = " + str(self.permission)

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.access_group) + hash(self.zone) + hash(self.permission)



# EXAMPLE OF ACL
# PUBLIC:
# jq -n '{collection: "/seq/10001", data_object: "10001_1#30_phix.bai"}' | /software/gapi/pkg/baton/0.15.0/bin/baton-list
# --acl --checksum --replicate{"collection": "/seq/10001", "data_object": "10001_1#30_phix.bai",
# "replicate": [{"checksum": "2b84f847c8418e5d1ccb26e8e5633c53", "number": 0, "valid": true},
# {"checksum": "2b84f847c8418e5d1ccb26e8e5633c53", "number": 1, "valid": true}],
# "checksum": "2b84f847c8418e5d1ccb26e8e5633c53",
# "access": [{"owner": "trace", "zone": "Sanger1", "level": "read"},
# {"owner": "srpipe", "zone": "Sanger1", "level": "own"},
# {"owner": "rodsBoot", "zone": "seq", "level": "own"},
# {"owner": "irods_metadata-g1", "zone": "seq", "level": "own"},
# {"owner": "public", "zone": "seq", "level": "read"},
# {"owner": "psdpipe", "zone": "Sanger1", "level": "read"}]}

