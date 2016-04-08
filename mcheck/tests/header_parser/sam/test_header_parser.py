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

This file has been created on Apr 07, 2016.
"""

import unittest
from mcheck.header_parser.sam.header_parser import SAMFileRGTagParser, SAMFileHeaderParser
from mcheck.header_parser.sam.header import SAMFileHeader, SAMFileRGTag

class TestSAMFileHeaderParser(unittest.TestCase):

    def test_parse_when_small_header(self):
        header = '@HD   1:2\n@SQ    SN:1\n@RG   LB:1\n@PG   ID:bwa'
        result = SAMFileHeaderParser.parse(header)
        expected = SAMFileHeader(rg_tag=['@RG   LB:1'], pg_tag=['@PG   ID:bwa'], sq_tag=['@SQ    SN:1'], hd_tag=['@HD   1:2'])
        self.assertEqual(result, expected)

    def test_parse_when_full_header(self):
        header = '@HD     VN:1.0  GO:none SO:coordinate\n' \
                 '@SQ     SN:1    LN:197195432    AS:NCBIM37      UR:file:/lustre/scratch102/projects/mouse/ref/NCBIM37_um        M5:f05d753079c455c0e57af88eeda24493\n' \
                 '@RG     ID:1662_1       PL:SLX  LB:A_J_SLX_500_HC_2     PI:500  DS:A_J_Mouse_Genome     SM:A_J  CN:SC\n' \
                 '@PG     ID:maq  VN:0.7.1-6'
        parsed_header = SAMFileHeaderParser.parse(header)
        expected = SAMFileHeader(rg_tag=['@RG     ID:1662_1       PL:SLX  LB:A_J_SLX_500_HC_2     PI:500  DS:A_J_Mouse_Genome     SM:A_J  CN:SC'],
                                 pg_tag=['@PG     ID:maq  VN:0.7.1-6'],
                                 hd_tag=['@HD     VN:1.0  GO:none SO:coordinate'],
                                 sq_tag=['@SQ     SN:1    LN:197195432    AS:NCBIM37      UR:file:/lustre/scratch102/projects/mouse/ref/NCBIM37_um        M5:f05d753079c455c0e57af88eeda24493'])
        self.assertEqual(parsed_header, expected)

    def test_parse_when_header_almost_empty(self):
        header = '@HD   nothing:nothing'
        result = SAMFileHeaderParser.parse(header)
        expected = SAMFileHeader(hd_tag=['@HD   nothing:nothing'])
        print("RESULT: %s" % str(type(result)))
        print("EXPECTED: %s" % str(type(expected)))
        self.assertEqual(result, expected)

    def test_parse_when_header_empty(self):
        header = ''
        result = SAMFileHeaderParser.parse(header)
        expected = SAMFileHeader()
        print("RESULT: %s" % str(type(result)))
        print("EXPECTED: %s" % str(type(expected)))
        self.assertEqual(result, expected)



class TestSAMFileRGTagParser(unittest.TestCase):

    def test_from_read_grp_to_dict_when_ok(self):
        read_grp = '@PG\tID:maq\tVN:0.7'
        result = SAMFileRGTagParser._from_read_grp_to_dict(read_grp)
        expected = {'ID': 'maq', 'VN': '0.7'}
        self.assertDictEqual(expected, result)

        read_grp = '@HD\tVN:1.0\tGO:none\tSO:coordinate'
        result = SAMFileRGTagParser._from_read_grp_to_dict(read_grp)
        expected = {'VN': '1.0', 'GO': 'none', 'SO': 'coordinate'}
        self.assertDictEqual(expected, result)

    def test_from_read_grp_to_dict_when_empty(self):
        read_grp = ''
        result = SAMFileRGTagParser._from_read_grp_to_dict(read_grp)
        expected = {}
        self.assertDictEqual(expected, result)

    def test_from_read_grp_to_dict_when_invalid(self):
        read_grp = '@HD\tMMM\tM:N'
        self.assertRaises(ValueError, SAMFileRGTagParser._from_read_grp_to_dict, read_grp)

    def test_parse_when_ok(self):
        read_grps = ['@RG\tID:1662_1\tPL:SLX\tLB:A_J_SLX_500_HC_2\tPI:500\tDS:A_J_Mouse_Genome\tSM:A_J\tCN:SC']
        result = SAMFileRGTagParser.parse(read_grps)
        expected = SAMFileRGTag(seq_centers=['SC'], platforms=['SLX'], samples=['A_J'], libraries=['A_J_SLX_500_HC_2'])
        self.assertEqual(result, expected)

    def test_parse_when_more_rgs_in_header(self):
        read_grps = ['@RG\tLB:1662\tSM:SAM1', '@RG\tLB:1661\tSM:SAM2']
        result = SAMFileRGTagParser.parse(read_grps)
        expected = SAMFileRGTag(samples=['SAM1', 'SAM2'], libraries=['1662', '1661'])
        self.assertEqual(result, expected)

    def test_parse_when_no_rgs(self):
        read_grps = []
        result = SAMFileRGTagParser.parse(read_grps)
        expected = SAMFileRGTag()
        self.assertEqual(result, expected)

    def test_parse_when_empty_rg(self):
        read_grps = ['@RG\tLB:1662\tSM:SAM1', '']
        result = SAMFileRGTagParser.parse(read_grps)
        expected = SAMFileRGTag(libraries=['1662'], samples=['SAM1'])
        self.assertEqual(result, expected)


