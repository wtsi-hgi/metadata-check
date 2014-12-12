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

import config

import unittest
from main import bam_checks
from irods import data_types as irods_types

class SeqscapeQueriesTests(unittest.TestCase):

    def test_get_samples_from_seqsc(self):
        identif_list = ['491STDY5478742']
        identif_type = 'name'
        results = bam_checks.get_samples_from_seqsc(identif_list, identif_type)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].internal_id, 1571544)
        self.assertEqual(results[0].accession_number, 'EGAN00001096108')

        identif_list = ['EGAN00001218652']
        identif_type = 'accession_number'
        results = bam_checks.get_samples_from_seqsc(identif_list, identif_type)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, 'SC_WES_INT5899561')
        self.assertEqual(results[0].internal_id, 2040105)



# def get_samples_from_seqsc(ids_list, id_type):
#     samples = []
#     for id_val in ids_list:
#         sample = seqsc.query_sample(**{id_type: id_val})
#         samples.append(sample)
#     return samples
#
#
# def get_libraries_from_seqsc(ids_list, id_type):
#     libraries = []
#     for id_val in ids_list:
#         library = seqsc.query_library(**{id_type: id_val})
#         libraries.append(library)
#     return libraries
#
#
# def get_studies_from_seqsc(ids_list, id_type):
#     studies = []
#     for id_val in ids_list:
#         study = seqsc.query_study(**{id_type: id_val})
#         studies.append(study)
#     return studies

class IRODSvsSeqscMetadataTests(unittest.TestCase):

    def test_get_diff_seqsc_and_irods_samples_metadata(self):
        irods_samples = {'name': ['491STDY5478742'], 'accession_number': ['EGAN00001096108'], 'internal_id': [1571544]}
        result = bam_checks.get_diff_seqsc_and_irods_samples_metadata(irods_samples)
        self.assertEqual(len(result), 0)

        irods_samples = {'name': ['491STDY5478742'], 'accession_number': ['EGAN0000'], 'internal_id': [1571544]}
        result = bam_checks.get_diff_seqsc_and_irods_samples_metadata(irods_samples)
        self.assertEqual(len(result), 1)




# def get_diff_seqsc_and_irods_samples_metadata(irods_samples):
#     seqsc_samples_by_name = get_samples_from_seqsc(irods_samples['name'], 'name')
#     seqsc_samples_by_acc_nr = get_samples_from_seqsc(irods_samples['accession_number'], 'accession_number')
#     seqsc_samples_by_internal_id = get_samples_from_seqsc(irods_samples['internal_id'], 'internal_id')
#
#     differences = []
#     if not (set(seqsc_samples_by_acc_nr) == set(seqsc_samples_by_internal_id) == set(seqsc_samples_by_name)):
#         diff = "Sample identifiers from iRODS don't identify the same set of samples: by name: " + \
#                str(seqsc_samples_by_name) + \
#                " by accession_number:" + str(seqsc_samples_by_acc_nr) + \
#                " by internal_id: " + str(seqsc_samples_by_internal_id)
#         differences.append(diff)
#     return differences


class IRODSvsHeaderMetadataTests(unittest.TestCase):

    def test_get_diff_irods_and_header_metadata(self):
        header_dict = {'name': ['491STDY5478742']}
        irods_dict = {'name': ['123STUDY']}
        result = bam_checks.get_diff_irods_and_header_metadata(header_dict, irods_dict)
        self.assertEqual(len(result), 1)

        header_dict = {'accession_number': ['EGAN00001218652']}
        irods_dict = {'accession_number': ['EGAN00001218652']}
        result = bam_checks.get_diff_irods_and_header_metadata(header_dict, irods_dict)
        self.assertEqual(len(result), 0)

        header_dict = {'accession_number': ['EGAN00001218652'], 'name': ['491STDY5478742']}
        irods_dict = {'accession_number': ['EGAN00001218652'], 'name': []}
        result = bam_checks.get_diff_irods_and_header_metadata(header_dict, irods_dict)
        self.assertEqual(len(result), 1)

        header_dict = {'accession_number': [], 'name': ['SC_WES_INT5899561']}
        irods_dict = {'accession_number': ['EGAN00001218652'], 'name': ['SC_WES_INT5899561']}
        result = bam_checks.get_diff_irods_and_header_metadata(header_dict, irods_dict)
        self.assertEqual(len(result), 0)



