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

import config
from mcheck.irods.api import iRODSAPI
from mcheck.metadata.irods_metadata import data_types


@unittest.skip
class TestiRODSAPI(unittest.TestCase):

    def setUp(self):
        self.path = '/humgen/projects/serapis_staging/test-metadata/upl-worker.out'
        # First adding an avu:
        self.avu1 = data_types.MetaAVU(attribute='name', value='Irina')
        self.avu2 = data_types.MetaAVU(attribute='name', value='Gabriela')
        iRODSAPI.add_metadata_avu(self.path, self.avu1)


    @unittest.skipIf(config.RUNNING_LOCATION == 'localhost', "Skipping imeta qu test because it runs locally")
    def test_modify_metadata_avu(self):
        iRODSAPI.modify_metadata_avu(self.path, self.avu1, self.avu2)
        avus = iRODSAPI.retrieve_metadata_for_file(self.path)
        self.assertEqual(len(avus), 1)
        self.assertEqual(avus[0].value, 'Gabriela')


    def tearDown(self):
        iRODSAPI.remove_metadata_avu(self.path, self.avu2)