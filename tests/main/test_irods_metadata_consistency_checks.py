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

This file has been created on Jun 22, 2015.
"""

import unittest
from main import irods_metadata_consistency_checks as checks
from seqscape import  models


class TestUtilFunctionsForEntities(unittest.TestCase):

    def test_is_id_missing(self):
        id_type = 'internal_id'
        entities_list = []
        result = checks.is_id_missing(id=1, id_type=id_type, entities=entities_list)
        self.assertEqual(result, True)

        id_type = 'internal_id'
        entities_list = [models.Sample(name='jojo', internal_id=1), models.Sample(name='kiki', internal_id=2)]
        result = checks.is_id_missing(id=1, id_type=id_type, entities=entities_list)
        self.assertEqual(result, False)

        id_type = 'internal_id'
        entities_list = [models.Sample(name='jojo', internal_id=1)]
        result = checks.is_id_missing(id=3, id_type=id_type, entities=entities_list)
        self.assertEqual(result, True)

        id_type = 'name'
        entities_list = [models.Sample(name='SANG2', internal_id=2),]
        result = checks.is_id_missing(id='SANG1', id_type=id_type, entities=entities_list)
        self.assertEqual(result, True)


    def test_is_duplicated(self):
        id_type = 'internal_id'
        result = checks.is_id_duplicated(id=1, id_type=id_type, entities=[])
        self.assertEqual(result, False)

        id_type = 'name'
        result = checks.is_id_duplicated(id='VBSEQ1', id_type=id_type, entities=[
            models.Sample(name='VBSEQ1', internal_id=1, accession_number='EGA1'),
            models.Sample(name='VBSEQ1', internal_id=1)])
        self.assertEqual(result, True)

        id_type = 'internal_id'
        entities = [models.Sample(name='VBSEQ1', internal_id=1, accession_number='EGA1'), models.Sample(name='VBSEQ2', internal_id=1)]
        result = checks.is_id_duplicated(id=1, id_type=id_type, entities=entities)
        self.assertEqual(result, True)

        id_type = 'internal_id'
        entities = [models.Sample(name='VBSEQ1', internal_id=1, accession_number='EGA1'), models.Sample(name='VBSEQ2', internal_id=2)]
        result = checks.is_id_duplicated(id=1, id_type=id_type, entities=entities)
        self.assertEqual(result, False)


class TestIRODSvsSeqscMetadata(unittest.TestCase):

    def test_compare_sample_sets_in_seqsc(self):
        irods_samples = {'name': ['491STDY5478742'], 'accession_number': ['EGAN00001096108'], 'internal_id': [1571544]}
        result = checks.compare_sample_sets_in_seqsc(irods_samples)
        print str(result)
        self.assertEqual(len(result), 0)

        irods_samples = {'name': ['491STDY5478742'], 'accession_number': ['EGAN0000'], 'internal_id': [1571544]}
        result = checks.compare_sample_sets_in_seqsc(irods_samples)
        self.assertEqual(len(result), 1)


class TestGetEntitiesFromSeqscape(unittest.TestCase):

    def test_get_samples_from_seqsc(self):
        identif_list = ['491STDY5478742']
        identif_type = 'name'
        results = checks.get_entities_from_seqscape('sample', identif_list, identif_type)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].internal_id, 1571544)
        self.assertEqual(results[0].accession_number, 'EGAN00001096108')

        identif_list = ['EGAN00001218652']
        identif_type = 'accession_number'
        results = checks.get_entities_from_seqscape('sample', identif_list, identif_type)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, 'SC_WES_INT5899561')
        self.assertEqual(results[0].internal_id, 2040105)


   def test_get_libraries_from_seqsc(self):
        ids_list = ['12219508']
        id_type = 'internal_id'
        result = checks.get_entities_from_seqscape('library', ids_list, id_type)
        self.assertEqual(len(result), 1)