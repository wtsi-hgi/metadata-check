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
from collections import  defaultdict


class FileMetadataComparison:


    # @staticmethod
    # def _comparison_checks_for_2_sources(metadata1, metadata2):

    @staticmethod
    def check_metadata_across_different_sources(irods_metadata_dict, header_metadata_dict, seqsc_metadata_dict, issues_dict):
        """
        This function checks the metadata from 3 different sources in terms of samples, libraries and studies.
        At the moment the checks across these sources consist of comparing: libraries, studies and samples
        As a result it updates the issues_dict by appending the CheckResults obtain after running the latest tests.
        :param irods_metadata_dict: key: fpath, value: irods_metadata for that file
        :param header_metadata_dict: key: fpath, value: header_metadata for that file
        :param seqsc_metadata_dict: key: fpath, value: seqscape_metadata for that file
        :param issues_dict: key: fpath, value: list of CheckResults
        :return:
        """
        for fpath, irods_metadata in irods_metadata_dict.items():
            header_metadata = header_metadata_dict[fpath]
            seqscape_metadata = seqsc_metadata_dict[fpath]

            seqscape_diff_header = seqscape_metadata.difference(header_metadata)
            header_diff_seqscape = header_metadata.difference(seqscape_metadata)

            irods_diff_header = irods_metadata.difference(header_metadata)
            header_diff_irods = header_metadata.difference(irods_metadata)
            # seqscape_diff_header = FileMetadataComparison._find_differences(seqscape_metadata, header_metadata,
            #                                                                ['samples', 'libraries', 'studies'])
            # header_diff_seqscape = FileMetadataComparison._find_differences(header_metadata, seqscape_metadata,
            #                                                                ['samples', 'libraries', 'studies'])
            #
            # irods_diff_header = FileMetadataComparison._find_differences(irods_metadata, header_metadata,
            #                                                             ['samples', 'libraries', 'studies'])
            # header_diff_irods = FileMetadataComparison._find_differences(header_metadata, irods_metadata,
            #                                                             ['samples', 'libraries', 'studies'])

            impossible_to_exe = False
            if not seqscape_metadata and not header_metadata:
                error_msg = "No seqscape metadata and no header_metadata"
                impossible_to_exe = True
            elif not seqscape_metadata:
                impossible_to_exe = True
                error_msg = "No seqscape metadata"
            elif not header_metadata:
                impossible_to_exe = True
                error_msg = "No header metadata"

            if impossible_to_exe:
                ss_vs_h_check_result = CheckResult(check_name=CHECK_NAMES.check_seqscape_ids_compared_to_header_ids, executed=False, error_message=error_msg)
                h_vs_ss_check_result = CheckResult(check_name=CHECK_NAMES.check_header_ids_compared_to_seqscape_ids, executed=False, error_message=error_msg)
                issues_dict[fpath].append(ss_vs_h_check_result)
                issues_dict[fpath].append(h_vs_ss_check_result)
            else:
                ss_vs_h_check_result = CheckResult(check_name=CHECK_NAMES.check_seqscape_ids_compared_to_header_ids)
                if seqscape_diff_header:
                    error_msg = "Differences: %s" % seqscape_diff_header
                    ss_vs_h_check_result.error_message = error_msg
                    ss_vs_h_check_result.result = RESULT.FAILURE
                issues_dict[fpath].append(ss_vs_h_check_result)

                h_vs_ss_check_result = CheckResult(check_name=CHECK_NAMES.check_header_ids_compared_to_seqscape_ids)
                if header_metadata and seqscape_metadata:
                    if header_diff_seqscape:
                        error_msg = "Differences: %s" % header_diff_seqscape
                        h_vs_ss_check_result.result = RESULT.FAILURE
                        h_vs_ss_check_result.error_message = error_msg
                issues_dict[fpath].append(h_vs_ss_check_result)


            impossible_to_exe = False
            error_msg = ""
            if not irods_metadata and not header_metadata:
                error_msg = "No header_metadata and no irods_metadata"
                impossible_to_exe = True
            elif not irods_metadata:
                error_msg = "No irods_metadata"
                impossible_to_exe = True
            elif not header_metadata:
                error_msg = "No header metadata"
                impossible_to_exe = True

            if impossible_to_exe:
                i_vs_h_check_result = CheckResult(check_name=CHECK_NAMES.check_irods_ids_compared_to_header_ids, executed=False, error_message=error_msg)
                h_vs_i_check_result = CheckResult(check_name=CHECK_NAMES.check_header_ids_compared_to_irods_ids, executed=False, error_message=error_msg)
                issues_dict[fpath].append(i_vs_h_check_result)
                issues_dict[fpath].append(h_vs_i_check_result)
            else:
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




