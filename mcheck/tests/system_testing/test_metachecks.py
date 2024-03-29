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
from unittest.mock import patch
from mcheck.main import api
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

        result = api.check_metadata_fetched_by_path(irods_fpaths=[irods_fpath])
        print("Comparisong checks: %s" % self.comparison_checks)
        for fpath, check_results in result.items():
            check_names = [c.check_name for c in check_results]
            self.assertSetEqual(set(check_names), set(CHECK_NAMES.get_only_mandatory_check_names()))
            for check_res in check_results:
                if check_res.check_name in self.comparison_checks:
                    self.assertFalse(check_res.executed)
                elif check_res.check_name in [
                    CHECK_NAMES.check_ss_irods_group_read_permission,
                    CHECK_NAMES.check_there_is_ss_irods_group,
                    CHECK_NAMES.check_studies_in_irods_with_studies_in_seqscape_fetched_by_samples,
                    CHECK_NAMES.check_samples_in_irods_same_as_samples_fetched_by_study_from_seqscape
                ]:
                    self.assertTrue(check_res.executed)
                    self.assertEqual(check_res.result, RESULT.FAILURE)


    def test_metadata_when_metadata_ok(self):
        irods_fpath = "/humgen/projects/serapis_staging/test-metacheck/test_ok_metadata.out"
        result = api.check_metadata_fetched_by_path(irods_fpaths=[irods_fpath])
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
        result = api.check_metadata_fetched_by_path(irods_fpaths=[irods_fpath], reference='GRCh38')
        for fpath, check_results in result.items():
            for check_res in check_results:
                if check_res.check_name == CHECK_NAMES.check_desired_reference:
                    self.assertEqual(check_res.result, RESULT.SUCCESS)


    def test_metadata_when_metadata_ok_with_wrong_reference(self):
        irods_fpath = "/humgen/projects/serapis_staging/test-metacheck/test_ok_metadata.out"
        result = api.check_metadata_fetched_by_path(irods_fpaths=[irods_fpath], reference='hs37d5')
        for fpath, check_results in result.items():
            for check_res in check_results:
                if check_res.check_name == CHECK_NAMES.check_desired_reference:
                    self.assertEqual(check_res.result, RESULT.FAILURE)

    def test_metadata_when_metadata_ok_with_wrong_reference_and_one_replica(self):
        irods_fpath = "/humgen/projects/serapis_staging/test-metacheck/test_metadata_missing_md5.out"
        result = api.check_metadata_fetched_by_path(irods_fpaths=[irods_fpath], reference='grch38')
        for fpath, check_results in result.items():
            for check_res in check_results:
                if check_res.check_name == CHECK_NAMES.check_desired_reference:
                    self.assertEqual(check_res.executed, False)
                elif check_res.check_name in [CHECK_NAMES.check_more_than_one_replica,
                                              CHECK_NAMES.check_ss_irods_group_read_permission,
                                              CHECK_NAMES.check_there_is_ss_irods_group,
                                              ]:
                    self.assertEqual(check_res.result, RESULT.FAILURE)


    def test_metadata_when_study_and_samples_dont_match(self):
        irods_fpath = "/humgen/projects/serapis_staging/test-metacheck/test_samples_given_wrong_study.cram"
        result = api.check_metadata_fetched_by_path(irods_fpaths=[irods_fpath], reference='grch38')
        for fpath, check_results in result.items():
            for check_res in check_results:
                if check_res.check_name in [
                    CHECK_NAMES.check_studies_in_irods_with_studies_in_seqscape_fetched_by_samples,
                    CHECK_NAMES.check_for_samples_in_more_studies,
                    CHECK_NAMES.check_samples_in_irods_same_as_samples_fetched_by_study_from_seqscape,
                    CHECK_NAMES.check_there_is_ss_irods_group,
                    CHECK_NAMES.check_ss_irods_group_read_permission,
                    CHECK_NAMES.check_attribute_count
                    ]:
                    self.assertEqual(check_res.result, RESULT.FAILURE)
                else:
                    self.assertEqual(check_res.result, RESULT.SUCCESS)


    def test_metadata_when_header_doesnt_match_irods(self):
        irods_fpath = "/humgen/projects/serapis_staging/test-metacheck/test_wrong_header.cram"
        result = api.check_metadata_fetched_by_path(irods_fpaths=[irods_fpath], reference='grch38')
        for fpath, check_results in result.items():
            for check_res in check_results:
                if check_res.check_name in [
                    CHECK_NAMES.check_there_is_ss_irods_group,
                    CHECK_NAMES.check_ss_irods_group_read_permission,
                    CHECK_NAMES.check_irods_ids_compared_to_header_ids,
                    CHECK_NAMES.check_header_ids_compared_to_irods_ids,
                    CHECK_NAMES.check_header_ids_compared_to_seqscape_ids,
                    CHECK_NAMES.check_seqscape_ids_compared_to_header_ids,
                    CHECK_NAMES.check_for_samples_in_more_studies,
                    CHECK_NAMES.check_attribute_count
                    ]:
                    self.assertEqual(check_res.result, RESULT.FAILURE)
                else:
                    self.assertEqual(check_res.result, RESULT.SUCCESS)

    def test_when_md5_is_wrong(self):
        irods_fpath = "/humgen/projects/serapis_staging/test-metacheck/test_wrong_md5.out"
        result = api.check_metadata_fetched_by_path(irods_fpaths=[irods_fpath], reference='grch38')
        for fpath, check_results in result.items():
            for check_res in check_results:
                if check_res.check_name in [
                    CHECK_NAMES.check_there_is_ss_irods_group,
                    CHECK_NAMES.check_ss_irods_group_read_permission,
                    CHECK_NAMES.check_for_samples_in_more_studies,
                    CHECK_NAMES.check_replica_checksum_valid,
                    CHECK_NAMES.check_more_than_one_replica,
                    CHECK_NAMES.check_by_comparison_checksum_in_meta_with_checksum_at_upload,
                    CHECK_NAMES.check_attribute_count
                    ]:
                    self.assertEqual(check_res.result, RESULT.FAILURE)
                else:
                    if check_res.executed:
                        self.assertEqual(check_res.result, RESULT.SUCCESS)
                    else:
                        self.assertIsNone(check_res.result)


    def test_when_more_than_1_md5s(self):
        irods_fpath = "/humgen/projects/serapis_staging/test-metacheck/test_more_than_one_md5s.out"
        result = api.check_metadata_fetched_by_path(irods_fpaths=[irods_fpath], reference='grch38')
        for fpath, check_results in result.items():
            for check_res in check_results:
                if check_res.check_name in [
                    CHECK_NAMES.check_there_is_ss_irods_group,
                    CHECK_NAMES.check_ss_irods_group_read_permission,
                    CHECK_NAMES.check_for_samples_in_more_studies,
                    CHECK_NAMES.check_more_than_one_replica,
                    CHECK_NAMES.check_by_comparison_checksum_in_meta_with_checksum_at_upload
                    ]:
                    self.assertEqual(check_res.result, RESULT.FAILURE)
                else:
                    if check_res.executed:
                        if check_res.check_name == CHECK_NAMES.check_attribute_count:
                            self.assertEqual(check_res.result, RESULT.FAILURE)
                        else:
                            self.assertEqual(check_res.result, RESULT.SUCCESS)
                    else:
                        self.assertIsNone(check_res.result)


