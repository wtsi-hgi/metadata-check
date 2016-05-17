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

This file has been created on Feb 11, 2015.
"""

import unittest

import config
from mcheck.main import irods_seq_data_tests as irods_seq_tests
from mcheck.main import error_types
from mcheck.metadata.irods_metadata import avu


@unittest.skip
class MD5Test(unittest.TestCase):

    @unittest.skipIf(config.RUNNING_LOCATION == 'localhost', "Skipping checksum test because it runs locally")
    def test_check_bam_md5_metadata(self):
        irods_fpath = '/seq/14761/14761_4.bam'
        irods_metadata = [avu.MetaAVU(attribute='md5', value='df8afb9196ea7080cd261e65d4ab2ef9')]
        result = irods_seq_tests.check_md5_metadata(irods_fpath, irods_metadata)
        print(result)
        self.assertEqual(len(result), 1)

    @unittest.skipIf(config.RUNNING_LOCATION == 'localhost', "Skipping checksum test because it runs locally")
    def test_check_cram_md5_metadata(self):
        irods_fpath = '/seq/14761/14761_4.cram'
        irods_metadata = [avu.MetaAVU(attribute='md5', value='a58d8e78d5d7a2a55136448a81c5dd90')]
        result = irods_seq_tests.check_md5_metadata(irods_fpath, irods_metadata)
        self.assertEqual(len(result), 0)

@unittest.skip
class AdjancentMetadataChecksTests(unittest.TestCase):

    def test_check_bam_run_id(self):
        # Testing it works for normal cases:
        irods_metadata = [avu.MetaAVU('id_run', '11000')]
        irods_fpath = '/seq/11000/11000_2#3.bam'
        result = irods_seq_tests.check_run_id(irods_fpath, irods_metadata)
        expected = []
        self.assertEqual(result, expected)

        # Testing that it returns an error if there is no run id in the metadata:
        irods_metadata = []
        irods_fpath = '/seq/11000/11000_2#3.bam'
        result = irods_seq_tests.check_run_id(irods_fpath, irods_metadata)
        self.assertEqual(len(result), 1)

        # Testing that it returns an error message if there is more than 1 run in the metadata:
        irods_metadata = [avu.MetaAVU('id_run', '11000'), avu.MetaAVU('id_run', '11111')]
        irods_fpath = '/seq/11000/11000_2#3.bam'
        result = irods_seq_tests.check_run_id(irods_fpath, irods_metadata)
        self.assertEqual(len(result), 1)

        # Testing that it returns an error message if the irods path doesn't look like expected:
        irods_metadata = [avu.MetaAVU('id_run', '11000')]
        irods_fpath = '/humgen/projects/hgi/11000_2#3.bam'
        result = irods_seq_tests.check_run_id(irods_fpath, irods_metadata)
        self.assertEqual(len(result), 1)

    def test_check_cram_run_id(self):
        # Testing it works for normal cases:
        irods_metadata = [avu.MetaAVU('id_run', '11000')]
        irods_fpath = '/seq/11000/11000_2#3.cram'
        result = irods_seq_tests.check_run_id(irods_fpath, irods_metadata)
        expected = []
        self.assertEqual(result, expected)

        # Testing that it returns an error if there is no run id in the metadata:
        irods_metadata = []
        irods_fpath = '/seq/11000/11000_2#3.cram'
        result = irods_seq_tests.check_run_id(irods_fpath, irods_metadata)
        self.assertEqual(len(result), 1)

        # Testing that it returns an error message if there is more than 1 run in the metadata:
        irods_metadata = [avu.MetaAVU('id_run', '11000'), avu.MetaAVU('id_run', '11111')]
        irods_fpath = '/seq/11000/11000_2#3.cram'
        result = irods_seq_tests.check_run_id(irods_fpath, irods_metadata)
        self.assertEqual(len(result), 1)

        # Testing that it returns an error message if the irods path doesn't look like expected:
        irods_metadata = [avu.MetaAVU('id_run', '11000')]
        irods_fpath = '/humgen/projects/hgi/11000_2#3.cram'
        result = irods_seq_tests.check_run_id(irods_fpath, irods_metadata)
        self.assertEqual(len(result), 1)



    def test_check_bam_lane_metadata(self):
        # Testing on a normal case - lanelet:
        irods_metadata = [avu.MetaAVU('lane', '1')]
        irods_fpath = '/seq/11111/11111_1#2.bam'
        result = irods_seq_tests.check_lane_metadata(irods_fpath, irods_metadata)
        expected = []
        self.assertEqual(result, expected)

        # Testing on a lane-level BAM:
        irods_metadata = [avu.MetaAVU('lane', '2')]
        irods_fpath = '/seq/11111/11111_2.bam'
        result = irods_seq_tests.check_lane_metadata(irods_fpath, irods_metadata)
        expected = []
        self.assertEqual(result, expected)

        # Testing that a message is returned if the irods path doesn't look normal:
        irods_metadata = [avu.MetaAVU('lane', '2')]
        irods_fpath = '/humgen/projects/hgi/SSS123.bam'
        result = irods_seq_tests.check_lane_metadata(irods_fpath, irods_metadata)
        self.assertEqual(len(result), 1)

        # Testing that a message is returned if there is no irods metadata:
        irods_metadata = []
        irods_fpath = '/seq/11111/11111_2.bam'
        result = irods_seq_tests.check_lane_metadata(irods_fpath, irods_metadata)
        self.assertEqual(len(result), 1)


    def test_check_cram_lane_metadata(self):
        # Testing on a normal case - lanelet:
        irods_metadata = [avu.MetaAVU('lane', '1')]
        irods_fpath = '/seq/11111/11111_1#2.cram'
        result = irods_seq_tests.check_lane_metadata(irods_fpath, irods_metadata)
        expected = []
        self.assertEqual(result, expected)

        # Testing on a lane-level BAM:
        irods_metadata = [avu.MetaAVU('lane', '2')]
        irods_fpath = '/seq/11111/11111_2.cram'
        result = irods_seq_tests.check_lane_metadata(irods_fpath, irods_metadata)
        expected = []
        self.assertEqual(result, expected)

        # Testing that a message is returned if the irods path doesn't look normal:
        irods_metadata = [avu.MetaAVU('lane', '2')]
        irods_fpath = '/humgen/projects/hgi/SSS123.cram'
        result = irods_seq_tests.check_lane_metadata(irods_fpath, irods_metadata)
        self.assertEqual(len(result), 1)

        # Testing that a message is returned if there is no irods metadata:
        irods_metadata = []
        irods_fpath = '/seq/11111/11111_2.cram'
        result = irods_seq_tests.check_lane_metadata(irods_fpath, irods_metadata)
        self.assertEqual(len(result), 1)


    def test_check_reference(self):
        # Testing on a normal case - the ref is not the desired one:
        irods_metadata = [avu.MetaAVU('reference', '/path/refs/GRCh38_15/all/bwa/Homo_sapiens.GRCh38_15.fa')]
        desired_ref = 'hs37d5'
        result = self.assertRaises(error_types.WrongReferenceError, irods_seq_tests.check_reference, '/seq/path/doesnt/matter.bam', irods_metadata, desired_ref)
        #self.assertEqual(len(result), 1)

        # Testing on a normal case - the ref is the desired one:
        irods_metadata = [avu.MetaAVU('reference', '/path/ref/Homo_sapiens/1000Genomes_hs37d5/all/bwa/hs37d5.fa')]
        desired_ref = 'hs37d5'
        result = irods_seq_tests.check_reference('/seq/path/doesnt/matter.bam', irods_metadata, desired_ref)
        self.assertEqual(len(result), 0)


    def test_check_bam_lanelet_name(self):
        # Testing on  a normal case:
        irods_fpath = '/seq/1234/1234_5#6.bam'
        header_lanelets = ['1234_5#6']
        result = irods_seq_tests.check_lanelet_name(irods_fpath, header_lanelets)
        expected = []
        self.assertEqual(result, expected)


    def test_check_cram_lanelet_name(self):
        # Testing on  a normal case:
        irods_fpath = '/seq/1234/1234_5#6.cram'
        header_lanelets = ['1234_5#6']
        result = irods_seq_tests.check_lanelet_name(irods_fpath, header_lanelets)
        expected = []
        self.assertEqual(result, expected)
