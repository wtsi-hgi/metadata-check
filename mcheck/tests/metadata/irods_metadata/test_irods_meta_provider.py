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

This file has been created on Jul 20, 2016.
"""
import unittest
from mcheck.metadata.irods_metadata.irods_meta_provider import iRODSMetadataProvider

class ArgsConvertedToIrodsFieldsTests(unittest.TestCase):

    def test_convert_args_to_search_criteria_1(self):
        result = set(iRODSMetadataProvider.convert_to_irods_fields(filter_by_npg_qc='1', filter_by_target='1', filter_by_file_types='cram'))
        expected = set([('manual_qc', '1'), ('target', '1'), ('type', 'cram')])
        self.assertSetEqual(result, expected)


    def test_convert_args_to_search_criteria_when_no_search_criteria(self):
        result = set(iRODSMetadataProvider.convert_to_irods_fields())
        expected = set()
        self.assertSetEqual(result, expected)


    def test_convert_args_to_search_criteria_2(self):
        result = iRODSMetadataProvider.convert_to_irods_fields(match_study_acc_nr='EGA1')
        expected = [('study_accession_number', 'EGA1')]
        self.assertSetEqual(set(result), set(expected))


    def test_convert_args_to_search_criteria_3(self):
        result = set(iRODSMetadataProvider.convert_to_irods_fields(filter_by_file_types='bam'))
        expected = set([('type', 'bam')])
        self.assertSetEqual(result, expected)
