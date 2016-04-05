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

from mcheck.metadata.common import identifiers


class TestEntityIdentifier(unittest.TestCase):

    def test_is_identifier_when_its_not(self):
        identifier = ''
        self.assertFalse(identifiers.EntityIdentifier.is_identifier(identifier))

        identifier = 'N/A'
        self.assertFalse(identifiers.EntityIdentifier.is_identifier(identifier))

        identifier = 'undefined'
        self.assertFalse(identifiers.EntityIdentifier.is_identifier(identifier))

        identifier = 'unspecified'
        self.assertFalse(identifiers.EntityIdentifier.is_identifier(identifier))

    def test_is_identifier_when_it_is(self):
        identifier = '123'
        self.assertTrue(identifiers.EntityIdentifier.is_identifier(identifier))

        identifier = 'abc'
        self.assertTrue(identifiers.EntityIdentifier.is_identifier(identifier))

    def test_is_name_when_its_not(self):
        identifier = '123.'
        self.assertFalse(identifiers.EntityIdentifier.is_name(identifier))

    def test_is_name_when_it_is(self):
        identifier = '123abc'
        self.assertTrue(identifiers.EntityIdentifier.is_name(identifier))

        identifier = '123'
        self.assertTrue(identifiers.EntityIdentifier.is_name(identifier))

        identifier = 'bc'
        self.assertTrue(identifiers.EntityIdentifier.is_name(identifier))


    def test_is_accession_number_when_its_not(self):
        identifier = 'AAA'
        self.assertFalse(identifiers.EntityIdentifier.is_accession_nr(identifier))

        identifier = '123'
        self.assertFalse(identifiers.EntityIdentifier.is_accession_nr(identifier))

        identifier = 'AB123'
        self.assertFalse(identifiers.EntityIdentifier.is_accession_nr(identifier))

    def test_is_accession_number_when_it_is(self):
        identifier = 'EGAN00001033157'
        self.assertTrue(identifiers.EntityIdentifier.is_accession_nr(identifier))

        identifier = 'ERS123'
        self.assertTrue(identifiers.EntityIdentifier.is_accession_nr(identifier))

        identifier = 'SR123'
        self.assertTrue(identifiers.EntityIdentifier.is_accession_nr(identifier))


    def test_guess_identifier_type_when_its_name(self):
        # Tests on sample identifiers

        identif = '2294STDY5395187'
        identif_name = identifiers.EntityIdentifier.guess_identifier_type(identif)
        self.assertEqual(identif_name, 'name')

        identif = 'VBSEQ5231029'
        identif_name = identifiers.EntityIdentifier.guess_identifier_type(identif)
        self.assertEqual(identif_name, 'name')

        identif = 'bcX98J21 1'
        identif_name = identifiers.EntityIdentifier.guess_identifier_type(identif)
        self.assertEqual(identif_name, 'name')

    def test_guess_identifier_type_when_its_accession_numbers(self):
        identif = 'ERS179268'
        identifier_name = identifiers.EntityIdentifier.guess_identifier_type(identif)
        self.assertEqual(identifier_name, 'accession_number')

        identif = 'EGAN00001033157'
        identif_name = identifiers.EntityIdentifier.guess_identifier_type(identif)
        self.assertEqual(identif_name, 'accession_number')

    def test_guess_identifier_type_when_its_internal_id(self):
        identifier = '132'
        identifier_name = identifiers.EntityIdentifier.guess_identifier_type(identifier)
        self.assertEqual(identifier_name, 'internal_id')

        identif = '3656641'
        identif_name = identifiers.EntityIdentifier.guess_identifier_type(identif)
        self.assertEqual(identif_name, 'internal_id')

        identif = 808346
        identif_name = identifiers.EntityIdentifier.guess_identifier_type(identif)
        self.assertEqual(identif_name, 'internal_id')

        identif = '808346'
        identif_name = identifiers.EntityIdentifier.guess_identifier_type(identif)
        self.assertEqual(identif_name, 'internal_id')

    def test_separate_identifiers_by_type(self):
        ids = ['123']
        ids_dict = identifiers.EntityIdentifier.separate_identifiers_by_type(ids)
        self.assertDictEqual({'internal_id': ['123'], 'name': [], 'accession_number': []}, ids_dict)

        ids = ['EGA123']
        ids_dict = identifiers.EntityIdentifier.separate_identifiers_by_type(ids)
        self.assertDictEqual({'internal_id': [], 'name': [], 'accession_number': ['EGA123']}, ids_dict)

        ids = ['123MYNAME']
        ids_dict = identifiers.EntityIdentifier.separate_identifiers_by_type(ids)
        self.assertDictEqual({'internal_id': [], 'name': ['123MYNAME'], 'accession_number': []}, ids_dict)

        ids = ['123', 'MYNAME', 'ERP123']
        ids_dict = identifiers.EntityIdentifier.separate_identifiers_by_type(ids)
        self.assertDictEqual({'internal_id': ['123'], 'name': ['MYNAME'], 'accession_number': ['ERP123']}, ids_dict)


