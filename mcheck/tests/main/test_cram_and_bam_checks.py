"""
Copyright (C) 2014  Genome Research Ltd.

Author: Irina Colgiu <ic4@sanger.ac.uk>

This program is part of metadata-check

metadata-check is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.
You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

This file has been created on Dec 11, 2014.
"""

import unittest

from main import cram_and_bam_checks
from mcheck.main import constants


class TestBamChecks(unittest.TestCase):

    def test_check_irods_vs_header_metadata(self):
        header_dict = {'name': ['491STDY5478742']}
        irods_dict = {'name': ['123STUDY']}
        result = cram_and_bam_checks.check_irods_vs_header_metadata('unimp', header_dict, irods_dict, 'study')
        self.assertEqual(len(result), 1)

        header_dict = {'accession_number': ['EGAN00001218652']}
        irods_dict = {'accession_number': ['EGAN00001218652']}
        result = cram_and_bam_checks.check_irods_vs_header_metadata('unimp', header_dict, irods_dict, 'sample')
        self.assertEqual(len(result), 0)

        # This tests that it's ok even if the irods metadata is a superset of header,
        header_dict = {'accession_number': ['EGAN00001218652']}
        irods_dict = {'accession_number': ['EGAN00001218652'], 'name': ['491STDY5478742']}
        result = cram_and_bam_checks.check_irods_vs_header_metadata('unimp', header_dict, irods_dict, 'study')
        self.assertEqual(len(result), 0)

        header_dict = {'accession_number': [], 'name': ['SC_WES_INT5899561']}
        irods_dict = {'accession_number': ['EGAN00001218652'], 'name': ['SC_WES_INT5899561']}
        result = cram_and_bam_checks.check_irods_vs_header_metadata('unimp', header_dict, irods_dict, 'sample')
        self.assertEqual(len(result), 0)


    # def test_check_all_identifiers_in_metadata(self):
    #     metadata = {'name': ['aaa'], 'internal_id': [1,2,3]}
    #     expected = []
    #     result = cram_and_bam_checks.check_all_identifiers_in_metadata(metadata, accession_number=False)
    #     self.assertEqual(expected, result)
    #
    #     metadata = {'name': ['aaa'], 'internal_id': [1,2,3], 'accession_number': []}
    #     expected = []
    #     result = cram_and_bam_checks.check_all_identifiers_in_metadata(metadata, accession_number=False)
    #     self.assertEqual(expected, result)
    #
    #     metadata = {'name': ['aaa'], 'internal_id': [1,2,3], 'accession_number': ['EGA123']}
    #     expected = []
    #     result = cram_and_bam_checks.check_all_identifiers_in_metadata(metadata, accession_number=False)
    #     self.assertEqual(expected, result)
    #
    #     metadata = {'name': ['aaa'], 'internal_id': [1,2,3], 'accession_number': []}
    #     expected = []
    #     result = cram_and_bam_checks.check_all_identifiers_in_metadata(metadata, accession_number=False)
    #     self.assertEqual(expected, result)


    def test_check_same_files_by_diff_study_ids(self):
        study_name = 'GDAP_XTEN'
        study_id = "3257"
        study_acc_nr = 'EGAS00001000929'

        result = cram_and_bam_checks.check_same_files_by_diff_study_ids(study_name, study_id, study_acc_nr)
        self.assertEqual(result, [])

        study_name = 'IHTP_MWGS_Papuan_Genomes'
        study_id = 3644
        study_acc_nr = 'EGAS00001001247'
        result = cram_and_bam_checks.check_same_files_by_diff_study_ids(study_name, study_id, study_acc_nr)
        print("ERROR: " + str(result))
        #self.assertEqual(result, [])


# def check_same_files_by_diff_study_ids(name, internal_id, acc_nr):
#     files_by_name = set(collect_fpaths_by_study_name(name))
#     files_by_acc_nr = set(collect_fpaths_by_study_accession_nr(acc_nr))
#     files_by_id = set(collect_fpaths_by_study_internal_id(internal_id))
#
#     problems = []
#     if files_by_name != files_by_acc_nr:
#         diffs = files_by_name.difference(files_by_acc_nr)
#         if diffs:
#             problems.append(error_types.DifferentFilesRetrievedByDiffStudyIdsOfSameStudy(diffs, 'name', 'accession_number'))
#
#         diffs = files_by_acc_nr.difference(files_by_name)
#         if diffs:
#             problems.append(error_types.DifferentFilesRetrievedByDiffStudyIdsOfSameStudy(diffs, 'accession_number', 'name'))
#
#     if files_by_name != files_by_id:
#         diffs = files_by_name.difference(files_by_id)
#         if diffs:
#             problems.append(error_types.DifferentFilesRetrievedByDiffStudyIdsOfSameStudy(diffs, 'name', 'internal_id'))
#
#         diffs = files_by_id.difference(files_by_name)
#         if diffs:
#             problems.append(error_types.DifferentFilesRetrievedByDiffStudyIdsOfSameStudy(diffs, 'internal_id', 'name'))
#
#     if files_by_acc_nr != files_by_id:
#         diffs = files_by_id.difference(files_by_acc_nr)
#         if diffs:
#             problems.append(error_types.DifferentFilesRetrievedByDiffStudyIdsOfSameStudy(diffs, 'internal_id', 'accession_number'))
#
#         diffs = files_by_acc_nr.difference(files_by_id)
#         if diffs:
#             problems.append(error_types.DifferentFilesRetrievedByDiffStudyIdsOfSameStudy(diffs, 'accession_number', 'internal_id'))
#     return problems
#


    def test_filter_by_file_type1(self):
        fpaths = ['/seq/1/2.bam', '/seq/1/2.cram']
        result = cram_and_bam_checks.filter_by_file_type(fpaths, constants.BAM_FILE_TYPE)
        self.assertEqual(len(result), 1)


    def test_filter_by_file_type2(self):
        fpaths = ['/seq/1/2.bam', '/seq/1/2.cram']
        result = cram_and_bam_checks.filter_by_file_type(fpaths, constants.CRAM_FILE_TYPE)
        self.assertEqual(len(result), 1)


# def filter_by_file_type(fpaths, file_type):
#     return [f for f in fpaths if f.endswith(file_type)]
