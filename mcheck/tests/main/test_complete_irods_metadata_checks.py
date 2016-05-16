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

This file has been created on Jul 09, 2015.
"""

import os
import unittest

from mcheck.metadata.irods_metadata.data_types import MetaAVU
from mcheck.main import complete_irods_metadata_checks as target_module


@unittest.skip
class TestCompleteIrodsMetadataChecks(unittest.TestCase):

    # def parse_config_file(path):
    # attributes_frequency = {}
    # config_file = open(path)
    # for line in config_file:
    #     line = line.strip()
    #     tokens = line.split()
    #     if len(tokens) != 2:
    #         raise ValueError("Non standard config file - each line must have 2 items. This line looks like:"+str(line))
    #     attribute = tokens[0]
    #     if not tokens[1].isdigit():
    #         raise ValueError("The config file doesn't contain integers as frequencies" + str(line))
    #     freq = int(tokens[1])
    #     attributes_frequency[attribute] = freq
    # return attributes_frequency


    def test_parse_config_file1(self):
        crt_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.abspath(os.path.join(crt_dir, os.pardir))
        testfile1 = os.path.join(parent_dir, 'testdata/testdata_parse_config_file1.txt')
        result = target_module.read_and_parse_config_file(testfile1)
        expected = {'reference' : 1, 'sample_accession_number' : 1, 'total_reads' : 1, 'id_run' : 1}
        self.assertDictEqual(result, expected)

    def test_parse_config_file2(self):
        crt_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.abspath(os.path.join(crt_dir, os.pardir))
        testfile1 = os.path.join(parent_dir, 'testdata/other_config.txt')
        result = target_module.read_and_parse_config_file(testfile1)
        expected = {'type' : 1, 'is_paired_read' : 0, 'library_id' : 3, 'lane' : 2}
        self.assertDictEqual(result, expected)

    def test_parse_config_file3(self):
        crt_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.abspath(os.path.join(crt_dir, os.pardir))
        testfile1 = os.path.join(parent_dir, 'testdata/empty_config.txt')
        self.assertRaises(ValueError, target_module.read_and_parse_config_file, testfile1)



# def build_freq_dict_from_avus_list(avus_list):
#     freq_dict = defaultdict(int)
#     for avu in avus_list:
#         freq_dict[avu.attribute] += 1
#     return freq_dict

    def test_build_freq_dict_from_avus_list1(self):
        avus =  [MetaAVU(attribute='study_id', value='2278'), MetaAVU(attribute='sample', value='SC_HE35369554')]
        result = target_module.build_freq_dict_from_avus_list(avus)
        expected = {'study_id' : 1, 'sample' : 1}
        self.assertDictEqual(result, expected)

    def test_build_freq_dict_from_avus_list2(self):
        avus =  [MetaAVU(attribute='study_id', value='2278'), MetaAVU(attribute='sample', value='SC1'),
                 MetaAVU(attribute='sample', value='SC2')]
        result = target_module.build_freq_dict_from_avus_list(avus)
        expected = {'study_id' : 1, 'sample' : 2}
        self.assertDictEqual(result, expected)


    def test_build_freq_dict_from_avus_list3(self):
        # avus =  [MetaAVU(attribute='study_id', value='2278'), MetaAVU(attribute='sample', value='SC1'),
        #          MetaAVU(attribute='sample', value='SC2')]
        avus = [MetaAVU(attribute='study_id', value='2278'),
                MetaAVU(attribute='study_title', value='Human Evolution 3'),
                MetaAVU(attribute='sample', value='SC_HE35369554'),
                MetaAVU(attribute='type', value='bam'),
                MetaAVU(attribute='is_paired_read', value='1'),
                MetaAVU(attribute='library', value='5622696'),
                MetaAVU(attribute='md5', value='c9d8b8f81dd5cbd10fd9971c4e3fc0dc'),
                MetaAVU(attribute='tag_index', value='55'),
                MetaAVU(attribute='sample_accession_number', value='EGAN00001072787'),
                MetaAVU(attribute='study', value='SEQCAP_WGS_Human_Evolution_3'),
                MetaAVU(attribute='tag', value='TTCGCACC'),
                MetaAVU(attribute='target', value='0'),
                MetaAVU(attribute='target', value='1'),
                MetaAVU(attribute='sample_common_name', value='Homo Sapien'),
                MetaAVU(attribute='manual_qc', value='1'), MetaAVU(attribute='total_reads', value='124544996'),
                MetaAVU(attribute='reference', value='/lustre/scratch109/srpipe/references/Homo_sapiens/1000Genomes_hs37d5/all/bwa/hs37d5.fa'),
                MetaAVU(attribute='sample_id', value='1448638'), MetaAVU(attribute='id_run', value='8284'),
                MetaAVU(attribute='lane', value='5'), MetaAVU(attribute='alignment_filter', value='xahuman'),
                MetaAVU(attribute='study_accession_number', value='EGAS00001000315'),
                MetaAVU(attribute='library_id', value='5622696'), MetaAVU(attribute='alignment', value='1'),
                MetaAVU(attribute='rt_ticket', value='431331')]

        result = target_module.build_freq_dict_from_avus_list(avus)
        self.assertEqual(result['target'], 2)
