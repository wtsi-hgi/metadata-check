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


class SeqscapeQueriesTests(unittest.TestCase):

    def test_get_samples_from_seqsc(self):
        identif_list = ['491STDY5478742']
        identif_type = 'name'
        results = sample_tests.get_samples_from_seqsc(identif_list, identif_type)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].internal_id, 1571544)
        self.assertEqual(results[0].accession_number, 'EGAN00001096108')

        identif_list = ['EGAN00001218652']
        identif_type = 'accession_number'
        results = sample_tests.get_samples_from_seqsc(identif_list, identif_type)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, 'SC_WES_INT5899561')
        self.assertEqual(results[0].internal_id, 2040105)


class IRODSvsSeqscMetadataTests(unittest.TestCase):

    def test_get_diff_seqsc_and_irods_samples_metadata(self):
        irods_samples = {'name': ['491STDY5478742'], 'accession_number': ['EGAN00001096108'], 'internal_id': [1571544]}
        result = sample_tests.get_diff_seqsc_and_irods_samples_metadata(irods_samples)
        self.assertEqual(len(result), 0)

        irods_samples = {'name': ['491STDY5478742'], 'accession_number': ['EGAN0000'], 'internal_id': [1571544]}
        result = sample_tests.get_diff_seqsc_and_irods_samples_metadata(irods_samples)
        self.assertEqual(len(result), 1)


class SampleMetadataWholeTests(unittest.TestCase):
    pass
    #won't run because I've commented out the fct called
    # @unittest.skipIf(config.RUNNING_LOCATION == 'localhost', "Skipping checks because it runs locally")
    # def test_check_sample_metadata(self):
    #     irods_fpath = '/seq/11010/11010_8#21.bam'
    #     header_metadata = bam_checks.get_header_metadata_from_irods_file(irods_fpath)
    #     irods_metadata = bam_checks.get_irods_metadata(irods_fpath)
    #     result = bam_checks.check_library_metadata(header_metadata, irods_metadata)
    #     self.assertEqual(len(result), 1)

