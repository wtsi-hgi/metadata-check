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

    def test_find_missing_ids_no_missing_internal_id(self):
        entities_fetched = [Sample(name='sam1', internal_id='123', accession_number='ega123')]
        query_ids = ['123']
        test_obj = SeqscapeEntitiesFetched(entities_fetched, query_ids, query_id_type='internal_id', query_entity_type='sample',
                                           fetched_entity_type='sample')
        result = test_obj._find_missing_ids()
        expected = []
        self.assertEqual(result, expected)

    def test_find_missing_ids_missing_internal_id(self):
        entities_fetched = [Sample(name='sam1', internal_id='123', accession_number='ega123')]
        query_ids = ['123', '456']
        test_obj = SeqscapeEntitiesFetched(entities_fetched, query_ids, query_id_type='internal_id', query_entity_type='sample',
                                           fetched_entity_type='sample')
        result = test_obj._find_missing_ids()
        expected = ['456']
        self.assertEqual(result, expected)

    def test_find_missing_ids_nothing_found(self):
        entities_fetched = []
        query_ids = ['123']
        test_obj = SeqscapeEntitiesFetched(entities_fetched, query_ids, query_id_type='internal_id', query_entity_type='sample',
                                           fetched_entity_type='sample')
        result = test_obj._find_missing_ids()
        expected = ['123']
        self.assertEqual(result, expected)


    def test_find_duplicated_ids_no_duplicates(self):
        entities_fetched = [Sample(name='sam1', internal_id='123', accession_number='ega123')]
        test_obj = SeqscapeEntitiesFetched(entities_fetched, ['123'], query_id_type='internal_id', query_entity_type='sample',
                                           fetched_entity_type='sample')
        result = test_obj._find_duplicated_ids()
        expected = []
        self.assertEqual(result, expected)

    def test_find_duplicated_ids_1_duplicate(self):
        entities_fetched = [Sample(name='sam1', internal_id='123', accession_number='ega123'), Sample(name='sam2', internal_id='123', accession_number='ega444')]
        test_obj = SeqscapeEntitiesFetched(entities_fetched, ['123'], query_id_type='internal_id', query_entity_type='sample',
                                           fetched_entity_type='sample')
        result = test_obj._find_duplicated_ids()
        expected = ['123']
        self.assertEqual(result, expected)

    def test_find_duplicated_ids_nothing_fetched(self):
        entities_fetched = []
        test_obj = SeqscapeEntitiesFetched(entities_fetched, ['123'], query_id_type='internal_id', query_entity_type='sample',
                                           fetched_entity_type='sample')
        result = test_obj._find_duplicated_ids()
        expected = []
        self.assertEqual(result, expected)


    def test_check_all_ids_were_found_when_missing(self):
        entities_fetched = [Sample(name='sam1', internal_id='123', accession_number='ega123'), Sample(name='sam2', internal_id='123', accession_number='ega444')]
        query_ids = ['1', '2', '123']
        test_obj = SeqscapeEntitiesFetched(entities_fetched, query_ids, query_id_type='internal_id', query_entity_type='sample',
                                           fetched_entity_type='sample')
        result = test_obj.check_all_ids_were_found()
        self.assertEqual(len(result), 1)

    def test_check_all_ids_were_found_when_not_missing(self):
        entities_fetched = [Sample(name='sam1', internal_id='123', accession_number='ega123'), Sample(name='sam2', internal_id='123', accession_number='ega444')]
        query_ids = ['123']
        test_obj = SeqscapeEntitiesFetched(entities_fetched, query_ids, query_id_type='internal_id', query_entity_type='sample',
                                           fetched_entity_type='sample')
        result = test_obj.check_all_ids_were_found()
        self.assertEqual(len(result), 0)


    def test_check_no_duplicates_found_when_duplicates(self):
        entities_fetched = [Sample(name='sam1', internal_id='123', accession_number='ega123'), Sample(name='sam1', internal_id='00', accession_number='ega444')]
        test_obj = SeqscapeEntitiesFetched(entities_fetched, ['123'], query_id_type='name', query_entity_type='sample',
                                           fetched_entity_type='sample')
        result = test_obj._find_duplicated_ids()
        self.assertEqual(len(result), 1)



