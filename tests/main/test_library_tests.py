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
from main import library_tests


class LibraryMetadataWholeTests(unittest.TestCase):

    # This will fail..cause I commented out these fct, refactored to smth else.
    # @unittest.skipIf(config.RUNNING_LOCATION == 'localhost', "Skipping checks because it runs locally")
    # def test_check_library_metadata(self):
    #     irods_fpath = '/seq/14761/14761_4.bam'
    #     header_metadata = bam_checks.get_header_metadata_from_irods_file(irods_fpath)
    #     irods_metadata = bam_checks.get_irods_metadata(irods_fpath)
    #     result = bam_checks.check_library_metadata(header_metadata, irods_metadata)
    #     self.assertEqual(len(result), 1)

    def test_get_all_possible_libraries_from_seqsc(self):
        ids_list = ['12219508']
        id_type = 'internal_id'
        result = library_tests.search_library_ids_in_different_tables_from_seqsc(ids_list, id_type)
        self.assertEqual(len(result), 1)
