"""
 Copyright (c) 2013 Genome Research Ltd.

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

"""


import os
from hamcrest import *
import unittest

# from Celery_Django_Prj import configs
# from serapis.com import constants
# from serapis.worker import tasks
# from serapis.worker.logic import entities
# from serapis.seqscape import data_access
# from serapis.worker.logic.header_parser import BAMHeaderParser, BAMHeader, VCFHeaderParser, VCFHeader, MetadataHandling

from header_parser.sam_header_analyser import BAMHeaderAnalyser, _RGTagAnalyser
#from header_parser.sam_header_parser import BAMHeaderParser

class Test_RGTagAnalyser(unittest.TestCase):

    def test_extract_platform_list_from_rg(self):
        header_rg = {"ID" : "1#71.5", "PL" : "ILLUMINA", "PU" : "120910_HS11_08408_B_C0PNFACXX_8#71", "LB" : "5507617"}
        platf = _RGTagAnalyser._extract_platform_list_from_rg(header_rg)
        print "PLATF: ", str(platf)
        #assert_that(platf, equal_to("ILLUMINA HS"))
        self.assertEqual(platf, "ILLUMINA HS")

        header_rg = {"ID" : "1#71.4", "PL" : "ILLUMINA", "PU" : "120910_HS11_08408_B_C0PNFACXX_7#71", "LB" : "5507617"}
        platf = _RGTagAnalyser._extract_platform_list_from_rg(header_rg)
        assert_that(platf, equal_to("ILLUMINA HS"))


    def test_extract_run_from_PUHeader(self):
        pu_entry = '120815_HS16_08276_A_C0NKKACXX_4#1'
        run = _RGTagAnalyser._extract_run_from_pu_entry(pu_entry)
        self.assertEqual(run, 8276)

        pu_entry = '120415_HS29_07874_B_C0K32ACXX_7#6'
        run = _RGTagAnalyser._extract_run_from_pu_entry(pu_entry)
        self.assertEqual(run, 7874)

    def test_extract_tag_from_PUHeader(self):
        pu_entry = '120415_HS29_07874_B_C0K32ACXX_7#6'
        run = _RGTagAnalyser._extract_tag_from_pu_entry(pu_entry)
        self.assertEqual(run, 6)

        pu_entry = '120815_HS16_08276_A_C0NKKACXX_4#1'
        run = _RGTagAnalyser._extract_tag_from_pu_entry(pu_entry)
        self.assertEqual(run, 1)

        pu_entry = '120815_HS16_08276_A_C0NKKACXX_4'
        run = _RGTagAnalyser._extract_tag_from_pu_entry(pu_entry)
        self.assertEqual(run, None)


    def test_extract_lane_from_PUHeader(self):
        pu_entry = '120815_HS16_08276_A_C0NKKACXX_4#1'
        run = _RGTagAnalyser._extract_lane_from_pu_entry(pu_entry)
        self.assertEqual(run, 4)

        pu_entry = '120415_HS29_07874_B_C0K32ACXX_7#6'
        run = _RGTagAnalyser._extract_lane_from_pu_entry(pu_entry)
        self.assertEqual(run, 7)

        pu_entry = '120814_HS5_08271_B_D0WDNACXX_2#88'
        run = _RGTagAnalyser._extract_lane_from_pu_entry(pu_entry)
        self.assertEqual(run, 2)

        pu_entry = '120814_HS5_08271_B_D0WDNACXX'
        run = _RGTagAnalyser._extract_lane_from_pu_entry(pu_entry)
        self.assertEqual(run, None)


    def test_build_lanelet_name(self):
        pu_entry = '120415_HS29_07874_B_C0K32ACXX_7#6'
        run_id = _RGTagAnalyser._extract_run_from_pu_entry(pu_entry)
        lane = _RGTagAnalyser._extract_lane_from_pu_entry(pu_entry)
        tag = _RGTagAnalyser._extract_tag_from_pu_entry(pu_entry)
        lanelet = _RGTagAnalyser._build_lanelet_name(run_id, lane, tag)
        self.assertEqual(lanelet, '7874_7#6')


        pu_entry = '120814_HS5_08271_B_D0WDNACXX_2#88'
        run_id = _RGTagAnalyser._extract_run_from_pu_entry(pu_entry)
        lane = _RGTagAnalyser._extract_lane_from_pu_entry(pu_entry)
        tag = _RGTagAnalyser._extract_tag_from_pu_entry(pu_entry)
        lanelet = _RGTagAnalyser._build_lanelet_name(run_id, lane, tag)
        self.assertEqual(lanelet, '8271_2#88')


        run = '1111'
        lane = '2'
        result = _RGTagAnalyser._build_lanelet_name(run, lane)
        self.assertEqual(result, '1111_2')

        result = _RGTagAnalyser._build_lanelet_name(None, None, None)
        self.assertEqual(None, result)


    def test_extract_lanelet_name_from_pu_entry(self):
        pu_entry = '111025_HS11_06976_B_C064EACXX_1#3'
        result = _RGTagAnalyser._extract_lanelet_name_from_pu_entry(pu_entry)
        self.assertEqual(result, '6976_1#3')

        pu_entry = '120724_HS17_08183_B_C0KC9ACXX_5#53'
        result = _RGTagAnalyser._extract_lanelet_name_from_pu_entry(pu_entry)
        self.assertEqual(result, '8183_5#53')

        pu_entry = '1111_1#1'
        result = _RGTagAnalyser._extract_lanelet_name_from_pu_entry(pu_entry)
        self.assertEqual(result, pu_entry)



    def test_parse_RG(self):
        fpath = os.path.join(configs.LUSTRE_HOME, 'bams/agv-ethiopia/egpg5306022.bam')
        #header = BAMHeaderParser.parse(fpath, sq=False, hd=False,pg=False)
        header = BAMHeaderParser.extract_header(fpath)
        header_rg = _RGTagAnalyser.parse_all(header['RG'])
        self.assertSetEqual(set(header_rg.seq_centers), set(['SC']))
        assert_that(header_rg.library_list, has_item('5507617'))
        assert_that(header_rg.platform_list, has_item('ILLUMINA HS'))
        assert_that(header_rg.sample_list, has_item('EGAN00001071830'))


        fpath = os.path.join(configs.LUSTRE_HOME, 'bams/crohns/WTCCC113699.bam')
        header = BAMHeaderParser.extract_header(fpath)
        header_rg = _RGTagAnalyser.parse_all(header['RG'])
        assert_that(header_rg, hasattr(header_rg, 'samples'))
        assert_that(header_rg, hasattr(header_rg, 'libraries'))
        assert_that(header_rg, hasattr(header_rg, 'seq_centers'))
        assert_that(header_rg, hasattr(header_rg, 'seq_dates'))
        assert_that(header_rg, hasattr(header_rg, 'platforms'))
        assert_that(header_rg, hasattr(header_rg, 'lanelets'))
        assert_that(header_rg.platform_list, instance_of(list))

        fpath = os.path.join(configs.LUSTRE_HOME, 'bams/agv-ethiopia/egpg5306042.bam')
        header = BAMHeaderParser.extract_header(fpath)
        header_rg = _RGTagAnalyser.parse_all(header['RG'])
        assert_that(header_rg, hasattr(header_rg, 'samples'))
        assert_that(header_rg, hasattr(header_rg, 'libraries'))
        assert_that(header_rg, hasattr(header_rg, 'seq_centers'))
        assert_that(header_rg, hasattr(header_rg, 'seq_dates'))
        assert_that(header_rg, hasattr(header_rg, 'platforms'))
        assert_that(header_rg, hasattr(header_rg, 'lanelets'))

        assert_that(header_rg.platforms, instance_of(list))
        assert_that(header_rg.samples, instance_of(list))
        assert_that(header_rg.libraries, instance_of(list))
        assert_that(header_rg.seq_centers, instance_of(list))
        assert_that(header_rg.seq_dates, instance_of(list))

        assert_that(header_rg.platforms, has_length(1))
        assert_that(header_rg.samples, has_length(1))
        assert_that(header_rg.libraries, has_length(1))
        assert_that(header_rg.seq_centers, has_length(1))
        assert_that(header_rg.seq_dates, has_length(3))
        assert_that(header_rg.lanelets, has_length(6))

        assert_that(header_rg.libraries, has_item('5507643'))
        assert_that(header_rg.samples, has_item('EGAN00001071820'))
        assert_that(header_rg.seq_centers, has_item('SC'))
        assert_that(header_rg.platforms, has_item('ILLUMINA HS'))
        assert_that(header_rg.seq_dates, has_item('2012-07-16T00:00:00+0100'))

        header_rg = [{'ID': 'SZAIPI037128-51',
                      'PL': 'illumina',
                      'PU': '131220_I875_FCC3K7HACXX_L4_SZAIPI037128-51',
                      'LB': 'SZAIPI037128-51',
                      'SM': 'F05_XX629745'}]
        parsed_header_rg = _RGTagAnalyser.parse_all(header_rg)
        assert_that(parsed_header_rg.sample_list, has_item('F05_XX629745'))
        assert_that(parsed_header_rg.platform_list, has_item('illumina'))
        assert_that(parsed_header_rg.library_list, has_item('SZAIPI037128-51'))


    def test_parse(self):
        path = os.path.join(configs.LUSTRE_HOME, 'bams/crohns/WTCCC113699.bam')
        header = BAMHeaderParser.extract_header(path)
        header_parsed = BAMHeaderParser.parse(header, rg=True, pg=False, hd=False, sq=False)
        assert_that(header_parsed.rg.platform_list, has_item('ILLUMINA HS'))