# def get_diff_irods_and_header_metadata(header_dict, irods_dict):
#     """
#         where: (e.g.)
#          irods_dict = dict('name': [sample_name], accession_number: [samples_acc_nr], internal_id: [internal_id])
#          header_dict = dict('name': [sample_name], accession_number: [samples_acc_nr], internal_id: [internal_id])
#     """
#     differences = []
#     for id_type, head_ids_list in header_dict.iteritems():
#         if not irods_dict.get(id_type):
#             differences.append("The header contains entities that are not present in iRODS: " + str(head_ids_list))
#         if set(head_ids_list).difference(set(irods_dict[id_type])):
#             differences.append("The header contains entities that are not present in iRODS: " + str(head_ids_list))
#     return differences

class MD5Test(unittest.TestCase):

    @unittest.skipIf(config.RUNNING_LOCATION == 'localhost', "Skipping checksum test because it runs locally")
    def test_check_md5_metadata(self):
        irods_fpath = '/seq/14761/14761_4.bam'
        irods_metadata = [('md5', 'df8afb9196ea7080cd261e65d4ab2ef9')]
        result = bam_checks.check_md5_metadata(irods_metadata, irods_fpath)
        self.assertEqual(len(result), 0)



# def check_md5_metadata(irods_metadata, irods_fpath):
#     md5_metadata = extract_values_by_key_from_irods_metadata(irods_metadata, 'md5')
#     md5_chksum = irods_wrapper.iRODSChecksumOperations.get_checksum(irods_fpath)
#     if not md5_metadata == md5_chksum:
#         return [
#             "The md5 in the iRODS metadata is different from what ichksum returns: " + str(md5_chksum) + " vs. " + str(
#                 md5_metadata)]
#     return []


class LibraryMetadataWholeTests(unittest.TestCase):

    @unittest.skipIf(config.RUNNING_LOCATION == 'localhost', "Skipping checks because it runs locally")
    def test_check_library_metadata(self):
        irods_fpath = '/seq/14761/14761_4.bam'
        header_metadata = bam_checks.get_header_metadata_from_irods_file(irods_fpath)
        irods_metadata = bam_checks.get_irods_metadata(irods_fpath)
        result = bam_checks.check_library_metadata(header_metadata, irods_metadata)
        self.assertEqual(len(result), 1)


class SampleMetadataWholeTests(unittest.TestCase):

    @unittest.skipIf(config.RUNNING_LOCATION == 'localhost', "Skipping checks because it runs locally")
    def test_check_sample_metadata(self):
        irods_fpath = '/seq/11010/11010_8#21.bam'
        header_metadata = bam_checks.get_header_metadata_from_irods_file(irods_fpath)
        irods_metadata = bam_checks.get_irods_metadata(irods_fpath)
        result = bam_checks.check_library_metadata(header_metadata, irods_metadata)
        self.assertEqual(len(result), 1)


# def check_library_metadata(header_metadata, irods_metadata):
#     irods_lib_names_list = extract_values_by_key_from_irods_metadata(irods_metadata, 'library')
#     irods_lib_internal_id_list = extract_values_by_key_from_irods_metadata(irods_metadata, 'library_id')
#     irods_libraries = {'name': irods_lib_names_list,
#                        'internal_id': irods_lib_internal_id_list}
#     header_libraries = {'name': [], 'internal_id': []}
#
#     for lib in header_metadata.libraries:
#         id_type = Identif.guess_identifier_type(lib)
#         header_libraries[id_type].append(lib)
#
#     # Compare IRODS vs. HEADER:
#     irods_vs_head_diffs = get_diff_irods_and_header_metadata(header_libraries, irods_libraries)
#
#     # Compare IRODS vs. SEQSCAPE:
#     irods_vs_seqsc_diffs = get_diff_seqsc_and_irods_libraries_metadata(irods_libraries)
#     return irods_vs_head_diffs + irods_vs_seqsc_diffs


