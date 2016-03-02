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
from mcheck.metadata.seqscape_metadata.seqscape_metadata import SeqscapeRawMetadata, SeqscapeEntitiesFetched, SeqscapeMetadata


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
        entities_fetched_obj = SeqscapeEntitiesFetched(samples_fetched, query_ids=['12'],
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
        entities_fetched_list = [SeqscapeEntitiesFetched(sample_fetched, query_ids=['12'],
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
        entities_fetched_obj = SeqscapeEntitiesFetched(samples_fetched, query_ids=['12'],
                                                       query_id_type='internal_id', query_entity_type='sample',
                                                       fetched_entity_type='study')
        raw_metadata = SeqscapeRawMetadata()
        self.assertEqual(len(raw_metadata.get_fetched_entities_by_type('sample')), 0)
        raw_metadata.add_fetched_entities(entities_fetched_obj)
        self.assertEqual(len(raw_metadata.get_fetched_entities_by_type('study')), 1)

    def test_get_fetched_entities_by_type_1_type(self):
        samples_fetched = Sample(name='sam12', accession_number='ega12', internal_id='12')
        entities_fetched_obj1 = SeqscapeEntitiesFetched(samples_fetched, query_ids=['12'],
                                                       query_id_type='internal_id', query_entity_type='sample',
                                                       fetched_entity_type='sample')
        raw_metadata = SeqscapeRawMetadata()
        raw_metadata.add_fetched_entities(entities_fetched_obj1)
        self.assertEqual(len(raw_metadata.get_fetched_entities_by_type('sample')), 1)

        samples_fetched = Sample(name='sam23', accession_number='ega23', internal_id='23')
        entities_fetched_obj2 = SeqscapeEntitiesFetched(samples_fetched, query_ids=['23'],
                                                       query_id_type='internal_id', query_entity_type='sample',
                                                       fetched_entity_type='sample')
        raw_metadata.add_fetched_entities(entities_fetched_obj2)
        self.assertEqual(len(raw_metadata.get_fetched_entities_by_type('sample')), 2)


    def test_get_fetched_entities_by_type_2_types(self):
        samples_fetched = Sample(name='sam12', accession_number='ega12', internal_id='12')
        entities_fetched_obj1 = SeqscapeEntitiesFetched(samples_fetched, query_ids=['12'],
                                                       query_id_type='internal_id', query_entity_type='sample',
                                                       fetched_entity_type='sample')
        raw_metadata = SeqscapeRawMetadata()
        raw_metadata.add_fetched_entities(entities_fetched_obj1)
        self.assertEqual(len(raw_metadata.get_fetched_entities_by_type('sample')), 1)

        studies_fetched = Sample(name='sam23', accession_number='ega23', internal_id='23')
        entities_fetched_obj2 = SeqscapeEntitiesFetched(samples_fetched, query_ids=['23'],
                                                       query_id_type='internal_id', query_entity_type='study',
                                                       fetched_entity_type='study')
        raw_metadata.add_fetched_entities(entities_fetched_obj2)
        self.assertEqual(len(raw_metadata.get_fetched_entities_by_type('sample')), 1)
        self.assertEqual(len(raw_metadata.get_fetched_entities_by_type('study')), 1)


    def test_get_entities_without_duplicates_by_entity_type(self):
        samples_fetched = Sample(name='sam12', accession_number='ega12', internal_id='12')
        entities_fetched_obj1 = SeqscapeEntitiesFetched(samples_fetched, query_ids=['12'],
                                                       query_id_type='internal_id', query_entity_type='sample',
                                                       fetched_entity_type='sample')
        raw_metadata = SeqscapeRawMetadata()
        raw_metadata.add_fetched_entities(entities_fetched_obj1)
        self.assertEqual(len(raw_metadata.get_fetched_entities_by_type('sample')), 1)

        samples_fetched = Sample(name='sam12', accession_number='ega12', internal_id='12')
        entities_fetched_obj2 = SeqscapeEntitiesFetched(samples_fetched, query_ids=['12'],
                                                       query_id_type='internal_id', query_entity_type='sample',
                                                       fetched_entity_type='sample')
        raw_metadata.add_fetched_entities(entities_fetched_obj2)
        self.assertEqual(len(raw_metadata.get_fetched_entities_by_type('sample')), 2)

        result = raw_metadata.get_entities_without_duplicates_by_entity_type('sample')
        self.assertEqual(1, len(result))

    def test_get_entities_without_duplicates_by_entity_type_when_no_entities(self):
        samples_fetched = Sample(name='sam12', accession_number='ega12', internal_id='12')
        entities_fetched_obj1 = SeqscapeEntitiesFetched(samples_fetched, query_ids=['12'],
                                                       query_id_type='internal_id', query_entity_type='sample',
                                                       fetched_entity_type='sample')
        raw_metadata = SeqscapeRawMetadata()
        raw_metadata.add_fetched_entities(entities_fetched_obj1)
        self.assertEqual(len(raw_metadata.get_fetched_entities_by_type('sample')), 1)

        result = raw_metadata.get_entities_without_duplicates_by_entity_type('library')
        self.assertEqual(0, len(result))


    def test_get_all_fetched_entity_types(self):
        samples_fetched = Sample(name='sam12', accession_number='ega12', internal_id='12')
        entities_fetched_obj1 = SeqscapeEntitiesFetched(samples_fetched, query_ids=['12'],
                                                       query_id_type='internal_id', query_entity_type='sample',
                                                       fetched_entity_type='sample')
        raw_metadata = SeqscapeRawMetadata()
        raw_metadata.add_fetched_entities(entities_fetched_obj1)

        study_fetched = Study(name='my study', accession_number='ega1', internal_id='444')
        entities_fetched_obj2 = SeqscapeEntitiesFetched(study_fetched, query_ids=['444'],
                                                       query_id_type='name', query_entity_type='study',
                                                       fetched_entity_type='study')
        raw_metadata.add_fetched_entities(entities_fetched_obj2)

        result = raw_metadata.get_all_fetched_entity_types()
        self.assertEqual(len(result), 2)


    def test_check_by_comparison_entities_fetched_by_different_id_types_ok(self):
        samples_fetched = [Sample(name='sam12', accession_number='ega12', internal_id='12')]
        samples_fetched_obj = SeqscapeEntitiesFetched(samples_fetched, query_ids=['12'],
                                                       query_id_type='internal_id', query_entity_type='sample',
                                                       fetched_entity_type='sample')
        raw_metadata = SeqscapeRawMetadata()
        raw_metadata.add_fetched_entities(samples_fetched_obj)
        raw_metadata.add_fetched_entities(samples_fetched_obj)
        entities_fetched = raw_metadata.get_fetched_entities_by_type('sample')

        result = raw_metadata._check_by_comparison_entities_fetched_by_different_id_types(entities_fetched)
        self.assertEqual(0, len(result))

    def test_check_by_comparison_entities_fetched_by_different_id_types_wrong(self):
        raw_metadata = SeqscapeRawMetadata()

        samples_fetched_1 = [Sample(name='sam12', accession_number='ega12', internal_id='12')]
        samples_fetched_obj_1 = SeqscapeEntitiesFetched(samples_fetched_1, query_ids=['12'],
                                                       query_id_type='name', query_entity_type='sample',
                                                       fetched_entity_type='sample')
        raw_metadata.add_fetched_entities(samples_fetched_obj_1)

        samples_fetched_2 = [Sample(name='sam34', accession_number='ega34', internal_id='34')]
        samples_fetched_obj_2 = SeqscapeEntitiesFetched(samples_fetched_2, query_ids=['12'],
                                                       query_id_type='internal_id', query_entity_type='sample',
                                                       fetched_entity_type='sample')
        raw_metadata.add_fetched_entities(samples_fetched_obj_2)

        entities_fetched = raw_metadata.get_fetched_entities_by_type('sample')
        print("Type of entity fetched -- from tests : %s " % str(type(entities_fetched[0])))
        result = raw_metadata._check_by_comparison_entities_fetched_by_different_id_types(entities_fetched)
        self.assertEqual(1, len(result))

    def test_check_by_comparison_entities_fetched_by_different_id_types_more_wrong(self):
        raw_metadata = SeqscapeRawMetadata()

        # Sample1:
        samples_fetched_1 = [Sample(name='sam12', accession_number='ega12', internal_id='12')]
        samples_fetched_obj_1 = SeqscapeEntitiesFetched(samples_fetched_1, query_ids=['12'],
                                                       query_id_type='name', query_entity_type='sample',
                                                       fetched_entity_type='sample')
        raw_metadata.add_fetched_entities(samples_fetched_obj_1)

        # Sample2:
        samples_fetched_2 = [Sample(name='sam34', accession_number='ega34', internal_id='34')]
        samples_fetched_obj_2 = SeqscapeEntitiesFetched(samples_fetched_2, query_ids=['12'],
                                                       query_id_type='internal_id', query_entity_type='sample',
                                                       fetched_entity_type='sample')
        raw_metadata.add_fetched_entities(samples_fetched_obj_2)

        # Sample 3:
        samples_fetched_3 = [Sample(name='sam12', accession_number='ega25', internal_id='25')]
        samples_fetched_obj_3 = SeqscapeEntitiesFetched(samples_fetched_3, query_ids=['12'],
                                                       query_id_type='accession_number', query_entity_type='sample',
                                                       fetched_entity_type='sample')
        raw_metadata.add_fetched_entities(samples_fetched_obj_3)

        entities_fetched = raw_metadata.get_fetched_entities_by_type('sample')
        print("Type of entity fetched -- from tests : %s " % str(type(entities_fetched[0])))
        result = raw_metadata._check_by_comparison_entities_fetched_by_different_id_types(entities_fetched)
        self.assertEqual(2, len(result))


class TestEntitiesFetchedByAssociation(unittest.TestCase):
    def setUp(self):
        samples_fetched = Sample(name='sam12', accession_number='ega12', internal_id='12')
        entities_fetched_obj1 = SeqscapeEntitiesFetched(samples_fetched, query_ids=['12'],
                                                       query_id_type='internal_id', query_entity_type='study',
                                                       fetched_entity_type='sample')
        self.raw_metadata = SeqscapeRawMetadata()
        self.raw_metadata.add_fetched_entities_by_association(entities_fetched_obj1)

        study_fetched = Study(name='my study', accession_number='ega1', internal_id='444')
        entities_fetched_obj2 = SeqscapeEntitiesFetched([study_fetched], query_ids=['444'],
                                                       query_id_type='name', query_entity_type='sample',
                                                       fetched_entity_type='study')
        self.raw_metadata.add_fetched_entities_by_association(entities_fetched_obj2)


    def test_add_fetched_entities_by_association(self):
        result = self.raw_metadata._entities_fetched_by_association
        self.assertEqual(len(result), 2)


    def test_get_all_fetched_entities_by_association(self):
        result = self.raw_metadata.get_all_fetched_entities_by_association()
        self.assertEqual(len(result), 2)


    def test_get_fetched_entities_by_association_by_type(self):
        result = self.raw_metadata.get_all_fetched_entities_by_association_by_type('sample', 'study')
        self.assertEqual(len(result), 1)


class TestSamplesAndStudiesFetched(unittest.TestCase):

    def setUp(self):
        # Entities by association
        sam1 = Sample(name='sam1', accession_number='ega1', internal_id='1')
        sam1_fetched = SeqscapeEntitiesFetched(sam1, query_ids=['1'],
                                                       query_id_type='internal_id', query_entity_type='sample',
                                                       fetched_entity_type='study')
        self.raw_metadata = SeqscapeRawMetadata()
        self.raw_metadata.add_fetched_entities_by_association(sam1_fetched)

        st2 = Study(name='study2', accession_number='ega2', internal_id='2')
        st2_fetched = SeqscapeEntitiesFetched(st2, query_ids=['2'],
                                                       query_id_type='name', query_entity_type='study',
                                                       fetched_entity_type='sample')
        self.raw_metadata.add_fetched_entities_by_association(st2_fetched)

        # Independent entities:
        sam3 = Sample(name='sam3', accession_number='ega3', internal_id='3')
        sam3_fetched = SeqscapeEntitiesFetched(sam3, query_ids=['3'], query_entity_type='study', query_id_type='name',
                                               fetched_entity_type='sample')
        self.raw_metadata.add_fetched_entities(sam3_fetched)

        std4 = Study(name='study4', accession_number='ega4', internal_id='4')
        std4_fetched = SeqscapeEntitiesFetched(std4, query_ids=['4'], query_id_type='name', query_entity_type='sample',
                                               fetched_entity_type='study')
        self.raw_metadata.add_fetched_entities(std4_fetched)

    def test_check_samples_fetched_by_study(self):
        result = self.raw_metadata.check_samples_fetched_by_study()
        self.assertEqual(len(result), 1)

    def test_check_studies_fetched_by_samples(self):
        result = self.raw_metadata.check_studies_fetched_by_samples()
        self.assertEqual(len(result), 1)


class TestCheckEntitiesFetched(unittest.TestCase):

    def test_check_entities_fetched_ok(self):
        sam1 = Sample(name='sam1', accession_number='ega1', internal_id='1')
        sam1_fetched = SeqscapeEntitiesFetched(sam1, query_ids=['1'],
                                                       query_id_type='internal_id', query_entity_type='sample',
                                                       fetched_entity_type='sample')
        result = SeqscapeRawMetadata._check_entities_fetched([sam1_fetched])
        self.assertEqual(len(result), 0)

    def test_check_entities_fetched_missing(self):
        sam1 = Sample(name='sam1', accession_number='ega1', internal_id='1')
        sam1_fetched = SeqscapeEntitiesFetched(sam1, query_ids=['1', '2'],
                                                       query_id_type='internal_id', query_entity_type='sample',
                                                       fetched_entity_type='sample')
        result = SeqscapeRawMetadata._check_entities_fetched([sam1_fetched])
        self.assertEqual(len(result), 1)

    def test_check_entities_fetched_duplication(self):
        sam1 = Sample(name='sam1', accession_number='ega1', internal_id='1')
        sam2 = Sample(name='sam1', accession_number='ega12', internal_id='1')
        sam1_fetched = SeqscapeEntitiesFetched([sam1, sam2], query_ids=['1'],
                                                       query_id_type='internal_id', query_entity_type='sample',
                                                       fetched_entity_type='sample')
        result = SeqscapeRawMetadata._check_entities_fetched([sam1_fetched])
        self.assertEqual(len(result), 1)


class TestCheckRawMetadata(unittest.TestCase):

    def test_check_raw_metadata_1_sample_ok(self):
        raw_metadata = SeqscapeRawMetadata()
        sam1 = Sample(name='sam1', accession_number='ega1', internal_id='1')
        sam1_fetched = SeqscapeEntitiesFetched(sam1, query_ids=['1'],
                                                       query_id_type='internal_id', query_entity_type='sample',
                                                       fetched_entity_type='sample')
        raw_metadata.add_fetched_entities(sam1_fetched)
        result = raw_metadata.check_raw_metadata()
        self.assertEqual([], result)

    def test_check_raw_metadata_not_ok(self):
        raw_metadata = SeqscapeRawMetadata()
        sam1 = Sample(name='sam1', accession_number='ega1', internal_id='1')
        sam1_fetched = SeqscapeEntitiesFetched(sam1, query_ids=['1'],
                                                       query_id_type='internal_id', query_entity_type='sample',
                                                       fetched_entity_type='sample')
        std1 = Study(name='std1', accession_number='ega2', internal_id='2')
        std1_fetched = SeqscapeEntitiesFetched(std1, query_ids=['2'],
                                                       query_id_type='internal_id', query_entity_type='sample',
                                                       fetched_entity_type='study')
        raw_metadata.add_fetched_entities(sam1_fetched)
        raw_metadata.add_fetched_entities_by_association(std1_fetched)
        result = raw_metadata.check_raw_metadata()
        self.assertEqual(1, len(result))


class TestSeqscapeMetadata(unittest.TestCase):

    def test_from_raw_metadata(self):
        raw_metadata = SeqscapeRawMetadata()
        sam1 = Sample(name='sam1', accession_number='ega1', internal_id='1')
        sam1_fetched = SeqscapeEntitiesFetched(sam1, query_ids=['1'],
                                                       query_id_type='internal_id', query_entity_type='sample',
                                                       fetched_entity_type='sample')
        raw_metadata.add_fetched_entities(sam1_fetched)

        lib1 = Library(name='lib1', internal_id='2')
        lib1_fetched = SeqscapeEntitiesFetched(lib1, query_ids=['2'], query_id_type='name', query_entity_type='library',
                                               fetched_entity_type='library')
        raw_metadata.add_fetched_entities(lib1_fetched)

        metadata = SeqscapeMetadata.from_raw_metadata(raw_metadata)
        self.assertListEqual(metadata.get_samples(), [sam1])
        self.assertListEqual(metadata.get_libraries(), [lib1])


    def test_extract_list_of_ids_from_entities_ok(self):
        sam1 = Sample(name='sam1', accession_number='ega1', internal_id='1')
        sam2 = Sample(name='sam2', accession_number='ega2', internal_id='2')
        entities = [sam1, sam2]
        names = SeqscapeMetadata._extract_list_of_ids_from_entities(entities, 'name')
        self.assertSetEqual(set(names), set(['sam1', 'sam2']))

        internal_ids = SeqscapeMetadata._extract_list_of_ids_from_entities(entities, 'internal_id')
        self.assertSetEqual(set(internal_ids), set(['1', '2']))

        acc_nrs = SeqscapeMetadata._extract_list_of_ids_from_entities(entities, 'accession_number')
        self.assertSetEqual(set(acc_nrs), set(['ega1', 'ega2']))

    def test_extract_list_of_ids_from_entities_ok(self):
        sam1 = Sample(name='sam1', accession_number='ega1', internal_id='1')
        sam2 = Sample(accession_number='ega2', internal_id='2')
        entities = [sam1, sam2]
        names = SeqscapeMetadata._extract_list_of_ids_from_entities(entities, 'name')
        self.assertSetEqual(set(names), set(['sam1']))

        internal_ids = SeqscapeMetadata._extract_list_of_ids_from_entities(entities, 'internal_id')
        self.assertSetEqual(set(internal_ids), set(['1', '2']))

        acc_nrs = SeqscapeMetadata._extract_list_of_ids_from_entities(entities, 'accession_number')
        self.assertSetEqual(set(acc_nrs), set(['ega1', 'ega2']))


    def test_group_entity_ids_by_id_type(self):
        sam1 = Sample(name='sam1', accession_number='ega1', internal_id='1')
        sam2 = Sample(name='sam2', accession_number='ega2', internal_id='2')
        grouped_entities = SeqscapeMetadata._group_entity_ids_by_id_type([sam1, sam2])
        self.assertSetEqual(set(grouped_entities['name']), set(['sam1', 'sam2']))
        self.assertSetEqual(set(grouped_entities['internal_id']), set(['1', '2']))
        self.assertSetEqual(set(grouped_entities['accession_number']), set(['ega1', 'ega2']))


    def test_get_all_sample_ids_grouped_by_id_type_ok(self):
        sam1 = Sample(name='sam1', accession_number='ega1', internal_id='1')
        sam2 = Sample(name='sam2', accession_number='ega2', internal_id='2')
        seqsc_metadata = SeqscapeMetadata(samples=[sam1, sam2])
        result = seqsc_metadata.get_all_sample_ids_grouped_by_id_type()
        expected = {'name': ['sam1', 'sam2'],
                    'accession_number': ['ega1', 'ega2'],
                    'internal_id': ['1', '2']
        }
        self.assertDictEqual(result, expected)


    def test_get_sample_ids_by_id_type_ok(self):
        sam1 = Sample(name='sam1', accession_number='ega1', internal_id='1')
        sam2 = Sample(name='sam2', accession_number='ega2', internal_id='2')
        seqsc_metadata = SeqscapeMetadata(samples=[sam1, sam2])
        result = seqsc_metadata.get_sample_ids_by_id_type('name')
        expected = ['sam1', 'sam2']
        self.assertListEqual(result, expected)


    def test_get_sample_ids_by_id_type_empty(self):
        sam1 = Sample(accession_number='ega1', internal_id='1')
        sam2 = Sample(accession_number='ega2', internal_id='2')
        seqsc_metadata = SeqscapeMetadata(samples=[sam1, sam2])
        result = seqsc_metadata.get_sample_ids_by_id_type('name')
        expected = []
        self.assertListEqual(result, expected)


