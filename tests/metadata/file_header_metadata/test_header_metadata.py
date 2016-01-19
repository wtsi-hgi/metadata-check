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

This file has been created on Jan 19, 2016.
"""

import unittest

from metadata.file_header_metadata.header_metadata import SAMFileHeaderMetadata

class TestSAMFileHeaderMetadata(unittest.TestCase):

    def test_is_id_valid_1(self):
        id = 123
        self.assertTrue(SAMFileHeaderMetadata._is_id_valid(id))

    def test_is_id_valid_2(self):
        id = 'undefined'
        self.assertFalse(SAMFileHeaderMetadata._is_id_valid(id))

    def test_is_id_valid_3(self):
        id = -1
        self.assertFalse(SAMFileHeaderMetadata._is_id_valid(id))

    def test_is_id_valid_4(self):
        id = ''
        self.assertFalse(SAMFileHeaderMetadata._is_id_valid(id))

    def test_is_id_valid_5(self):
        id = None
        self.assertFalse(SAMFileHeaderMetadata._is_id_valid(id))

    def test_is_id_valid_6(self):
        id = "123"
        self.assertTrue(SAMFileHeaderMetadata._is_id_valid(id))


    def test_filter_out_invalid_ids_1(self):
        ids = [123, '']
        expected_result = [123]
        actual_result = SAMFileHeaderMetadata._filter_out_invalid_ids(ids)
        self.assertListEqual(expected_result, actual_result)

    def test_filter_out_invalid_ids_2(self):
        ids = [123, -1]
        expected_result = [123]
        actual_result = SAMFileHeaderMetadata._filter_out_invalid_ids(ids)
        self.assertListEqual(expected_result, actual_result)

    def test_filter_out_invalid_ids_3(self):
        ids = ['123']
        expected_result = ['123']
        actual_result = SAMFileHeaderMetadata._filter_out_invalid_ids(ids)
        self.assertListEqual(expected_result, actual_result)

    def test_filter_out_invalid_ids_4(self):
        ids = [None, 123]
        expected_result = [123]
        actual_result = SAMFileHeaderMetadata._filter_out_invalid_ids(ids)
        self.assertListEqual(expected_result, actual_result)


    def test_check_for_invalid_ids_1(self):
        multi_ids = {'name': ['Ana', '']}
        result = SAMFileHeaderMetadata._check_for_invalid_ids(multi_ids, 'sample')
        self.assertEqual(len(result), 1)

    def test_check_for_invalid_ids_2(self):
        multi_ids = {'name': ['Ana', ''], 'ids': [-1, 0]}
        result = SAMFileHeaderMetadata._check_for_invalid_ids(multi_ids, 'sample')
        self.assertEqual(len(result), 2)

    def test_check_for_invalid_ids_3(self):
        multi_ids = {'name': ['Ana']}
        result = SAMFileHeaderMetadata._check_for_invalid_ids(multi_ids, 'sample')
        self.assertEqual(len(result), 0)

    def test_check_for_invalid_ids_4(self):
        multi_ids = {'name': ['Ana', ''], 'id': [], 'accession_number': ['EGA1', None]}
        result = SAMFileHeaderMetadata._check_for_invalid_ids(multi_ids, 'sample')
        self.assertEqual(len(result), 2)