class AuxiliaryFctsTests(unittest.TestCase):

    def test_get_run_from_irods_path(self):
        # Testing for a normal path:
        path = '/seq/1234/1234_3#12.bam'
        result = bam_checks.get_run_from_irods_path(path)
        expected = '1234'
        self.assertEqual(result, expected)

        path = '/seq/11000/11000_2#3.bam'
        result = bam_checks.get_run_from_irods_path(path)
        expected = '11000'
        self.assertEqual(result, expected)

        # Testing that it doesn't crash if a random thing is given:
        path = '/a/random/path'
        result = bam_checks.get_run_from_irods_path(path)
        expected = ''
        self.assertEqual(result, expected)

        path = 'pathwithout_slashes'
        result = bam_checks.get_run_from_irods_path(path)
        expected = ''
        self.assertEqual(result, expected)


    def test_get_lane_from_irods_path(self):
        # Testing it works with normal irods path:
        path = '/seq/1234/1234_3#1.bam'
        result = bam_checks.get_lane_from_irods_path(path)
        expected = '3'
        self.assertEqual(result, expected)

        path = '/seq/1234/12345_6#7.bam'
        result = bam_checks.get_lane_from_irods_path(path)
        expected = '6'
        self.assertEqual(result, expected)

        # Testing it works on a lane-level BAM:
        path = '/seq/1234/1234_5.bam'
        result = bam_checks.get_lane_from_irods_path(path)
        expected = '5'
        self.assertEqual(result, expected)

        # Testing it works on abnormal params:
        path = '/seq/'
        result = bam_checks.get_lane_from_irods_path(path)
        expected = ''
        self.assertEqual(result, expected)

        path = 'a_random_path'
        result = bam_checks.get_lane_from_irods_path(path)
        expected = ''
        self.assertEqual(result, expected)

        # Testing that it returns '' on an empty path
        path = ''
        result = bam_checks.get_lane_from_irods_path(path)
        expected = ''
        self.assertEqual(result, expected)

        # Testing it returns '' on a path from diff. zone:
        path = '/humgen/projects/hgi/SRP123.bam'
        result = bam_checks.get_lane_from_irods_path(path)
        expected = ''
        self.assertEqual(result, expected)


