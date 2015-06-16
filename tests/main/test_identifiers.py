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

This file has been created on Jun 15, 2015.
"""

import unittest
from main import identifiers

class TestEntityIdentifier(unittest.TestCase):

    def test_guess_identifier_type(self):

        # Tests on sample identifiers
        identif = 'EGAN00001033157'
        identif_name = identifiers.guess_identifier_type(identif)
        self.assertEqual(identif_name, 'accession_number')

        identif = 808346
        identif_name = identifiers.guess_identifier_type(identif)
        self.assertEqual(identif_name, 'internal_id')

        identif = '808346'
        identif_name = identifiers.guess_identifier_type(identif)
        self.assertEqual(identif_name, 'internal_id')

        identif = '2294STDY5395187'
        identif_name = identifiers.guess_identifier_type(identif)
        self.assertEqual(identif_name, 'name')

        identif = 'VBSEQ5231029'
        identif_name = identifiers.guess_identifier_type(identif)
        self.assertEqual(identif_name, 'name')


        # Tests on library identifiers - same ones actually (id, name)
        identif = '3656641'
        identif_name = identifiers.guess_identifier_type(identif)
        self.assertEqual(identif_name, 'internal_id')

        identif = 'bcX98J21 1'
        identif_name = identifiers.guess_identifier_type(identif)
        assert_that(identif_name, equal_to('name'))