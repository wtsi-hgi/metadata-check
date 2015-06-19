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

This file has been created on Feb 10, 2015.
"""


import unittest
from main import sample_tests
from seqscape import models



# def is_id_missing(id, id_type, entities_list):
#     for entity in entities_list:
#         if str(id) == str(getattr(entity, id_type)):
#             return False
#     return True
#
# def is_duplicated(id, id_type, entities_list):
#     for entity in entities_list:
#         if getattr(entity, id_type) == id:
#             return True
#     return False
#
# def get_entities_by_id(id, id_type, entities):
#     result = []
#     for ent in  entities:
#         if getattr(ent, id_type) == id:
#             result.append(ent)
#     return result

class TestUtilFunctionsForEntities(unittest.TestCase):

    def test_is_id_missing(self):
        id_type = 'internal_id'
        entities_list = []
        result = sample_tests.is_id_missing(id=1, id_type=id_type, entities=entities_list)
        self.assertEqual(result, True)

        id_type = 'internal_id'
        entities_list = [models.Sample(name='jojo', internal_id=1), models.Sample(name='kiki', internal_id=2)]
        result = sample_tests.is_id_missing(id=1, id_type=id_type, entities=entities_list)
        self.assertEqual(result, False)

        id_type = 'internal_id'
        entities_list = [models.Sample(name='jojo', internal_id=1)]
        result = sample_tests.is_id_missing(id=3, id_type=id_type, entities=entities_list)
        self.assertEqual(result, True)

        id_type = 'name'
        entities_list = [models.Sample(name='SANG2', internal_id=2),]
        result = sample_tests.is_id_missing(id='SANG1', id_type=id_type, entities=entities_list)
        self.assertEqual(result, True)


    def test_is_duplicated(self):
        id_type = 'internal_id'
        result = sample_tests.is_id_duplicated(id=1, id_type=id_type, entities=[])
        self.assertEqual(result, False)

        id_type = 'name'
        result = sample_tests.is_id_duplicated(id='VBSEQ1', id_type=id_type, entities=[
            models.Sample(name='VBSEQ1', internal_id=1, accession_number='EGA1'),
            models.Sample(name='VBSEQ1', internal_id=1)])
        self.assertEqual(result, True)

        id_type = 'internal_id'
        entities = [models.Sample(name='VBSEQ1', internal_id=1, accession_number='EGA1'), models.Sample(name='VBSEQ2', internal_id=1)]
        result = sample_tests.is_id_duplicated(id=1, id_type=id_type, entities=entities)
        self.assertEqual(result, True)

        id_type = 'internal_id'
        entities = [models.Sample(name='VBSEQ1', internal_id=1, accession_number='EGA1'), models.Sample(name='VBSEQ2', internal_id=2)]
        result = sample_tests.is_id_duplicated(id=1, id_type=id_type, entities=entities)
        self.assertEqual(result, False)



class TestIRODSvsSeqscMetadata(unittest.TestCase):

    def test_compare_sample_sets_in_seqsc(self):
        irods_samples = {'name': ['491STDY5478742'], 'accession_number': ['EGAN00001096108'], 'internal_id': [1571544]}
        result = sample_tests.compare_sample_sets_in_seqsc(irods_samples)
        print str(result)
        self.assertEqual(len(result), 0)

        irods_samples = {'name': ['491STDY5478742'], 'accession_number': ['EGAN0000'], 'internal_id': [1571544]}
        result = sample_tests.compare_sample_sets_in_seqsc(irods_samples)
        self.assertEqual(len(result), 1)


class TestSampleMetadata(unittest.TestCase):
    pass
    #won't run because I've commented out the fct called
    # @unittest.skipIf(config.RUNNING_LOCATION == 'localhost', "Skipping checks because it runs locally")
    # def test_check_sample_metadata(self):
    #     irods_fpath = '/seq/11010/11010_8#21.bam'
    #     header_metadata = bam_checks.get_header_metadata_from_irods_file(irods_fpath)
    #     irods_metadata = bam_checks.get_irods_metadata(irods_fpath)
    #     result = bam_checks.check_library_metadata(header_metadata, irods_metadata)
    #     self.assertEqual(len(result), 1)

