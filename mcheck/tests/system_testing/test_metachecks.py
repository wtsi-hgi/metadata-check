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

This file has been created on Jun 07, 2016.
"""

import unittest
from mcheck.main import run_checks
from mcheck.check_names import CHECK_NAMES
from mcheck.results.checks_results import RESULT

@unittest.skip
class MetadataFetchedByPathTest(unittest.TestCase):
    def setUp(self):
        self.comparison_checks = [
            CHECK_NAMES.check_seqscape_ids_compared_to_header_ids,
            CHECK_NAMES.check_header_ids_compared_to_seqscape_ids,
            CHECK_NAMES.check_irods_ids_compared_to_header_ids,
            CHECK_NAMES.check_header_ids_compared_to_irods_ids,
        ]

    def test_metadata_for_library_file(self):
        """
         The file tested has metadata just like a library cram, except for some fields that are not used within metacheck
         anyway. It is a txt file, so it will have no header metadata.
        """
        irods_fpath = "/humgen/projects/serapis_staging/test-metacheck/test_metadata.txt"

        result = run_checks.check_metadata(metadata_fetching_strategy='fetch_by_path', irods_fpaths=[irods_fpath])
        print("Comparisong checks: %s" % self.comparison_checks)
        for fpath, check_results in result.items():
            check_names = [c.check_name for c in check_results]
            self.assertSetEqual(set(check_names), set(CHECK_NAMES.get_only_mandatory_check_names()))
            for check_res in check_results:
                print("Printing check name: %s " % check_res.check_name)
                if check_res.check_name in self.comparison_checks:
                    print("Found match with %s " % (check_res.check_name))
                    self.assertFalse(check_res.executed)
                elif check_res.check_name in [
                    CHECK_NAMES.check_ss_irods_group_read_permission,
                    CHECK_NAMES.check_there_is_ss_irods_group,
                    CHECK_NAMES.check_studies_in_irods_with_studies_in_seqscape_fetched_by_samples,
                    CHECK_NAMES.check_samples_in_irods_same_as_samples_fetched_by_study_from_seqscape
                ]:
                    print("Found match in the failed category: %s" % check_res.check_name)
                    self.assertTrue(check_res.executed)
                    self.assertEqual(check_res.result, RESULT.FAILURE)


    def test_metadata_when_metadata_ok(self):
        irods_fpath = "/humgen/projects/serapis_staging/test-metacheck/test_ok_metadata.out"
        result = run_checks.check_metadata(metadata_fetching_strategy='fetch_by_path', irods_fpaths=[irods_fpath])
        for fpath, check_results in result.items():
            check_names = [c.check_name for c in check_results]
            self.assertSetEqual(set(check_names), set(CHECK_NAMES.get_only_mandatory_check_names()))
            for check_res in check_results:
                if check_res.check_name in self.comparison_checks:
                    self.assertFalse(check_res.executed)
                elif check_res.check_name in [
                    CHECK_NAMES.check_there_is_ss_irods_group,
                    CHECK_NAMES.check_ss_irods_group_read_permission,
                    CHECK_NAMES.check_for_samples_in_more_studies,

                ]:
                    self.assertEqual(RESULT.FAILURE, check_res.result)
                else:
                    self.assertEqual(RESULT.SUCCESS, check_res.result)


    def test_metadata_when_metadata_ok_with_reference(self):
        irods_fpath = "/humgen/projects/serapis_staging/test-metacheck/test_ok_metadata.out"
        result = run_checks.check_metadata(metadata_fetching_strategy='fetch_by_path', irods_fpaths=[irods_fpath], reference='GRCh38')
        for fpath, check_results in result.items():
            for check_res in check_results:
                if check_res.check_name == CHECK_NAMES.check_desired_reference:
                    self.assertEqual(check_res.result, RESULT.SUCCESS)


    def test_metadata_when_metadata_ok_with_wrong_reference(self):
        irods_fpath = "/humgen/projects/serapis_staging/test-metacheck/test_ok_metadata.out"
        result = run_checks.check_metadata(metadata_fetching_strategy='fetch_by_path', irods_fpaths=[irods_fpath], reference='hs37d5')
        for fpath, check_results in result.items():
            for check_res in check_results:
                if check_res.check_name == CHECK_NAMES.check_desired_reference:
                    self.assertEqual(check_res.result, RESULT.FAILURE)

    def test_metadata_when_metadata_ok_with_wrong_reference2(self):
        irods_fpath = "/humgen/projects/serapis_staging/test-metacheck/test_metadata_missing_md5.out"
        result = run_checks.check_metadata(metadata_fetching_strategy='fetch_by_path', irods_fpaths=[irods_fpath], reference='grch38')
        for fpath, check_results in result.items():
            for check_res in check_results:
                if check_res.check_name == CHECK_NAMES.check_desired_reference:
                    self.assertEqual(check_res.executed, False)



        # def check_metadata(metadata_fetching_strategy, reference=None, filter_npg_qc=None, filter_target=None, file_types=None,
        # study_name=None, study_acc_nr=None, study_internal_id=None, irods_fpaths=None, irods_zone=None):
        #     issues_dict = defaultdict(list)
        #     # Getting iRODS metadata for files and checking before bringing it a "normalized" form:
        #     # TODO: add the option of getting the metadata as a json from the command line...
        #     if metadata_fetching_strategy == 'fetch_by_metadata':
        #         search_criteria = convert_args_to_search_criteria(filter_npg_qc, filter_target,
        #                                                           file_types, study_name,
        #                                                           study_acc_nr, study_internal_id)
        #
        #         irods_metadata_dict = MetadataSelfChecks.fetch_and_preprocess_irods_metadata_by_metadata(search_criteria, irods_zone, issues_dict, reference)
        #     elif metadata_fetching_strategy == 'fetch_by_path':
        #         irods_metadata_dict = MetadataSelfChecks.fetch_and_preprocess_irods_metadata_by_path(irods_fpaths, issues_dict, reference)
        #
        #     # Getting HEADER metadata:
        #     header_metadata_dict = MetadataSelfChecks.fetch_and_preprocess_header_metadata(irods_metadata_dict.keys(), issues_dict)
        #
        #     # Getting Seqscape metadata:
        #     seqsc_metadata_dict = MetadataSelfChecks.fetch_and_preprocess_seqscape_metadata(irods_metadata_dict, issues_dict)
        #
        #     # Running checks to compare metadata obtained from different sources:
        #     FileMetadataComparison.check_metadata_across_different_sources(irods_metadata_dict, header_metadata_dict, seqsc_metadata_dict, issues_dict)
        #
        #     return issues_dict