class TestSeqscapeRawMetadata(unittest.TestCase):

    def test_add_fetched_entities_ok(self):
        samples_fetched = Sample(name='sam12', accession_number='ega12', internal_id='12')
        entities_fetched_obj = SeqscapeEntitiesFetched([samples_fetched], query_ids=['12'],
                                                       query_id_type='internal_id', query_entity_type='sample',
                                                       fetched_entity_type='sample')
        raw_metadata = SeqscapeRawMetadata()
        self.assertEqual(len(raw_metadata.get_fetched_entities_by_type('sample')), 0)
        raw_metadata.add_fetched_entities(entities_fetched_obj)
        self.assertEqual(len(raw_metadata.get_fetched_entities_by_type('sample')), 1)

    def test_add_fetched_entities_when_nothing_to_add(self):
        raw_metadata = SeqscapeRawMetadata()
        self.assertEqual(len(raw_metadata.get_fetched_entities_by_type('sample')), 0)
        raw_metadata.add_fetched_entities(None)
        self.assertEqual(len(raw_metadata.get_fetched_entities_by_type('sample')), 0)


    def test_add_all_fetched_entities_ok(self):
        sample_fetched = Sample(name='sam12', accession_number='ega12', internal_id='12')
        entities_fetched_list = [SeqscapeEntitiesFetched([sample_fetched], query_ids=['12'],
                                                       query_id_type='internal_id', query_entity_type='sample',
                                                       fetched_entity_type='sample')]
        raw_metadata = SeqscapeRawMetadata()
        self.assertEqual(len(raw_metadata.get_fetched_entities_by_type('sample')), 0)
        raw_metadata.add_all_fetched_entities(entities_fetched_list)
        self.assertEqual(len(raw_metadata.get_fetched_entities_by_type('sample')), 1)


    def test_add_all_fetched_entities_nothing_to_add(self):
        raw_metadata = SeqscapeRawMetadata()
        self.assertEqual(len(raw_metadata.get_fetched_entities_by_type('sample')), 0)
        raw_metadata.add_all_fetched_entities([])
        self.assertEqual(len(raw_metadata.get_fetched_entities_by_type('sample')), 0)


    def test_add_fetched_entities_by_association_ok(self):
        samples_fetched = Sample(name='sam12', accession_number='ega12', internal_id='12')
        entities_fetched_obj = SeqscapeEntitiesFetched([samples_fetched], query_ids=['12'],
                                                       query_id_type='internal_id', query_entity_type='sample',
                                                       fetched_entity_type='study')
        raw_metadata = SeqscapeRawMetadata()
        self.assertEqual(len(raw_metadata.get_fetched_entities_by_type('sample')), 0)
        raw_metadata.add_fetched_entities(entities_fetched_obj)
        self.assertEqual(len(raw_metadata.get_fetched_entities_by_type('study')), 1)

    def test_get_fetched_entities_by_type_1_type(self):
        samples_fetched = Sample(name='sam12', accession_number='ega12', internal_id='12')
        entities_fetched_obj1 = SeqscapeEntitiesFetched([samples_fetched], query_ids=['12'],
                                                       query_id_type='internal_id', query_entity_type='sample',
                                                       fetched_entity_type='sample')
        raw_metadata = SeqscapeRawMetadata()
        raw_metadata.add_fetched_entities(entities_fetched_obj1)
        self.assertEqual(len(raw_metadata.get_fetched_entities_by_type('sample')), 1)

        samples_fetched = Sample(name='sam23', accession_number='ega23', internal_id='23')
        entities_fetched_obj2 = SeqscapeEntitiesFetched([samples_fetched], query_ids=['23'],
                                                       query_id_type='internal_id', query_entity_type='sample',
                                                       fetched_entity_type='sample')
        raw_metadata.add_fetched_entities(entities_fetched_obj2)
        self.assertEqual(len(raw_metadata.get_fetched_entities_by_type('sample')), 2)


    def test_get_fetched_entities_by_type_2_types(self):
        samples_fetched = Sample(name='sam12', accession_number='ega12', internal_id='12')
        entities_fetched_obj1 = SeqscapeEntitiesFetched([samples_fetched], query_ids=['12'],
                                                       query_id_type='internal_id', query_entity_type='sample',
                                                       fetched_entity_type='sample')
        raw_metadata = SeqscapeRawMetadata()
        raw_metadata.add_fetched_entities(entities_fetched_obj1)
        self.assertEqual(len(raw_metadata.get_fetched_entities_by_type('sample')), 1)

        studies_fetched = Sample(name='sam23', accession_number='ega23', internal_id='23')
        entities_fetched_obj2 = SeqscapeEntitiesFetched([samples_fetched], query_ids=['23'],
                                                       query_id_type='internal_id', query_entity_type='study',
                                                       fetched_entity_type='study')
        raw_metadata.add_fetched_entities(entities_fetched_obj2)
        self.assertEqual(len(raw_metadata.get_fetched_entities_by_type('sample')), 1)
        self.assertEqual(len(raw_metadata.get_fetched_entities_by_type('study')), 1)


    def test_get_entities_without_duplicates_by_entity_type(self):
        samples_fetched = Sample(name='sam12', accession_number='ega12', internal_id='12')
        entities_fetched_obj1 = SeqscapeEntitiesFetched([samples_fetched], query_ids=['12'],
                                                       query_id_type='internal_id', query_entity_type='sample',
                                                       fetched_entity_type='sample')
        raw_metadata = SeqscapeRawMetadata()
        raw_metadata.add_fetched_entities(entities_fetched_obj1)
        self.assertEqual(len(raw_metadata.get_fetched_entities_by_type('sample')), 1)

        samples_fetched = Sample(name='sam12', accession_number='ega12', internal_id='12')
        entities_fetched_obj2 = SeqscapeEntitiesFetched([samples_fetched], query_ids=['12'],
                                                       query_id_type='internal_id', query_entity_type='sample',
                                                       fetched_entity_type='sample')
        raw_metadata.add_fetched_entities(entities_fetched_obj2)
        self.assertEqual(len(raw_metadata.get_fetched_entities_by_type('sample')), 2)

        result = raw_metadata.get_entities_without_duplicates_by_entity_type('sample')
        self.assertEqual(1, len(result))

    def test_get_entities_without_duplicates_by_entity_type_when_no_entities(self):
        samples_fetched = Sample(name='sam12', accession_number='ega12', internal_id='12')
        entities_fetched_obj1 = SeqscapeEntitiesFetched([samples_fetched], query_ids=['12'],
                                                       query_id_type='internal_id', query_entity_type='sample',
                                                       fetched_entity_type='sample')
        raw_metadata = SeqscapeRawMetadata()
        raw_metadata.add_fetched_entities(entities_fetched_obj1)
        self.assertEqual(len(raw_metadata.get_fetched_entities_by_type('sample')), 1)

        result = raw_metadata.get_entities_without_duplicates_by_entity_type('library')
        self.assertEqual(0, len(result))

