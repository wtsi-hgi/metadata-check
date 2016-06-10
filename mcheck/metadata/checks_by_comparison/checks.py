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

This file has been created on Jun 10, 2016.
"""

from mcheck.results.checks_results import CheckResult, RESULT
from mcheck.check_names import CHECK_NAMES


class FileMetadataComparison:

    @staticmethod
    def find_differences(metadata1, metadata2, entity_types_list):
        for entity_type in entity_types_list:
            metadata_entities1 = getattr(metadata1, entity_type)  # header
            metadata_entities2 = getattr(metadata2, entity_type)  # seqsc
            differences = {}
            for id_type, values in metadata_entities1.items():
                if values and metadata_entities2.get(id_type):
                    if values != metadata_entities2.get(id_type):
                        differences[id_type] = set(values).difference(set(metadata_entities2.get(id_type)))
            return differences


    @staticmethod
    def check_metadata_across_different_sources(irods_metadata_dict, header_metadata_dict, seqsc_metadata_dict, issues_dict):
        """
        This function checks the metadata from 3 different sources in terms of samples, libraries and studies.
        As a result it updates the issues_dict by appending the CheckResults obtain after running the latest tests.
        :param irods_metadata_dict:
        :param header_metadata_dict:
        :param seqsc_metadata_dict:
        :param issues_dict:
        :return:
        """
        for fpath, irods_metadata in irods_metadata_dict.items():
            header_metadata = header_metadata_dict[fpath]
            seqscape_metadata = seqsc_metadata_dict[fpath]
            seqscape_diff_header = FileMetadataComparison.find_differences(seqscape_metadata, header_metadata,
                                                                           ['samples', 'libraries', 'studies'])
            header_diff_seqscape = FileMetadataComparison.find_differences(header_metadata, seqscape_metadata,
                                                                           ['samples', 'libraries', 'studies'])

            irods_diff_header = FileMetadataComparison.find_differences(irods_metadata, header_metadata,
                                                                        ['samples', 'libraries', 'studies'])
            header_diff_irods = FileMetadataComparison.find_differences(header_metadata, irods_metadata,
                                                                        ['samples', 'libraries', 'studies'])

            print("Irods metadata: %s" % irods_metadata)
            print("Seqscape metadata: %s" % seqscape_metadata)
            print("Header metadata: %s" % header_metadata)
            ss_vs_h_check_result = CheckResult(check_name=CHECK_NAMES.check_seqscape_ids_compared_to_header_ids)
            if seqscape_diff_header:
                error_msg = "Differences: %s" % seqscape_diff_header
                ss_vs_h_check_result.error_message = error_msg
                ss_vs_h_check_result.result = RESULT.FAILURE
            issues_dict[fpath].append(ss_vs_h_check_result)

            h_vs_ss_check_result = CheckResult(check_name=CHECK_NAMES.check_header_ids_compared_to_seqscape_ids)
            if header_diff_seqscape:
                error_msg = "Differences: %s" % header_diff_seqscape
                h_vs_ss_check_result.result = RESULT.FAILURE
                h_vs_ss_check_result.error_message = error_msg
            issues_dict[fpath].append(h_vs_ss_check_result)

            i_vs_h_check_result = CheckResult(check_name=CHECK_NAMES.check_irods_ids_compared_to_header_ids)
            if irods_diff_header:
                error_msg = "Differences: %s" % irods_diff_header
                i_vs_h_check_result.error_message = error_msg
                i_vs_h_check_result.result = RESULT.FAILURE
            issues_dict[fpath].append(i_vs_h_check_result)

            h_vs_i_check_result = CheckResult(check_name=CHECK_NAMES.check_header_ids_compared_to_irods_ids)
            if header_diff_irods:
                error_msg = "Differences between what is in the header and not in iRODS: %s" % header_diff_irods
                h_vs_i_check_result.error_message = error_msg
                h_vs_i_check_result.result = RESULT.FAILURE
            issues_dict[fpath].append(h_vs_i_check_result)




