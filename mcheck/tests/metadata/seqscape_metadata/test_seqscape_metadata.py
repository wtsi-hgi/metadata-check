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

This file has been created on Feb 26, 2016.
"""
import unittest
from sequencescape import connect_to_sequencescape, Sample, Study, Library
from mcheck.metadata.seqscape_metadata.seqscape_metadata import SeqscapeRawMetadata, SeqscapeEntitiesFetched


class TestSeqscapeEntitiesFetched(unittest.TestCase):

    def test_check_all_ids_were_found_when_no_missing_internal_id(self):
        entities_fetched = [Sample(name='sam1', internal_id='123', accession_number='ega123')]
        query_ids = ['123']
        test_obj = SeqscapeEntitiesFetched(entities_fetched, query_ids, query_id_type='internal_id', query_entity_type='sample',
                                           fetched_entity_type='sample')
        result = test_obj._find_missing_ids()
        expected = []
        self.assertEqual(result, expected)

    def test_check_all_ids_were_found_when_missing_internal_id(self):
        entities_fetched = [Sample(name='sam1', internal_id='123', accession_number='ega123')]
        query_ids = ['123', '456']
        test_obj = SeqscapeEntitiesFetched(entities_fetched, query_ids, query_id_type='internal_id', query_entity_type='sample',
                                           fetched_entity_type='sample')
        result = test_obj._find_missing_ids()
        expected = ['456']
        self.assertEqual(result, expected)

    def test_check_all_ids_were_found_nothing_found(self):
        entities_fetched = []
        query_ids = ['123']
        test_obj = SeqscapeEntitiesFetched(entities_fetched, query_ids, query_id_type='internal_id', query_entity_type='sample',
                                           fetched_entity_type='sample')
        result = test_obj._find_missing_ids()
        expected = ['123']
        self.assertEqual(result, expected)


    def test_check_no_duplicates_found_when_no_duplicates(self):
        entities_fetched = [Sample(name='sam1', internal_id='123', accession_number='ega123')]
        test_obj = SeqscapeEntitiesFetched(entities_fetched, ['123'], query_id_type='internal_id', query_entity_type='sample',
                                           fetched_entity_type='sample')
        result = test_obj._find_duplicated_ids()
        expected = []
        self.assertEqual(result, expected)

    def test_check_no_duplicates_found_when_1_duplicate(self):
        entities_fetched = [Sample(name='sam1', internal_id='123', accession_number='ega123'), Sample(name='sam2', internal_id='123', accession_number='ega444')]
        test_obj = SeqscapeEntitiesFetched(entities_fetched, ['123'], query_id_type='internal_id', query_entity_type='sample',
                                           fetched_entity_type='sample')
        result = test_obj._find_duplicated_ids()
        expected = ['123']
        self.assertEqual(result, expected)

    def test_check_no_duplicates_found_when_nothing_fetched(self):
        entities_fetched = []
        test_obj = SeqscapeEntitiesFetched(entities_fetched, ['123'], query_id_type='internal_id', query_entity_type='sample',
                                           fetched_entity_type='sample')
        result = test_obj._find_duplicated_ids()
        expected = []
        self.assertEqual(result, expected)








