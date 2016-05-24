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

This file has been created on May 20, 2016.
"""


class CHECK_NAMES:
    valid_replica_checksum_check = "Check that the replica checksum field is valid"
    valid_replica_number_check = "Check that the replica number is valid"
    attribute_count_check = "Check attribute count is as configured"
    check_all_replicas_same_checksum = "Check all replicas have the same checksum"
    check_more_than_one_replica = "Check that file has more than 1 replica"
    check_no_public_acl = "Check that there are no public ACLS"
    check_ss_irods_group_read_permission = "Check that the permission for iRODS ss_<id> user group is READ"
    check_there_is_ss_irods_group = "Check ACLs contain at least one ss_<id> group"
    check_checksum_in_metadata_present = "Check that checksum present within metadata"
    check_checksum_at_upload_present = "Check that checksum at upload(ichksum) present"
    check_by_comparison_checksum_in_meta_with_checksum_at_upload = "Compare checksum in metadata with checksum at upload"
    check_npg_qc_field = "Check that the NPG QC field is valid"
    check_target_field = "Check that the target field is valid"
    check_desired_reference = "Check that the reference for this file is the one desired"


