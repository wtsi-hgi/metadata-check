"""
Copyright (C) 2015  Genome Research Ltd.

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

This file has been created on Feb 10, 2015.
"""

import unittest
from main import utils


class TestUtils(unittest.TestCase):

    def test_get_diff_irods_and_header_metadata(self):
        header_dict = {'name': ['491STDY5478742']}
        irods_dict = {'name': ['123STUDY']}
        result = utils.get_diff_irods_and_header_metadata(header_dict, irods_dict)
        self.assertEqual(len(result), 1)

        header_dict = {'accession_number': ['EGAN00001218652']}
        irods_dict = {'accession_number': ['EGAN00001218652']}
        result = utils.get_diff_irods_and_header_metadata(header_dict, irods_dict)
        self.assertEqual(len(result), 0)

        header_dict = {'accession_number': ['EGAN00001218652']}
        irods_dict = {'accession_number': ['EGAN00001218652'], 'name': ['491STDY5478742']}
        result = utils.get_diff_irods_and_header_metadata(header_dict, irods_dict)
        self.assertEqual(len(result), 1)

        header_dict = {'accession_number': [], 'name': ['SC_WES_INT5899561']}
        irods_dict = {'accession_number': ['EGAN00001218652'], 'name': ['SC_WES_INT5899561']}
        result = utils.get_diff_irods_and_header_metadata(header_dict, irods_dict)
        self.assertEqual(len(result), 0)


    def test_check_all_identifiers_in_metadata(self):
        metadata = {'name': ['aaa'], 'internal_id': [1,2,3]}
        expected = []
        result = utils.check_all_identifiers_in_metadata(metadata, accession_number=False)
        self.assertEqual(expected, result)

        metadata = {'name': ['aaa'], 'internal_id': [1,2,3], 'accession_number': []}
        expected = []
        result = utils.check_all_identifiers_in_metadata(metadata, accession_number=False)
        self.assertEqual(expected, result)

        metadata = {'name': ['aaa'], 'internal_id': [1,2,3], 'accession_number': ['EGA123']}
        expected = []
        result = utils.check_all_identifiers_in_metadata(metadata, accession_number=False)
        self.assertEqual(expected, result)

        metadata = {'name': ['aaa'], 'internal_id': [1,2,3], 'accession_number': []}
        expected = []
        result = utils.check_all_identifiers_in_metadata(metadata, accession_number=False)
        self.assertEqual(expected, result)


    def test_get_run_from_irods_path(self):
        # Testing for a normal path:
        path = '/seq/1234/1234_3#12.bam'
        result = utils.get_run_from_irods_path(path)
        expected = '1234'
        self.assertEqual(result, expected)

        path = '/seq/11000/11000_2#3.bam'
        result = utils.get_run_from_irods_path(path)
        expected = '11000'
        self.assertEqual(result, expected)

        # Testing that it doesn't crash if a random thing is given:
        path = '/a/random/path'
        result = utils.get_run_from_irods_path(path)
        expected = ''
        self.assertEqual(result, expected)

        path = 'pathwithout_slashes'
        result = utils.get_run_from_irods_path(path)
        expected = ''
        self.assertEqual(result, expected)


    def test_get_lane_from_irods_path(self):
        # Testing it works with normal irods path:
        path = '/seq/1234/1234_3#1.bam'
        result = utils.get_lane_from_irods_path(path)
        expected = '3'
        self.assertEqual(result, expected)

        path = '/seq/1234/12345_6#7.bam'
        result = utils.get_lane_from_irods_path(path)
        expected = '6'
        self.assertEqual(result, expected)

        # Testing it works on a lane-level BAM:
        path = '/seq/1234/1234_5.bam'
        result = utils.get_lane_from_irods_path(path)
        expected = '5'
        self.assertEqual(result, expected)

        # Testing it works on abnormal params:
        path = '/seq/'
        result = utils.get_lane_from_irods_path(path)
        expected = ''
        self.assertEqual(result, expected)

        path = 'a_random_path'
        result = utils.get_lane_from_irods_path(path)
        expected = ''
        self.assertEqual(result, expected)

        # Testing that it returns '' on an empty path
        path = ''
        result = utils.get_lane_from_irods_path(path)
        expected = ''
        self.assertEqual(result, expected)

        # Testing it returns '' on a path from diff. zone:
        path = '/humgen/projects/hgi/SRP123.bam'
        result = utils.get_lane_from_irods_path(path)
        expected = ''
        self.assertEqual(result, expected)



    def test_extract_reference_name_from_path(self):
        # Testing that it works on the normal case:
        ref_path = '/lustre/scratch110/srpipe/references/Homo_sapiens/1000Genomes_hs37d5/all/bwa/hs37d5.fa'
        result = utils.extract_reference_name_from_path(ref_path)
        expected = 'hs37d5'
        self.assertEqual(result, expected)

        # Testing on a different reference - again normal case, should work:
        ref_path = '/lustre/scratch110/srpipe/references/Homo_sapiens/GRCh38_15/all/bwa/Homo_sapiens.GRCh38_15.fa'
        result = utils.extract_reference_name_from_path(ref_path)
        expected = 'Homo_sapiens.GRCh38_15'
        self.assertEqual(result, expected)

        # Testing that it returns '' if the path is not a reference:
        ref_path = '/lustre/scratch110/srpipe/references/Homo_sapiens/GRCh38_15/all/bwa/Homo_sapiens'
        result = utils.extract_reference_name_from_path(ref_path)
        expected = ''
        self.assertEqual(result, expected)


    def test_extract_lanelet_name_from_irods_fpath(self):
        # Testing on a normal lanelet:
        irods_fpath = '/seq/1234/1234_5#6.bam'
        result = utils.extract_lanelet_name_from_irods_fpath(irods_fpath)
        expected = '1234_5#6'
        self.assertEqual(result, expected)

        # Testing for a lane-level bam:
        irods_fpath = '/seq/1234/1234_5.bam'
        result = utils.extract_lanelet_name_from_irods_fpath(irods_fpath)
        expected = '1234_5'
        self.assertEqual(result, expected)

        # Testing on a non-standard path - should return ''
        irods_fpath = '/humgen/projectscrohns/1234SRA.bam'
        result = utils.extract_lanelet_name_from_irods_fpath(irods_fpath)
        expected = ''
        self.assertEqual(result, expected)