class TestRGTagAnalyser(unittest.TestCase):

    # def test_group_header_entries_by_type(self):
    #     #path = "/home/ic4/media-tmp2/users/ic4/bams/agv-ethiopia/egpg5306046.bam"
    #
    #     # Must be: {'LB': ['5507617'], 'CN': ['SC'], 'PU': ['120910_HS11_08408_B_C0PNFACXX_6#71', '120731_HS25_08213_B_C0N8CACXX_2#71']}
    #     header = [{"ID" : "1#71.5", "PL" : "ILLUMINA", "PU" : "120910_HS11_08408_B_C0PNFACXX_8#71", "LB" : "5507617"},
    #               {"ID" : "1#71.4", "PL" : "ILLUMINA", "PU" : "120910_HS11_08408_B_C0PNFACXX_7#71", "LB" : "5507617"}]
    #     grouped_header = BAMHeaderAnalyser.group_header_entries_by_type(header)
    #     assert_that(grouped_header, has_entry("LB", ["5507617"]))
    #     assert_that(grouped_header, has_entry("PU", has_item("120910_HS11_08408_B_C0PNFACXX_7#71")))
    #
    #
    # def test_extract_platform_list_from_header(self):
    #     header = [{"ID" : "1#71.5", "PL" : "ILLUMINA", "PU" : "120910_HS11_08408_B_C0PNFACXX_8#71", "LB" : "5507617"},
    #               {"ID" : "1#71.4", "PL" : "ILLUMINA", "PU" : "120910_HS11_08408_B_C0PNFACXX_7#71", "LB" : "5507617"}]
    #     grouped_header = BAMHeaderAnalyser.group_header_entries_by_type(header)
    #     platf = BAMHeaderAnalyser.extract_platform_list_from_header(grouped_header)
    #     assert_that(platf, contains("Illumina HiSeq"))
    #
    #     grouped_header = {'LB': ['5507617'], 'ID': ['1#71.4', '1#71.5'], 'PU': ['120910_HS11_08408_B_C0PNFACXX_7#71']}
    #     platf = BAMHeaderAnalyser.extract_platform_list_from_header(grouped_header)
    #     print "PLATFORM: ", platf
    #     assert_that(platf, has_item("Illumina HiSeq"))
    #     assert_that(platf, instance_of(list))
    #

    # def test_get_header_readgrps_list(self):
    #     path = os.path.join(configs.LUSTRE_HOME, 'bams/agv-ethiopia/egpg5306022.bam')
    #     #"/home/ic4/media-tmp2/users/ic4/bams/agv-ethiopia/egpg5306022.bam"
    #     header = BAMHeaderAnalyser.get_header_readgrps_list(path)
    #     assert_that(header, has_item(has_key("CN")))
    #     assert_that(header, has_item(has_entry("PL", "ILLUMINA")))
    #     assert_that(header, has_item(has_entry("PU", "120910_HS11_08408_B_C0PNFACXX_8#71")))
    #     assert_that(header, has_item(has_entry("SM", "EGAN00001071830")))


    def test_build_run_id(self):
        pu_entry = '120415_HS29_07874_B_C0K32ACXX_7#6'
        run_id = BAMHeaderAnalyser.build_run_id(pu_entry)
        self.assertEqual(run_id, '7874_7#6')

        pu_entry = '120814_HS5_08271_B_D0WDNACXX_2#88'
        run_id = BAMHeaderAnalyser.build_run_id(pu_entry)
        self.assertEqual(run_id, '8271_2#88')

    def test_extract_run_from_PUHeader(self):
        pu_entry = '120815_HS16_08276_A_C0NKKACXX_4#1'
        run = _RGTagAnalyser._extract_run_from_pu_entry(pu_entry)
        self.assertEqual(run, 8276)

        pu_entry = '120415_HS29_07874_B_C0K32ACXX_7#6'
        run = _RGTagAnalyser._extract_run_from_pu_entry(pu_entry)
        self.assertEqual(run, 7874)

    def test_extract_tag_from_PUHeader(self):
        pu_entry = '120415_HS29_07874_B_C0K32ACXX_7#6'
        run = _RGTagAnalyser._extract_tag_from_pu_entry(pu_entry)
        self.assertEqual(run, 6)

        pu_entry = '120815_HS16_08276_A_C0NKKACXX_4#1'
        run = _RGTagAnalyser._extract_tag_from_pu_entry(pu_entry)
        self.assertEqual(run, 1)

    def test_extract_lane_from_PUHeader(self):
        pu_entry = '120815_HS16_08276_A_C0NKKACXX_4#1'
        run = _RGTagAnalyser._extract_lane_from_pu_entry(pu_entry)
        self.assertEqual(run, 4)

        pu_entry = '120415_HS29_07874_B_C0K32ACXX_7#6'
        run = _RGTagAnalyser._extract_lane_from_pu_entry(pu_entry)
        self.assertEqual(run, 7)

        pu_entry = '120814_HS5_08271_B_D0WDNACXX_2#88'
        run = _RGTagAnalyser._extract_lane_from_pu_entry(pu_entry)
        self.assertEqual(run, 2)

    #
    # def test_parse_header(self):
    #     fpath = os.path.join(configs.LUSTRE_HOME, 'bams/agv-ethiopia/egpg5306022.bam')
    #     # "/home/ic4/media-tmp2/users/ic4/bams/agv-ethiopia/egpg5306022.bam"
    #     header = BAMHeaderAnalyser.parse_header(fpath)
    #     self.assertSetEqual(set(header.seq_centers), set(['SC']))
    #
    #
    #     fpath = os.path.join(configs.LUSTRE_HOME, 'bams/crohns/WTCCC113699.bam')
    #     #"/home/ic4/media-tmp2/users/ic4/bams/crohns/WTCCC113699.bam"
    #     header = BAMHeaderAnalyser.parse_header(fpath)
    #     assert_that(header, hasattr(header, 'sample_list'))
    #     assert_that(header, hasattr(header, 'library_list'))
    #     assert_that(header, hasattr(header, 'seq_centers'))
    #     assert_that(header, hasattr(header, 'seq_date_list'))
    #     assert_that(header, hasattr(header, 'platform_list'))
    #     assert_that(header, hasattr(header, 'run_ids_list'))
    #     assert_that(header.platform_list, instance_of(list))
    #
    #     fpath = os.path.join(configs.LUSTRE_HOME, 'bams/agv-ethiopia/egpg5306042.bam')
    #     #"/home/ic4/media-tmp2/users/ic4/bams/agv-ethiopia/egpg5306042.bam"
    #     header = BAMHeaderAnalyser.parse_header(fpath)
    #     assert_that(header, hasattr(header, 'sample_list'))
    #     assert_that(header, hasattr(header, 'library_list'))
    #     assert_that(header, hasattr(header, 'seq_centers'))
    #     assert_that(header, hasattr(header, 'seq_date_list'))
    #     assert_that(header, hasattr(header, 'platform_list'))
    #     assert_that(header, hasattr(header, 'run_ids_list'))
    #
    #     assert_that(header.platform_list, instance_of(list))
    #     assert_that(header.sample_list, instance_of(list))
    #     assert_that(header.library_list, instance_of(list))
    #     assert_that(header.seq_centers, instance_of(list))
    #     assert_that(header.seq_date_list, instance_of(list))
    #
    #     assert_that(header.platform_list, has_length(1))
    #     assert_that(header.sample_list, has_length(1))
    #     assert_that(header.library_list, has_length(1))
    #     assert_that(header.seq_centers, has_length(1))
    #     assert_that(header.seq_date_list, has_length(3))
