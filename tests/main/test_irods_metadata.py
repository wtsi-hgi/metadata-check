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
from main.irods_metadata import IrodsSeqFileMetadata
from main import error_types
from main import metadata_utils
from irods import data_types

class TestIrodsSeqFileMetadata(unittest.TestCase):

    def test_check_is_irods_seq_fpath1(self):
        path ='/seq/1234/1234_5.bam'
        result = IrodsSeqFileMetadata.check_is_irods_seq_fpath(path)
        self.assertIsNone(result)

    def test_check_is_irods_seq_fpath2(self):
        path = '/seq/12345/12345_6.bam'
        result = IrodsSeqFileMetadata.check_is_irods_seq_fpath(path)
        self.assertIsNone(result)

    def test_check_is_irods_seq_fpath3(self):
        path = '/seq/12345/12345_6#1.bam'
        result = IrodsSeqFileMetadata.check_is_irods_seq_fpath(path)
        self.assertIsNone(result)

    def test_check_is_irods_seq_fpath3(self):
        path = '/seq/12345/1_6.bam'
        self.assertRaises(ValueError, IrodsSeqFileMetadata.check_is_irods_seq_fpath, path)

    def test_check_is_irods_seq_fpath4(self):
        path = '/seq/1/12345_6.bam'
        self.assertRaises(ValueError, IrodsSeqFileMetadata.check_is_irods_seq_fpath, path)

    def test_check_is_irods_seq_fpath5(self):
        path = '/seq/12345/12345_6.bam'
        result = IrodsSeqFileMetadata.check_is_irods_seq_fpath(path)
        self.assertIsNone(result)

    def test_check_is_irods_seq_fpath6(self):
        path = '/seq/12345/12345_6#56.bam'
        result = IrodsSeqFileMetadata.check_is_irods_seq_fpath(path)
        self.assertIsNone(result)

    def test_check_is_irods_seq_fpath7(self):
        path = '/seq/12345/12345_56#56.bam'
        self.assertRaises(ValueError, IrodsSeqFileMetadata.check_is_irods_seq_fpath, path)

    def test_check_is_irods_seq_fpath8(self):
        path = 'something/seq/12345/12345_6#56.bam'
        self.assertRaises(ValueError, IrodsSeqFileMetadata.check_is_irods_seq_fpath, path)

    def test_check_is_irods_seq_fpath10(self):
        path = '/smthseq/12345/12345_6#56.bam'
        self.assertRaises(ValueError, IrodsSeqFileMetadata.check_is_irods_seq_fpath, path)

    def test_check_is_irods_seq_fpath11(self):
        path = '/smth/seq/12345/12345_6#56.bam'
        self.assertRaises(ValueError, IrodsSeqFileMetadata.check_is_irods_seq_fpath, path)

    def test_check_is_irods_seq_fpath12(self):
        path = '/seq/12345/12345_6#56.cram'
        result = IrodsSeqFileMetadata.check_is_irods_seq_fpath(path)
        self.assertIsNone(result)



    def test_check_is_lanelet_filename1(self):
        lanelet = '1234_5.bam'
        result = IrodsSeqFileMetadata.check_is_lanelet_filename(lanelet)
        self.assertIsNone(result)

    def test_check_is_lanelet_filename2(self):
        lanelet = '1234_5#6.bam'
        result = IrodsSeqFileMetadata.check_is_lanelet_filename(lanelet)
        self.assertIsNone(result)

    def test_check_is_lanelet_filename3(self):
        lanelet = '1234_5#56.bam'
        result = IrodsSeqFileMetadata.check_is_lanelet_filename(lanelet)
        self.assertIsNone(result)

    def test_check_is_lanelet_filename4(self):
        lanelet = '12345_5.bam'
        result = IrodsSeqFileMetadata.check_is_lanelet_filename(lanelet)
        self.assertIsNone(result)

    def test_check_is_lanelet_filename5(self):
        lanelet = '1.bam'
        self.assertRaises(ValueError, IrodsSeqFileMetadata.check_is_lanelet_filename, lanelet)

    def test_check_is_lanelet_filename6(self):
        lanelet = '123.bam'
        self.assertRaises(ValueError, IrodsSeqFileMetadata.check_is_lanelet_filename, lanelet)

    def test_check_is_lanelet_filename7(self):
        lanelet = '1_1.bam'
        self.assertRaises(ValueError, IrodsSeqFileMetadata.check_is_lanelet_filename, lanelet)

    def test_check_is_lanelet_filename8(self):
        lanelet = 'bambam'
        self.assertRaises(ValueError, IrodsSeqFileMetadata.check_is_lanelet_filename, lanelet)

    def test_check_is_lanelet_filename9(self):
        lanelet = '1234'
        self.assertRaises(ValueError, IrodsSeqFileMetadata.check_is_lanelet_filename, lanelet)

    def test_check_is_lanelet_filename10(self):
        lanelet = '1234_4'
        result = IrodsSeqFileMetadata.check_is_lanelet_filename(lanelet)
        self.assertIsNone(result)

    def test_check_is_lanelet_filename11(self):
        lanelet = '12345_4'
        result = IrodsSeqFileMetadata.check_is_lanelet_filename(lanelet)
        self.assertIsNone(result)

    def test_check_is_lanelet_filename12(self):
        lanelet = 'blabla123'
        self.assertRaises(ValueError, IrodsSeqFileMetadata.check_is_lanelet_filename, lanelet)



    def test_check_is_irods_lanelet_fpath1(self):
        path = '/seq/1234/1234_1#3.bam'
        result = IrodsSeqFileMetadata.check_is_irods_lanelet_fpath(path)
        self.assertIsNone(result)

    def test_check_is_irods_lanelet_fpath2(self):
        path = '/seq/1234/1234_1#34.bam'
        result = IrodsSeqFileMetadata.check_is_irods_lanelet_fpath(path)
        self.assertIsNone(result)

    def test_check_is_irods_lanelet_fpath3(self):
        path = '/seq/12345/12345_1#34.bam'
        result = IrodsSeqFileMetadata.check_is_irods_lanelet_fpath(path)
        self.assertIsNone(result)

    def test_check_is_irods_lanelet_fpath4(self):
        path = '/seq/1234/1234_12#34.bam'
        self.assertRaises(ValueError, IrodsSeqFileMetadata.check_is_irods_lanelet_fpath, path)

    def test_check_is_irods_lanelet_fpath5(self):
        path = '/seq/1234/1234_12#345.bam'
        self.assertRaises(ValueError, IrodsSeqFileMetadata.check_is_irods_lanelet_fpath, path)

    def test_check_is_irods_lanelet_fpath6(self):
        path = '/seq/12345/12345_1.cram'
        result = IrodsSeqFileMetadata.check_is_irods_lanelet_fpath(path)
        self.assertIsNone(result)

    def test_check_is_irods_lanelet_fpath7(self):
        path = '/seq/1234/1234.bam'
        self.assertRaises(ValueError, IrodsSeqFileMetadata.check_is_irods_lanelet_fpath, path)

    def test_check_is_irods_lanelet_fpath8(self):
        path = '/seq/1234/1234_1#3.cram'
        result = IrodsSeqFileMetadata.check_is_irods_lanelet_fpath(path)
        self.assertIsNone(result)

    def test_check_is_irods_lanelet_fpath9(self):
        path = '/lustre/1234.bam'
        self.assertRaises(ValueError, IrodsSeqFileMetadata.check_is_irods_lanelet_fpath, path)




    def test_extract_lanelet_name_from_irods_fpath1(self):
        fpath = '/seq/1234/1234_5.cram'
        result = IrodsSeqFileMetadata.extract_lanelet_name_from_irods_fpath(fpath)
        self.assertEqual(result, '1234_5')

    def test_extract_lanelet_name_from_irods_fpath2(self):
        fpath = '/seq/1234/1234_5#6.cram'
        result = IrodsSeqFileMetadata.extract_lanelet_name_from_irods_fpath(fpath)
        self.assertEqual(result, '1234_5#6')

    def test_extract_lanelet_name_from_irods_fpath3(self):
        fpath = '/blah/1234/1234_5.cram'
        self.assertRaises(ValueError, IrodsSeqFileMetadata.extract_lanelet_name_from_irods_fpath, fpath)

    def test_extract_lanelet_name_from_irods_fpath4(self):
        fpath = '/blah/1234/1234_5.cram'
        self.assertRaises(ValueError, IrodsSeqFileMetadata.extract_lanelet_name_from_irods_fpath, fpath)

    def test_extract_lanelet_name_from_irods_fpath5(self):
        fpath = '/seq/balh/1234_5.cram'
        self.assertRaises(ValueError, IrodsSeqFileMetadata.extract_lanelet_name_from_irods_fpath, fpath)



    # @classmethod
    # def get_run_from_irods_path(cls, irods_fpath):
    #     """
    #         This function extracts the run_id from the filename of the irods_path given as parameter.
    #     :param irods_fpath:
    #     :return:
    #     :raises: ValueError if the path doesnt look like an irods sequencing path or the file is not a lanelet.
    #     """
    #     fname = cls.extract_lanelet_name_from_irods_fpath(irods_fpath)
    #     return cls.get_run_from_irods_fname(fname)


    def test_get_run_from_irods_path1(self):
        fpath = '/seq/1234/1234_5.cram'
        result = IrodsSeqFileMetadata.get_run_from_irods_path(fpath)
        self.assertEqual(result, '1234')

    def test_get_run_from_irods_path2(self):
        fpath = '/seq/12345/12345_5#6.cram'
        result = IrodsSeqFileMetadata.get_run_from_irods_path(fpath)
        self.assertEqual(result, '12345')

    def test_get_run_from_irods_path3(self):
        fpath = '/blah/12345/12345_5#6.cram'
        self.assertRaises(ValueError, IrodsSeqFileMetadata.get_run_from_irods_path, fpath)

    def test_get_run_from_irods_path4(self):
        fpath = '/seq/blah/12345_5#6.cram'
        self.assertRaises(ValueError, IrodsSeqFileMetadata.get_run_from_irods_path, fpath)

    def test_get_run_from_irods_path4(self):
        fpath = '/seq/blah/12345_5#6.cram'
        self.assertRaises(ValueError, IrodsSeqFileMetadata.get_run_from_irods_path, fpath)


    # @classmethod
    # def get_lane_from_irods_fname(cls, fname):
    #     r = re.compile(irods_consts.LANLET_NAME_REGEX)
    #     matched_groups = r.match(fname).groupdict()
    #     return matched_groups['lane_id']
    #

    def test_get_lane_from_irods_fname1(self):
        fname = '1234_5.cram'
        result = IrodsSeqFileMetadata.get_lane_from_irods_fname(fname)
        self.assertEqual(result, '5')

    def test_get_lane_from_irods_fname2(self):
        fname = '1234_5#6.cram'
        result = IrodsSeqFileMetadata.get_lane_from_irods_fname(fname)
        self.assertEqual(result, '5')
    def test_extract_reference_name_from_ref_path4(self):
        ref_path = '/lustre/scratch110/srpipe/references/Homo_sapiens/GRCh37_53/all/bwa/Homo_sapiens.GRCh37.dna.all.fa'
        result = IrodsSeqFileMetadata.extract_reference_name_from_ref_path(ref_path)
        self.assertEqual(result, 'Homo_sapiens.GRCh37.dna.all')

    def test_get_lane_from_irods_fname3(self):
        fname = '1234_54#6.cram'
        self.assertRaises(ValueError, IrodsSeqFileMetadata.get_lane_from_irods_fname, fname)

    def test_get_lane_from_irods_fname4(self):
        fname = '1234.cram'
        self.assertRaises(ValueError, IrodsSeqFileMetadata.get_lane_from_irods_fname, fname)


   # @classmethod
   #  def extract_reference_name_from_ref_path(cls, ref_path):
   #      ref_file_name = os.path.basename(ref_path)
   #      if ref_file_name.find(".fa") != -1:
   #          ref_name = ref_file_name.split(".fa")[0]
   #          return ref_name
   #      return ''

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



    # @classmethod
    # def is_md5(cls, md5):
    #     r = re.compile(irods_consts.MD5_REGEX)
    #     return True if r.match(md5) else False

    def test_is_md5_1(self):
        md5 = 'abcdref123asssssdaf'
        result = IrodsSeqFileMetadata.is_md5(md5)
        self.assertTrue(result)

    def test_is_md5_2(self):
        md5 = 'abcdref123asssssdafAAA'
        result = IrodsSeqFileMetadata.is_md5(md5)
        self.assertFalse(result)

    def test_is_md5_3(self):
        md5 = ''
        result = IrodsSeqFileMetadata.is_md5(md5)
        self.assertFalse(result)

    def test_is_md5_4(self):
        md5 = '123'
        result = IrodsSeqFileMetadata.is_md5(md5)
        self.assertTrue(result)

    def test_is_md5_5(self):
        md5 = 'AAA'
        result = IrodsSeqFileMetadata.is_md5(md5)
        self.assertFalse(result)

    def test_is_md5_6(self):
        md5 = 123
        self.assertRaises(TypeError, IrodsSeqFileMetadata.is_md5, md5)


    #
    # @classmethod
    # def is_run_id(cls, run_id):
    #     r = re.compile(irods_consts.RUN_ID_REGEX)
    #     return True if r.match(run_id) else False
    #

    def test_is_run_id1(self):
        run_id = '1234'
        result = IrodsSeqFileMetadata.is_run_id(run_id)
        self.assertTrue(result)

    def test_is_run_id2(self):
        run_id = '1'
        result = IrodsSeqFileMetadata.is_run_id(run_id)
        self.assertFalse(result)

    def test_is_run_id3(self):
        run_id = 'aaa'
        result = IrodsSeqFileMetadata.is_run_id(run_id)
        self.assertFalse(result)

    def test_is_run_id4(self):
        run_id = '12345'
        result = IrodsSeqFileMetadata.is_run_id(run_id)
        self.assertTrue(result)

    def test_is_run_id5(self):
        run_id = True
        self.assertRaises(TypeError, IrodsSeqFileMetadata.is_run_id, run_id)


    # @classmethod
    # def is_lane_id(cls, lane_id):
    #     r = re.compile(irods_consts.LANE_ID_REGEX)
    #     return True if r.match(lane_id) else False
    #
    def test_is_lane_id1(self):
        lane_id = 1
        result = IrodsSeqFileMetadata.is_lane_id(lane_id)
        self.assertTrue(result)

    def test_is_lane_id2(self):
        lane_id = '1'
        result = IrodsSeqFileMetadata.is_lane_id(lane_id)
        self.assertTrue(result)

    def test_is_lane_id3(self):
        lane_id = False
        self.assertRaises(TypeError, IrodsSeqFileMetadata.is_lane_id, lane_id)

    def test_is_lane_id4(self):
        lane_id = '123'
        result = IrodsSeqFileMetadata.is_lane_id(lane_id)
        self.assertFalse(result)

    def test_is_lane_id5(self):
        lane_id = '123aaaa'
        result = IrodsSeqFileMetadata.is_lane_id(lane_id)
        self.assertFalse(result)


    # @classmethod
    # def is_npg_qc(cls, npg_qc):
    #     r = re.compile(irods_consts.NPG_QC_REGEX)
    #     return True if r.match(npg_qc) else False

    def test_is_npg_qc1(self):
        npq_qc = 1
        result = IrodsSeqFileMetadata.is_npg_qc(npq_qc)
        self.assertTrue(result)

    def test_is_npg_qc2(self):
        npq_qc = 4
        result = IrodsSeqFileMetadata.is_npg_qc(npq_qc)
        self.assertFalse(result)

    def test_is_npg_qc3(self):
        npq_qc = "1"
        result = IrodsSeqFileMetadata.is_npg_qc(npq_qc)
        self.assertTrue(result)

    def test_is_npg_qc4(self):
        npq_qc = "0"
        result = IrodsSeqFileMetadata.is_npg_qc(npq_qc)
        self.assertTrue(result)

    def test_is_npg_qc5(self):
        npq_qc = 123
        result = IrodsSeqFileMetadata.is_npg_qc(npq_qc)
        self.assertFalse(result)

    def test_is_npg_qc6(self):
        npq_qc = "mamba"
        result = IrodsSeqFileMetadata.is_npg_qc(npq_qc)
        self.assertFalse(result)

    def test_is_npg_qc7(self):
        npq_qc = True
        self.assertRaises(TypeError, IrodsSeqFileMetadata.is_npg_qc, npq_qc)


    # def check_lane_from_fname_vs_metadata(self):
    #     if not self.lane_id:
    #         raise error_types.TestImpossibleToRunError(fpath=self.fpath, reason='The lane id in the iRODS metadata is either missing or more than 1 ')
    #     lane_from_fname = self.get_lane_from_irods_fname(self.fname)
    #     if str(lane_from_fname) != str(self.lane_id):
    #         raise error_types.IrodsMetadataAttributeVsFileNameError(fpath=self.fpath, attribute='lane', irods_value=self.lane_id, filename_value=lane_from_fname)


    def test_test_lane_from_fname_vs_metadata1(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.bam', fname='1234_5#6.bam', lane_id='5') # fname, fpath, samples, libraries, studies, md5, ichksum_md5, reference, run_id, lane_id, npg_qc):
        result = irods_metadata.test_lane_from_fname_vs_metadata()
        self.assertIsNone(result)

    def test_test_lane_from_fname_vs_metadata2(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5.bam',fname='1234_5.bam', lane_id='5') # fname, fpath, samples, libraries, studies, md5, ichksum_md5, reference, run_id, lane_id, npg_qc):
        result = irods_metadata.test_lane_from_fname_vs_metadata()
        self.assertIsNone(result)

    def test_test_lane_from_fname_vs_metadata3(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.bam', fname='1234_5#6.bam') # fname, fpath, samples, libraries, studies, md5, ichksum_md5, reference, run_id, lane_id, npg_qc):
        self.assertRaises(error_types.TestImpossibleToRunError, irods_metadata.test_lane_from_fname_vs_metadata)

    def test_test_lane_from_fname_vs_metadata4(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.bam',fname='1234_5#6.bam', lane_id='1') # fname, fpath, samples, libraries, studies, md5, ichksum_md5, reference, run_id, lane_id, npg_qc):
        self.assertRaises(error_types.IrodsMetadataAttributeVsFileNameError, irods_metadata.test_lane_from_fname_vs_metadata)


    # def check_md5s(self):
    #     if self.ichksum_md5 and self.md5:
    #         if self.ichksum_md5 != self.md5:
    #             raise error_types.WrongMD5Error(fpath=None, imeta_value=self.md5, ichksum_value=self.ichksum_md5)
    #     else:
    #         if not self.ichksum_md5:
    #             raise error_types.TestImpossibleToRunError(fpath=None, test_name='Test md5', reason='The md5 returned by ichksum is missing')
    #         if not self.md5:
    #             raise error_types.TestImpossibleToRunError(fpath=None, test_name='Test md5', reason='The md5 in iRODS metadata is either missing or more than 1.')

    def test_test_md5_calculated_vs_metadata1(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.bam', fname='1234_5#6.bam', md5='123abc', ichksum_md5='123abc') # fname, fpath, samples, libraries, studies, md5, ichksum_md5, reference, run_id, lane_id, npg_qc):
        result = irods_metadata.test_md5_calculated_vs_metadata()
        self.assertIsNone(result)

    def test_test_md5_calculated_vs_metadata2(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.bam',fname='1234_5#6.bam', md5='123abc123', ichksum_md5='123abc') # fname, fpath, samples, libraries, studies, md5, ichksum_md5, reference, run_id, lane_id, npg_qc):
        self.assertRaises(error_types.WrongMD5Error, irods_metadata.test_md5_calculated_vs_metadata)

    def test_test_md5_calculated_vs_metadata3(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.bam', fname='1234_5#6.bam', md5='123abc') # fname, fpath, samples, libraries, studies, md5, ichksum_md5, reference, run_id, lane_id, npg_qc):
        self.assertRaises(error_types.TestImpossibleToRunError, irods_metadata.test_md5_calculated_vs_metadata)

    def test_test_md5_calculated_vs_metadata4(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.bam', fname='1234_5#6.bam', ichksum_md5='123abc') # fname, fpath, samples, libraries, studies, md5, ichksum_md5, reference, run_id, lane_id, npg_qc):
        self.assertRaises(error_types.TestImpossibleToRunError, irods_metadata.test_md5_calculated_vs_metadata)



    # def check_run_id_from_fname_vs_metadata(self):
    #     """
    #     This test assumes that all the files in iRODS have exactly 1 run (=LANELETS)
    #     """
    #     try:
    #         run_id_from_fname = metadata_utils.iRODSUtils.get_run_from_irods_fname(self.fpath)
    #     except ValueError as e:
    #         raise error_types.TestImpossibleToRunError(fpath=self.fpath, reason=str(e), test_name='Check run_id from filename vs. run_id from iRODS metadata') # 'Cant extract the run id from file name. Not a sequencing file?'
    #     else:
    #         if str(self.run_id) != str(run_id_from_fname):
    #             raise error_types.IrodsMetadataAttributeVsFileNameError(fpath=self.fpath, attribute='run_id', irods_value=self.run_id, filename_value=run_id_from_fname)


    def test_test_run_id_from_fname_vs_metadata1(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.bam', fname='1234_5#6.bam', run_id='1234')
        result = irods_metadata.test_run_id_from_fname_vs_metadata()
        self.assertIsNone(result)

    def test_test_run_id_from_fname_vs_metadata2(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.bam', fname='1234_5#6.bam', run_id='5')
        self.assertRaises(error_types.IrodsMetadataAttributeVsFileNameError, irods_metadata.test_run_id_from_fname_vs_metadata)

    def test_test_run_id_from_fname_vs_metadata3(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.bam', fname='1234_5#6.bam')
        self.assertRaises(error_types.TestImpossibleToRunError, irods_metadata.test_run_id_from_fname_vs_metadata)

    def test_test_run_id_from_fname_vs_metadata4(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.bam', fname='1234_5#6.bam')
        self.assertRaises(error_types.TestImpossibleToRunError, irods_metadata.test_run_id_from_fname_vs_metadata)



    # def sanity_checks_on_fields(self):
    #     problems = []
    #     if self.md5 and not self.is_md5(self.md5):
    #         problems.append(error_types.WrongMetadataValue(attribute='md5', value=self.md5))
    #     if self.run_id and not self.is_run_id(self.run_id):
    #         problems.append(error_types.WrongMetadataValue(attribute='run_id', value=self.run_id))
    #     if self.lane_id and not self.is_lane_id(self.lane_id):
    #         problems.append(error_types.WrongMetadataValue(attribute='lane_id', value=self.lane_id))
    #     if self.npg_qc and not self.is_npg_qc(self.npg_qc):
    #         problems.append(error_types.WrongMetadataValue(attribute='npg_qc', value=self.npg_qc))
    #     return problems


    def test_run_field_sanity_checks1(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.bam', fname='1234_5#6.bam', md5='aaAAA')
        result = irods_metadata.run_field_sanity_checks()
        self.assertEqual(len(result) , 1)
        self.assertEqual(type(result[0]), error_types.WrongMetadataValue)

    def test_run_field_sanity_checks2(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.bam', fname='1234_5#6.bam', run_id='aaAAA')
        result = irods_metadata.run_field_sanity_checks()
        self.assertEqual(len(result) , 1)
        self.assertEqual(type(result[0]), error_types.WrongMetadataValue)

    def test_run_field_sanity_checks3(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.bam', fname='1234_5#6.bam', lane_id='aaAAA')
        result = irods_metadata.run_field_sanity_checks()
        self.assertEqual(len(result) , 1)
        self.assertEqual(type(result[0]), error_types.WrongMetadataValue)

    def test_run_field_sanity_checks4(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.bam', fname='1234_5#6.bam', npg_qc='aaAAA')
        result = irods_metadata.run_field_sanity_checks()
        self.assertEqual(len(result) , 1)
        self.assertEqual(type(result[0]), error_types.WrongMetadataValue)


   # @classmethod
   #  def run_avu_count_checks(cls, fpath, avus):
   #      problems = []
   #      md5_list = metadata_utils.iRODSUtils.extract_values_for_key_from_irods_metadata(avus, 'md5')
   #      if len(md5_list) != 1:
   #          problems.append(error_types.IrodsMetadataAttributeFrequencyError(fpath, 'md5', '1', str(len(md5_list))))
   #
   #      ref_list = metadata_utils.iRODSUtils.extract_values_for_key_from_irods_metadata(avus, 'reference')
   #      if len(ref_list) != 1:
   #          problems.append(error_types.IrodsMetadataAttributeFrequencyError(fpath, 'reference', '1', str(len(ref_list))))
   #
   #      run_id_list = metadata_utils.iRODSUtils.extract_values_for_key_from_irods_metadata(avus, 'id_run')
   #      if len(run_id_list) != 1:
   #          problems.append(error_types.IrodsMetadataAttributeFrequencyError(fpath, 'id_run', '1', str(len(run_id_list))))
   #
   #      lane_id_list = metadata_utils.iRODSUtils.extract_values_for_key_from_irods_metadata(avus, 'lane')
   #      if len(lane_id_list) != 1:
   #          problems.append(error_types.IrodsMetadataAttributeFrequencyError(fpath, 'lane', '1', str(len(lane_id_list))))
   #
   #      npg_qc_list = metadata_utils.iRODSUtils.extract_values_for_key_from_irods_metadata(avus, 'manual_qc')
   #      if len(npg_qc_list) != 1:
   #          problems.append(error_types.IrodsMetadataAttributeFrequencyError(fpath, 'manual_qc', '1', str(len(npg_qc_list))))
   #      return problems
   #
   #

    def test_run_avu_count_checks1(self):
        fpath = '/seq/6661/6661_2#12.bam'
        avus = metadata_utils.iRODSUtils.retrieve_irods_avus(fpath)
        print str(avus)
        result = IrodsSeqFileMetadata.run_avu_count_checks(fpath, avus)
        self.assertEqual([], result)


    def test_run_avu_count_checks2(self):
        fpath = 'balh - not used'
        avus = [data_types.MetaAVU(attribute='reference', value='/Homo_sapiens/1000Genomes_hs37d5/all/bwa/hs37d5.fa'),
         data_types.MetaAVU(attribute='lane', value='2'),
         data_types.MetaAVU(attribute='id_run', value='6661'),
         data_types.MetaAVU(attribute='manual_qc', value='1'),
         data_types.MetaAVU(attribute='md5', value='57a5a38aa987c78457dedee14c00e95c')]
        result = IrodsSeqFileMetadata.run_avu_count_checks(fpath, avus)
        self.assertEqual(result, [])

    def test_run_avu_count_checks3(self):
        fpath = 'balh - not used'
        avus = [data_types.MetaAVU(attribute='reference', value='/Homo_sapiens/1000Genomes_hs37d5/all/bwa/hs37d5.fa'),
         data_types.MetaAVU(attribute='lane', value='2'),
         data_types.MetaAVU(attribute='id_run', value='6661'),
         #data_types.MetaAVU(attribute='manual_qc', value='1'),
         data_types.MetaAVU(attribute='md5', value='57a5a38aa987c78457dedee14c00e95c')]
        result = IrodsSeqFileMetadata.run_avu_count_checks(fpath, avus)
        self.assertEqual(len(result), 1)



 #  @classmethod
 #    def get_lane_from_irods_path(cls, irods_fpath):
 #        cls.check_is_irods_seq_fpath(irods_fpath)
 #        fname = common_utils.extract_fname_without_ext(irods_fpath)
 #        return cls.get_lane_from_irods_fname(fname)
 #

    def test_get_lane_from_irods_path1(self):
        fpath = '/seq/1234/1234_1.bam'
        result = IrodsSeqFileMetadata.get_lane_from_irods_path(fpath)
        self.assertEqual(result, '1')

    def test_get_lane_from_irods_path2(self):
        fpath = '/seq/1234/12348.bam'
        self.assertRaises(ValueError, IrodsSeqFileMetadata.get_lane_from_irods_path, fpath)