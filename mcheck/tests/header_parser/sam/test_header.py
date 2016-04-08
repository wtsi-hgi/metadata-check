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
from mcheck.header_parser.sam.header import SAMFileHeader, SAMFileRGTag


class TestSAMFileHeader(unittest.TestCase):
    def test_eq_when_not_equals(self):
        header1 = SAMFileHeader(
            rg_tag=['ID:1662_1       PL:SLX  LB:A_J_SLX_500_HC_2     PI:500  DS:A_J_Mouse_Genome     SM:A_J  CN:SC'],
            pg_tag=['ID:maq  VN:0.7.1-6'],
            hd_tag=['VN:1.0  GO:none SO:coordinate'],
            sq_tag=['SN:1    LN:197195432    AS:NCBIM37      UR:file:/lustre/scratch102/projects/mouse/ref/NCBIM37_um        M5:f05d753079c455c0e57af88eeda24493'])
        header2 = SAMFileHeader(
            rg_tag=['ID:1662_1       PL:SLX  LB:A_J_SLX_500_HC_2     PI:500  DS:A_J_Mouse_Genome     SM:A_J  CN:SC'])
        self.assertNotEqual(header1, header2)

    def test_eq_when_real_headers_equal(self):
        header1 = SAMFileHeader(
            rg_tag=['ID:1662_1       PL:SLX  LB:A_J_SLX_500_HC_2     PI:500  DS:A_J_Mouse_Genome     SM:A_J  CN:SC'],
            pg_tag=['ID:maq  VN:0.7.1-6'],
            hd_tag=['VN:1.0  GO:none SO:coordinate'],
            sq_tag=[
                'SN:1    LN:197195432    AS:NCBIM37      UR:file:/lustre/scratch102/projects/mouse/ref/NCBIM37_um        M5:f05d753079c455c0e57af88eeda24493'])
        header2 = SAMFileHeader(
            rg_tag=['ID:1662_1       PL:SLX  LB:A_J_SLX_500_HC_2     PI:500  DS:A_J_Mouse_Genome     SM:A_J  CN:SC'],
            pg_tag=['ID:maq  VN:0.7.1-6'],
            hd_tag=['VN:1.0  GO:none SO:coordinate'],
            sq_tag=[
                'SN:1    LN:197195432    AS:NCBIM37      UR:file:/lustre/scratch102/projects/mouse/ref/NCBIM37_um        M5:f05d753079c455c0e57af88eeda24493'])
        self.assertEqual(header1, header2)

    def test_eq_when_empty_headers(self):
        header1 = SAMFileHeader()
        header2 = SAMFileHeader()
        self.assertEqual(header2, header1)

    def test_eq_when_random_strings_not_eq(self):
        header1 = SAMFileHeader(rg_tag=['ID:1662_1\tPL:SLX'])
        header2 = SAMFileHeader(rg_tag=['ID:1662_1'])
        self.assertNotEqual(header1, header2)

    def test_eq_when_more_rgs(self):
        header1 = SAMFileHeader(rg_tag=['some RG'])
        header2 = SAMFileHeader(rg_tag=['other RG', 'second other RG'])
        self.assertNotEqual(header1, header2)

    def test_eq_when_empty_tag(self):
        header1 = SAMFileHeader()
        header2 = SAMFileHeader(rg_tag=['other RG', 'second other RG'])
        self.assertNotEqual(header1, header2)

class TestRGTag(unittest.TestCase):

    def test_eq_when_eqal_tags(self):
        tag1 = SAMFileRGTag(seq_centers=['SC'], seq_dates=[], lanelets=['1234'], libraries=['lib1'], samples=['sam1'])
        tag2 = SAMFileRGTag(seq_centers=['SC'], seq_dates=[], lanelets=['1234'], libraries=['lib1'], samples=['sam1'])
        self.assertEqual(tag1, tag2)

    def test_eq_when_not_eqal_samples(self):
        tag1 = SAMFileRGTag(seq_centers=['SC'], lanelets=['1234'], libraries=['lib1'], samples=['sam1'])
        tag2 = SAMFileRGTag(seq_centers=['SC'], lanelets=['1234'], libraries=['lib2'], samples=['sam2'])
        self.assertNotEqual(tag1, tag2)

    def test_eq_when_missing_fields(self):
        tag1 = SAMFileRGTag(seq_centers=['SC'], lanelets=['1234'], libraries=['lib1'], samples=['sam1'])
        tag2 = SAMFileRGTag(seq_centers=['SC'], lanelets=['1234'])
        self.assertNotEqual(tag1, tag2)

    def test_eq_when_equals_qith_short_lists(self):
        tag1 = SAMFileRGTag(lanelets=['1234'])
        tag2 = SAMFileRGTag(lanelets=['1234'])
        self.assertEqual(tag1, tag2)

    def test_eq_when_equals_qith_long_lists(self):
        tag1 = SAMFileRGTag(lanelets=['1234', '3456', '5678'])
        tag2 = SAMFileRGTag(lanelets=['1234', '5678', '3456'])
        self.assertEqual(tag1, tag2)





