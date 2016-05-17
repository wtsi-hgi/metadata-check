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

from mcheck.main import metadata_utils
from unittest import skip

@skip
class TestUtils(unittest.TestCase):


    def test_get_run_from_irods_path(self):
        # Testing for a normal path:
        path = '/seq/1234/1234_3#12.bam'
        result = metadata_utils.iRODSiCmdsUtils.get_run_from_irods_path(path)
        expected = '1234'
        self.assertEqual(result, expected)

        path = '/seq/11000/11000_2#3.bam'
        result = metadata_utils.iRODSiCmdsUtils.get_run_from_irods_path(path)
        expected = '11000'
        self.assertEqual(result, expected)

        # Testing that it doesn't crash if a random thing is given:
        path = '/a/random/path'
        result = metadata_utils.iRODSiCmdsUtils.get_run_from_irods_path(path)
        expected = ''
        self.assertEqual(result, expected)

        path = 'pathwithout_slashes'
        result = metadata_utils.iRODSiCmdsUtils.get_run_from_irods_path(path)
        expected = ''
        self.assertEqual(result, expected)


    def test_get_lane_from_irods_path(self):
        # Testing it works with normal irods path:
        path = '/seq/1234/1234_3#1.bam'
        result = metadata_utils.iRODSiCmdsUtils.get_lane_from_irods_path(path)
        expected = '3'
        self.assertEqual(result, expected)

        path = '/seq/1234/12345_6#7.bam'
        result = metadata_utils.iRODSiCmdsUtils.get_lane_from_irods_path(path)
        expected = '6'
        self.assertEqual(result, expected)

        # Testing it works on a lane-level BAM:
        path = '/seq/1234/1234_5.bam'
        result = metadata_utils.iRODSiCmdsUtils.get_lane_from_irods_path(path)
        expected = '5'
        self.assertEqual(result, expected)

        # Testing it works on abnormal params:
        path = '/seq/'
        result = metadata_utils.iRODSiCmdsUtils.get_lane_from_irods_path(path)
        expected = ''
        self.assertEqual(result, expected)

        path = 'a_random_path'
        self.assertRaises(NameError, metadata_utils.iRODSiCmdsUtils.get_lane_from_irods_path, path)
        self.assertEqual(result, expected)

        # Testing that it returns '' on an empty path
        path = ''
        result = metadata_utils.iRODSiCmdsUtils.get_lane_from_irods_path(path)
        expected = ''
        self.assertEqual(result, expected)

        # Testing it returns '' on a path from diff. zone:
        path = '/humgen/projects/hgi/SRP123.bam'
        result = metadata_utils.iRODSiCmdsUtils.get_lane_from_irods_path(path)
        expected = ''
        self.assertEqual(result, expected)



    def test_extract_reference_name_from_path(self):
        # Testing that it works on the normal case:
        ref_path = '/lustre/scratch110/srpipe/references/Homo_sapiens/1000Genomes_hs37d5/all/bwa/hs37d5.fa'
        result = metadata_utils.iRODSiCmdsUtils.extract_reference_name_from_path(ref_path)
        expected = 'hs37d5'
        self.assertEqual(result, expected)

        # Testing on a different reference - again normal case, should work:
        ref_path = '/lustre/scratch110/srpipe/references/Homo_sapiens/GRCh38_15/all/bwa/Homo_sapiens.GRCh38_15.fa'
        result = metadata_utils.iRODSiCmdsUtils.extract_reference_name_from_path(ref_path)
        expected = 'Homo_sapiens.GRCh38_15'
        self.assertEqual(result, expected)

        # Testing that it returns '' if the path is not a reference:
        ref_path = '/lustre/scratch110/srpipe/references/Homo_sapiens/GRCh38_15/all/bwa/Homo_sapiens'
        result = metadata_utils.iRODSiCmdsUtils.extract_reference_name_from_path(ref_path)
        expected = ''
        self.assertEqual(result, expected)


    def test_extract_lanelet_name_from_irods_fpath(self):
        # Testing on a normal lanelet:
        irods_fpath = '/seq/1234/1234_5#6.bam'
        result = metadata_utils.iRODSiCmdsUtils.extract_lanelet_name_from_irods_fpath(irods_fpath)
        expected = '1234_5#6'
        self.assertEqual(result, expected)

        # Testing for a lane-level bam:
        irods_fpath = '/seq/1234/1234_5.bam'
        result = metadata_utils.iRODSiCmdsUtils.extract_lanelet_name_from_irods_fpath(irods_fpath)
        expected = '1234_5'
        self.assertEqual(result, expected)

        # Testing on a non-standard path - should return ''
        irods_fpath = '/humgen/projectscrohns/1234SRA.bam'
        result = metadata_utils.iRODSiCmdsUtils.extract_lanelet_name_from_irods_fpath(irods_fpath)
        expected = ''
        self.assertEqual(result, expected)

