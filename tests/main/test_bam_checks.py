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

class TestBamChecks(unittest.TestCase):

    def test_get_diff_irods_and_header_metadata(self):
        header_dict = {'name': ['491STDY5478742']}
        irods_dict = {'name': ['123STUDY']}
        result = bam_checks.get_diff_irods_and_header_metadata(header_dict, irods_dict)
        self.assertEqual(len(result), 1)

        header_dict = {'accession_number': ['EGAN00001218652']}
        irods_dict = {'accession_number': ['EGAN00001218652']}
        result = bam_checks.get_diff_irods_and_header_metadata(header_dict, irods_dict)
        self.assertEqual(len(result), 0)

        header_dict = {'accession_number': ['EGAN00001218652']}
        irods_dict = {'accession_number': ['EGAN00001218652'], 'name': ['491STDY5478742']}
        result = bam_checks.get_diff_irods_and_header_metadata(header_dict, irods_dict)
        self.assertEqual(len(result), 1)

        header_dict = {'accession_number': [], 'name': ['SC_WES_INT5899561']}
        irods_dict = {'accession_number': ['EGAN00001218652'], 'name': ['SC_WES_INT5899561']}
        result = bam_checks.get_diff_irods_and_header_metadata(header_dict, irods_dict)
        self.assertEqual(len(result), 0)


    def test_check_all_identifiers_in_metadata(self):
        metadata = {'name': ['aaa'], 'internal_id': [1,2,3]}
        expected = []
        result = bam_checks.check_all_identifiers_in_metadata(metadata, accession_number=False)
        self.assertEqual(expected, result)

        metadata = {'name': ['aaa'], 'internal_id': [1,2,3], 'accession_number': []}
        expected = []
        result = bam_checks.check_all_identifiers_in_metadata(metadata, accession_number=False)
        self.assertEqual(expected, result)

        metadata = {'name': ['aaa'], 'internal_id': [1,2,3], 'accession_number': ['EGA123']}
        expected = []
        result = bam_checks.check_all_identifiers_in_metadata(metadata, accession_number=False)
        self.assertEqual(expected, result)

        metadata = {'name': ['aaa'], 'internal_id': [1,2,3], 'accession_number': []}
        expected = []
        result = bam_checks.check_all_identifiers_in_metadata(metadata, accession_number=False)
        self.assertEqual(expected, result)