class AdjancentMetadataChecksTests(unittest.TestCase):

    def test_check_run_id(self):
        # Testing it works for normal cases:
        irods_metadata = [irods_types.MetaAVU('id_run', '11000')]
        irods_fpath = '/seq/11000/11000_2#3.bam'
        result = bam_checks.check_run_id(irods_metadata, irods_fpath)
        expected = []
        self.assertEqual(result, expected)

        # Testing that it returns an error if there is no run id in the metadata:
        irods_metadata = []
        irods_fpath = '/seq/11000/11000_2#3.bam'
        result = bam_checks.check_run_id(irods_metadata, irods_fpath)
        self.assertEqual(len(result), 1)

        # Testing that it returns an error message if there is more than 1 run in the metadata:
        irods_metadata = [irods_types.MetaAVU('id_run', '11000'), irods_types.MetaAVU('id_run', '11111')]
        irods_fpath = '/seq/11000/11000_2#3.bam'
        result = bam_checks.check_run_id(irods_metadata, irods_fpath)
        self.assertEqual(len(result), 1)

        # Testing that it returns an error message if the irods path doesn't look like expected:
        irods_metadata = [irods_types.MetaAVU('id_run', '11000')]
        irods_fpath = '/humgen/projects/hgi/11000_2#3.bam'
        result = bam_checks.check_run_id(irods_metadata, irods_fpath)
        self.assertEqual(len(result), 1)


    def test_check_lane_metadata(self):
        # Testing on a normal case - lanelet:
        irods_metadata = [irods_types.MetaAVU('lane', '1')]
        irods_fpath = '/seq/11111/11111_1#2.bam'
        result = bam_checks.check_lane_metadata(irods_metadata, irods_fpath)
        expected = []
        self.assertEqual(result, expected)

        # Testing on a lane-level BAM:
        irods_metadata = [irods_types.MetaAVU('lane', '2')]
        irods_fpath = '/seq/11111/11111_2.bam'
        result = bam_checks.check_lane_metadata(irods_metadata, irods_fpath)
        expected = []
        self.assertEqual(result, expected)

        # Testing that a message is returned if the irods path doesn't look normal:
        irods_metadata = [irods_types.MetaAVU('lane', '2')]
        irods_fpath = '/humgen/projects/hgi/SSS123.bam'
        result = bam_checks.check_lane_metadata(irods_metadata, irods_fpath)
        self.assertEqual(len(result), 1)

        # Testing that a message is returned if there is no irods metadata:
        irods_metadata = []
        irods_fpath = '/seq/11111/11111_2.bam'
        result = bam_checks.check_lane_metadata(irods_metadata, irods_fpath)
        self.assertEqual(len(result), 1)

    def test_extract_reference_name_from_path(self):
        # Testing that it works on the normal case:
        ref_path = '/lustre/scratch110/srpipe/references/Homo_sapiens/1000Genomes_hs37d5/all/bwa/hs37d5.fa'
        result = bam_checks.extract_reference_name_from_path(ref_path)
        expected = 'hs37d5'
        self.assertEqual(result, expected)

        # Testing on a different reference - again normal case, should work:
        ref_path = '/lustre/scratch110/srpipe/references/Homo_sapiens/GRCh38_15/all/bwa/Homo_sapiens.GRCh38_15.fa'
        result = bam_checks.extract_reference_name_from_path(ref_path)
        expected = 'Homo_sapiens.GRCh38_15'
        self.assertEqual(result, expected)

        # Testing that it returns '' if the path is not a reference:
        ref_path = '/lustre/scratch110/srpipe/references/Homo_sapiens/GRCh38_15/all/bwa/Homo_sapiens'
        result = bam_checks.extract_reference_name_from_path(ref_path)
        expected = ''
        self.assertEqual(result, expected)


    def test_check_reference(self):
        # Testing on a normal case - the ref is not the desired one:
        irods_metadata = [irods_types.MetaAVU('reference', '/path/refs/GRCh38_15/all/bwa/Homo_sapiens.GRCh38_15.fa')]
        desired_ref = 'hs37d5'
        result = bam_checks.check_reference(irods_metadata, desired_ref)
        self.assertEqual(len(result), 1)

        # Testing on a normal case - the ref is the desired one:
        irods_metadata = [irods_types.MetaAVU('reference', '/path/ref/Homo_sapiens/1000Genomes_hs37d5/all/bwa/hs37d5.fa')]
        desired_ref = 'hs37d5'
        result = bam_checks.check_reference(irods_metadata, desired_ref)
        self.assertEqual(len(result), 0)


    def test_extract_lanelet_name_from_irods_fpath(self):
        # Testing on a normal lanelet:
        irods_fpath = '/seq/1234/1234_5#6.bam'
        result = bam_checks.extract_lanelet_name_from_irods_fpath(irods_fpath)
        expected = '1234_5#6'
        self.assertEqual(result, expected)

        # Testing for a lane-level bam:
        irods_fpath = '/seq/1234/1234_5.bam'
        result = bam_checks.extract_lanelet_name_from_irods_fpath(irods_fpath)
        expected = '1234_5'
        self.assertEqual(result, expected)

        # Testing on a non-standard path - should return ''
        irods_fpath = '/humgen/projectscrohns/1234SRA.bam'
        result = bam_checks.extract_lanelet_name_from_irods_fpath(irods_fpath)
        expected = ''
        self.assertEqual(result, expected)


    def test_check_lanelet_name(self):
        # Testing on  a normal case:
        irods_fpath = '/seq/1234/1234_5#6.bam'
        header_lanelets = ['1234_5#6']
        result = bam_checks.check_lanelet_name(irods_fpath, header_lanelets)
        expected = []
        self.assertEqual(result, expected)








# def check_run_metadata(irods_metadata, irods_fpath):
#     irods_run_id = extract_values_by_key_from_irods_metadata(irods_metadata, 'id_run')
#     path_run_id = get_run_from_irods_path(irods_fpath)
#     if not irods_run_id == path_run_id:
#         return ["The run id in the iRODS file path is not the same as the run id in the iRODS metadata: " + \
#                 str(irods_run_id) + " vs. " + str(path_run_id)]
#     return []
#