@unittest.skip
class MetadataFetchedByMetadataTest(unittest.TestCase):

    def test_fetch_study_by_metadata(self):
        result = api.check_metadata_fetched_by_metadata(filter_target="1", filter_npg_qc="1", file_types="cram",
                                           study_name="SEQCAP_WGS_GDAP_AADM", irods_zone='seq')
        for fpath, check_results in result.items():
            for check_res in check_results:
                # if check_res.check_name == CHECK_NAMES.check_for_samples_in_more_studies:
                #     self.assertEqual(check_res.result, RESULT.FAILURE)
                # Added the second condition because some files from this study fail that check, others pass. Can't distinguish between the 2.
                if check_res.executed and check_res.check_name != CHECK_NAMES.check_for_samples_in_more_studies:
                    self.assertEqual(check_res.result, RESULT.SUCCESS)
                # else:
                #     print(check_res)
                #     self.assertTrue(False)


@unittest.skip
class ComparisonTests(unittest.TestCase):

    def test_same_check_results_by_path_and_by_metadata(self):
        fpath = '/humgen/projects/serapis_staging/test-metacheck/test_metadata_comparison.cram'
        check_results_by_metadata = api.check_metadata_fetched_by_metadata(reference='GRCh38', study_name='GDAP_XTEN', irods_zone='humgen')
        check_results_by_path = api.check_metadata_fetched_by_path(irods_fpaths=[fpath], reference='GRCh38')

        file_check_results_by_meta = check_results_by_metadata[fpath]
        file_check_results_by_path = check_results_by_path[fpath]

        def find_check_in_list(check_list, check_searched_name):
            for check in check_list:
                if check.check_name == check_searched_name:
                    return check
            return None

        for check_result in file_check_results_by_meta:
            check_by_path = find_check_in_list(file_check_results_by_path, check_result.check_name)
            self.assertEqual(check_result, check_by_path)

        self.assertEqual(len(file_check_results_by_path), len(file_check_results_by_meta))


    @patch('mcheck.main.api.sys.stdin.read')
    def test_fetch_study_metadata_vs_stream_study_metadata(self, stdin):
        fpath = "/nfs/users/nfs_i/ic4/Projects/python3/meta-check/aadm6.json"
        stdin.return_value = open(fpath).read()
        result_stream_metadata = api.check_metadata_given_as_json_stream()

        result_fetch_by_metadata = api.check_metadata_fetched_by_metadata(filter_npg_qc=1, filter_target=1,
                                                             study_name='SEQCAP_WGS_GDAP_AADM', irods_zone='seq')

        self.assertSetEqual(set(result_stream_metadata.keys()), set(result_fetch_by_metadata.keys()))
        for fpath, results in result_fetch_by_metadata.items():
            self.assertSetEqual(set(results), set(result_stream_metadata[fpath]))


    @patch('mcheck.main.api.sys.stdin.read')
    def test_fetch_study_metadata_vs_stream_study_metadata(self, stdin):
        fpath = "/nfs/users/nfs_i/ic4/Projects/python3/meta-check/cffdna.json"
        stdin.return_value = open(fpath).read()
        result_stream_metadata = api.check_metadata_given_as_json_stream()
        result_fetch_by_metadata = api.check_metadata_fetched_by_metadata(filter_npg_qc=1, filter_target=1,
                                                             study_name='De novo mutations in cell-free foetal DNA (cffDNA)', irods_zone='seq')

        self.assertSetEqual(set(result_stream_metadata.keys()), set(result_fetch_by_metadata.keys()))
        for fpath, results in result_fetch_by_metadata.items():
            self.assertSetEqual(set(results), set(result_stream_metadata[fpath]))


    @patch('mcheck.main.api.sys.stdin.read')
    def test_fetch_study_metadata_vs_stream_study_metadata(self, stdin):
        fpath = "/nfs/users/nfs_i/ic4/Projects/python3/meta-check/16006_5.json"
        stdin.return_value = open(fpath).read()
        result_fetch_by_metadata = api.check_metadata_fetched_by_path(irods_fpaths=['/seq/16006/16006_5.cram'])
        result_stream_metadata = api.check_metadata_given_as_json_stream()

        self.assertSetEqual(set(result_stream_metadata.keys()), set(result_fetch_by_metadata.keys()))
        print()
        for fpath, results in result_fetch_by_metadata.items():
            self.assertSetEqual(set(results), set(result_stream_metadata[fpath]))
