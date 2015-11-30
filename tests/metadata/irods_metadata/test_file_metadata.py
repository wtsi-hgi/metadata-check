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

This file has been created on Jun 26, 2015.
"""

import unittest

from metadata.irods_metadata.file_metadata import IrodsSeqFileMetadata
#from main import error_types
from results.constants import RESULT


class TestIrodsSeqFileMetadata(unittest.TestCase):

    def test_extract_reference_name_from_ref_path1(self):
        ref_path = '/lustre/scratch109/srpipe/references/Homo_sapiens/1000Genomes_hs37d5/all/bwa/hs37d5.fa'
        result = IrodsSeqFileMetadata.extract_reference_name_from_ref_path(ref_path)
        self.assertEqual(result, 'hs37d5')

    def test_extract_reference_name_from_ref_path2(self):
        ref_path = '/lustre/scratch110/srpipe/references/Homo_sapiens/1000Genomes/all/bwa/human_g1k_v37.fasta'
        result = IrodsSeqFileMetadata.extract_reference_name_from_ref_path(ref_path)
        self.assertEqual(result, 'human_g1k_v37')

    def test_extract_reference_name_from_ref_path3(self):
        ref_path = '/lustre/scratch109/srpipe/references/Homo_sapiens/GRCh38_15/all/bwa0_6/Homo_sapiens.GRCh38_15.fa'
        result = IrodsSeqFileMetadata.extract_reference_name_from_ref_path(ref_path)
        self.assertEqual(result, 'Homo_sapiens.GRCh38_15')

    def test_extract_reference_name_from_ref_path4(self):
        ref_path = '/lustre/scratch110/srpipe/references/Homo_sapiens/GRCh37_53/all/bwa/Homo_sapiens.GRCh37.dna.all.fa'
        result = IrodsSeqFileMetadata.extract_reference_name_from_ref_path(ref_path)
        self.assertEqual(result, 'Homo_sapiens.GRCh37.dna.all')

    def test_extract_reference_name_from_ref_path5(self):
        ref_path = '/lustre/scratch110/srpipe/references/Homo_sapiens/GRCh37_53/all/bwa/Homo_sapiens.bam'
        self.assertRaises(ValueError, IrodsSeqFileMetadata.extract_reference_name_from_ref_path, ref_path)


    def test_is_checksum_valid_1(self):
        checksum = 'abcdref123asssssdaf'
        result = IrodsSeqFileMetadata._is_checksum_valid(checksum)
        self.assertTrue(result)

    def test_is_checksum_valid_2(self):
        checksum = 'abcdref123asssssdafAAA'
        result = IrodsSeqFileMetadata._is_checksum_valid(checksum)
        self.assertFalse(result)

    def test_is_checksum_valid_3(self):
        checksum = ''
        result = IrodsSeqFileMetadata._is_checksum_valid(checksum)
        self.assertFalse(result)

    def test_is_checksum_valid_4(self):
        checksum = '123'
        result = IrodsSeqFileMetadata._is_checksum_valid(checksum)
        self.assertTrue(result)

    def test_is_checksum_valid_5(self):
        checksum = 'AAA'
        result = IrodsSeqFileMetadata._is_checksum_valid(checksum)
        self.assertFalse(result)

    def test_is_checksum_valid_6(self):
        checksum = 123
        self.assertRaises(TypeError, IrodsSeqFileMetadata._is_checksum_valid, checksum)


    #
    # @classmethod
    # def is_run_id(cls, run_id):
    #     r = re.compile(irods_consts.RUN_ID_REGEX)
    #     return True if r.match(run_id) else False
    #

    def test_is_run_id_valid_1(self):
        run_id = '1234'
        result = IrodsSeqFileMetadata._is_run_id_valid(run_id)
        self.assertTrue(result)

    def test_is_run_id_valid_2(self):
        run_id = '1'
        result = IrodsSeqFileMetadata._is_run_id_valid(run_id)
        self.assertFalse(result)

    def test_is_run_id_valid_3(self):
        run_id = 'aaa'
        result = IrodsSeqFileMetadata._is_run_id_valid(run_id)
        self.assertFalse(result)

    def test_is_run_id_valid_4(self):
        run_id = '12345'
        result = IrodsSeqFileMetadata._is_run_id_valid(run_id)
        self.assertTrue(result)

    def test_is_run_id_valid_5(self):
        run_id = True
        self.assertRaises(TypeError, IrodsSeqFileMetadata._is_run_id_valid, run_id)


    # @classmethod
    # def is_lane_id(cls, lane_id):
    #     r = re.compile(irods_consts.LANE_ID_REGEX)
    #     return True if r.match(lane_id) else False
    #
    def test_is_lane_id_valid_1(self):
        lane_id = 1
        result = IrodsSeqFileMetadata._is_lane_id_valid(lane_id)
        self.assertTrue(result)

    def test_is_lane_id_valid_2(self):
        lane_id = '1'
        result = IrodsSeqFileMetadata._is_lane_id_valid(lane_id)
        self.assertTrue(result)

    def test_is_lane_id_valid_3(self):
        lane_id = False
        self.assertRaises(TypeError, IrodsSeqFileMetadata._is_lane_id_valid, lane_id)

    def test_is_lane_id_valid_4(self):
        lane_id = '123'
        result = IrodsSeqFileMetadata._is_lane_id_valid(lane_id)
        self.assertFalse(result)

    def test_is_lane_id_valid_5(self):
        lane_id = '123aaaa'
        result = IrodsSeqFileMetadata._is_lane_id_valid(lane_id)
        self.assertFalse(result)



    def test_is_npg_qc_valid_1(self):
        npq_qc = 1
        result = IrodsSeqFileMetadata._is_npg_qc_valid(npq_qc)
        self.assertTrue(result)

    def test_is_npg_qc_valid_2(self):
        npq_qc = 4
        result = IrodsSeqFileMetadata._is_npg_qc_valid(npq_qc)
        self.assertFalse(result)

    def test_is_npg_qc_valid_3(self):
        npq_qc = "1"
        result = IrodsSeqFileMetadata._is_npg_qc_valid(npq_qc)
        self.assertTrue(result)

    def test_is_npg_qc_valid_4(self):
        npq_qc = "0"
        result = IrodsSeqFileMetadata._is_npg_qc_valid(npq_qc)
        self.assertTrue(result)

    def test_is_npg_qc_valid_5(self):
        npq_qc = 123
        result = IrodsSeqFileMetadata._is_npg_qc_valid(npq_qc)
        self.assertFalse(result)

    def test_is_npg_qc_valid_6(self):
        npq_qc = "mamba"
        result = IrodsSeqFileMetadata._is_npg_qc_valid(npq_qc)
        self.assertFalse(result)

    def test_is_npg_qc_valid_7(self):
        npq_qc = True
        self.assertRaises(TypeError, IrodsSeqFileMetadata._is_npg_qc_valid, npq_qc)




    def test_check_checksum_calculated_vs_metadata_1(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.bam', fname='1234_5#6.bam', checksum_in_meta='123abc', checksum_at_upload='123abc')
        result = irods_metadata.check_checksum_calculated_vs_metadata()
        self.assertEqual(len(result), 0)

    def test_check_checksum_calculated_vs_metadata_2(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.bam',fname='1234_5#6.bam', checksum_in_meta='123abc123', checksum_at_upload='123abc')
        result = irods_metadata.check_checksum_calculated_vs_metadata()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].result, RESULT.FAILURE)

    def test_check_checksum_calculated_vs_metadata_3(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.bam', fname='1234_5#6.bam', checksum_in_meta='123abc')
        result = irods_metadata.check_checksum_calculated_vs_metadata()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].executed, False)

    def test_check_checksum_calculated_vs_metadata_4(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.bam', fname='1234_5#6.bam', checksum_at_upload='123abc')
        result = irods_metadata.check_checksum_calculated_vs_metadata()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].executed, False)




    def test_validate_fields_1(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.bam', fname='1234_5#6.bam', checksum_in_meta='aaAAA')
        result = irods_metadata.validate_fields()
        self.assertEqual(len(result) , 1)

    def test_validate_fields_2(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.bam', fname='1234_5#6.bam', run_ids=['aaAAA'])
        result = irods_metadata.validate_fields()
        self.assertEqual(len(result) , 1)

    def test_validate_fields_3(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.bam', fname='1234_5#6.bam', lane_ids=['aaAAA'])
        result = irods_metadata.validate_fields()
        self.assertEqual(len(result) , 1)

    def test_validate_fields_4(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.bam', fname='1234_5#6.bam', npg_qc='aaAAA')
        result = irods_metadata.validate_fields()
        self.assertEqual(len(result) , 1)


    def test_check_reference_1(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.cram', fname='1234_5#6.cram', references=['/lustre/hs37d5.fa'])
        result = irods_metadata.check_reference('hs37d5')
        self.assertEqual(result, [])

    def test_check_reference_2(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.cram', fname='1234_5#6.cram', references=['/lustre/hs37d5.fa'])
        result = irods_metadata.check_reference('')
        self.assertEqual(len(result), 1)

    def test_check_reference_3(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.cram', fname='1234_5#6.cram')
        result = irods_metadata.check_reference('')
        self.assertEqual(len(result), 2)



