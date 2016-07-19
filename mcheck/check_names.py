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
    check_replica_checksum_valid = "Check that the replica checksum field is valid"
    check_replica_number = "Check that the replica number is valid"
    check_attribute_count = "Check attribute count is as configured"
    check_all_replicas_same_checksum = "Check all replicas have the same checksum"
    check_more_than_one_replica = "Check that file has more than 1 replica"
    check_no_public_acl = "Check that there are no public ACLS"
    check_ss_irods_group_read_permission = "Check that non-NPG groups have READ permission"
    check_there_is_ss_irods_group = "Check non-NPG user groups have access to data"
    check_checksum_in_metadata_present = "Check that checksum present within metadata"
    check_checksum_at_upload_present = "Check that checksum at upload(ichksum) present"
    check_by_comparison_checksum_in_meta_with_checksum_at_upload = "Compare checksum in metadata with checksum at upload"
    check_npg_qc_field = "Check that the NPG QC field is valid"
    check_target_field = "Check that the target field is valid"
    check_desired_reference = "Check that the reference for this file is the one desired"
    check_irods_zone_within_acl = "Check valid iRODS zone in ACL"
    check_irods_permission_within_acl = "Check valid permission in ACL"
    check_valid_ids = "Check valid id strings"
    check_all_irods_ids_found_in_seqscape = "Check all iRODS ids were found in seqscape"
    check_for_duplicated_ids_within_seqscape = "Check for duplicated ids within seqscape"
    check_entities_in_seqscape_fetched_by_different_ids = "Check entities fetched by different types of ids from Seqscape"
    check_studies_in_irods_with_studies_in_seqscape_fetched_by_samples = "Check that the studies in iRODS are the same as the studies fetched from Seqscape when querying by sample"
    check_samples_in_irods_same_as_samples_fetched_by_study_from_seqscape = "Check that the samples in iRODS are the same as the samples fetched by study from Seqscape"
    check_for_samples_in_more_studies = "Check if a set of samples is in more studies within Seqscape"
    check_all_id_types_present = 'Check that all id types are present'
    check_seqscape_ids_compared_to_header_ids = "Compare what is in seqscape and not in header"
    check_header_ids_compared_to_seqscape_ids = "Compare what is in the header and not in seqscape"
    check_irods_ids_compared_to_header_ids = "Compare what is in iRODS and not in the header"
    check_header_ids_compared_to_irods_ids = "Compare what is in the header and not in iRODS"

    @classmethod
    def get_check_names(cls):
        checks = dir(CHECK_NAMES)
        return [getattr(CHECK_NAMES, c) for c in checks if c.startswith('check_')]

    @classmethod
    def get_only_mandatory_check_names(cls):
        optional_checks = ['check_desired_reference', 'check_attribute_count' ]
        checks = dir(CHECK_NAMES)
        return [getattr(CHECK_NAMES, c) for c in checks if c.startswith('check_') and not c in optional_checks]