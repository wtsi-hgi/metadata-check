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

This file has been created on Jun 19, 2015.
"""

import unittest
import seqscape.queries as seqsc
from main import library_tests

class TestSeqscapeQueries(unittest.TestCase):

    def test_get_samples_from_seqsc(self):
        identif_list = ['491STDY5478742']
        identif_type = 'name'
        results = seqsc.query_all_samples_as_batch(identif_list, identif_type)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].internal_id, 1571544)
        self.assertEqual(results[0].accession_number, 'EGAN00001096108')

        identif_list = ['EGAN00001218652']
        identif_type = 'accession_number'
        results = seqsc.query_all_samples_as_batch(identif_list, identif_type)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, 'SC_WES_INT5899561')
        self.assertEqual(results[0].internal_id, 2040105)


   def test_get_libraries_from_seqsc(self):
        ids_list = ['12219508']
        id_type = 'internal_id'
        result = library_tests.search_library_ids_in_different_tables_from_seqsc(ids_list, id_type)
        self.assertEqual(len(result), 1)
