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

This file has been created on Mar 02, 2016.
"""

from unittest import TestCase, mock, skip

import config
from mcheck.metadata.seqscape_metadata.seqscape_meta_provider import SeqscapeRawMetadataProvider

@skip
class TestFetchSamplesFromSeqscapeRawMetadataProvider(TestCase):

    def setUp(self):
        self.ss_connection = SeqscapeRawMetadataProvider._get_connection(config.SEQSC_HOST, config.SEQSC_PORT,
                                                                         config.SEQSC_DB_NAME, config.SEQSC_USER)

    def test_fetch_samples_real_samples(self):
        sample_acc_nr = 'EGAN00001192046'
        sample_name = 'SC_BLUE5620006'
        sample_id = '1724102'
        samples_fetched_by_names, samples_fetched_by_ids, samples_fetched_by_accession_nrs = \
            SeqscapeRawMetadataProvider._fetch_samples(self.ss_connection, [sample_name], [sample_id], [sample_acc_nr])
        self.assertEqual(len(samples_fetched_by_accession_nrs.entities_fetched), 1)
        self.assertEqual(len(samples_fetched_by_ids.entities_fetched), 1)
        self.assertEqual(len(samples_fetched_by_names.entities_fetched), 1)

    def test_fetch_samples_nonexisting(self):
        sample_name = ['random']
        samples_fetched_by_names, samples_fetched_by_ids, samples_fetched_by_accession_nrs = \
            SeqscapeRawMetadataProvider._fetch_samples(self.ss_connection, sample_name, None, None)
        self.assertEqual(samples_fetched_by_accession_nrs, None)
        self.assertEqual(samples_fetched_by_names, None)
        self.assertEqual(samples_fetched_by_ids, None)

    def test_fetch_samples_wrong_type_parameter(self):
        sample_name = 'random'
        self.assertRaises(ValueError, SeqscapeRawMetadataProvider._fetch_samples, self.ss_connection, sample_name, None, None)

    def test_fetch_samples_nothing_to_fetch(self):
        self.assertEqual((None, None, None), SeqscapeRawMetadataProvider._fetch_samples(self.ss_connection, None, None, None))

    def test_fetch_samples_only_by_ids(self):
        sample_ids = ['1724102', '1633262']
        samples_fetched_by_names, samples_fetched_by_ids, samples_fetched_by_accession_nrs = \
            SeqscapeRawMetadataProvider._fetch_samples(self.ss_connection, None, sample_ids, None)
        self.assertIsNone(samples_fetched_by_names)
        self.assertEqual(len(samples_fetched_by_ids.entities_fetched), 2)
        self.assertIsNone(samples_fetched_by_accession_nrs)


class TestFetchStudiesFromSeqscapeRawMetadataProvider(TestCase):

    def setUp(self):
        self.ss_connection = SeqscapeRawMetadataProvider._get_connection(config.SEQSC_HOST, config.SEQSC_PORT,
                                                                 config.SEQSC_DB_NAME, config.SEQSC_USER)

    def test_fetch_studies_real_studies(self):
        study_acc_nr = 'EGAS00001000530'
        study_name = 'SEQCAP_Oxford IBD cohort project'
        study_id = '2659'
        studies_fetched_by_names, studies_fetched_by_ids, studies_fetched_nu_acc_nrs = \
            SeqscapeRawMetadataProvider._fetch_studies(self.ss_connection, [study_name], [study_id], [study_acc_nr])
        self.assertEqual(len(studies_fetched_by_ids.entities_fetched), 1)
        self.assertEqual(len(studies_fetched_by_names.entities_fetched), 1)
        self.assertEqual(len(studies_fetched_nu_acc_nrs.entities_fetched), 1)

    def test_fetch_studies_only_one_id(self):
        study_acc_nr = ['EGAS00001000530']
        studies_fetched_by_names, studies_fetched_by_ids, studies_fetched_by_acc_nr = SeqscapeRawMetadataProvider._fetch_studies(self.ss_connection, None, None, study_acc_nr)
        self.assertEqual(len(studies_fetched_by_acc_nr.entities_fetched), 1)
        self.assertIsNone(studies_fetched_by_names)
        self.assertIsNone(studies_fetched_by_ids)

    def test_fetch_studies_nonexisting(self):
        study_id = 'Random'
        studies_fetched_by_names, studies_fetched_by_ids, studies_fetched_by_acc_nr = SeqscapeRawMetadataProvider._fetch_studies(self.ss_connection, None, [study_id], None)
        self.assertIsNone(studies_fetched_by_ids)
        self.assertIsNone(studies_fetched_by_names)
        self.assertIsNone(studies_fetched_by_acc_nr)

    def test_fetch_studies_wrong_type_param(self):
        study_name = 'smth'
        self.assertRaises(ValueError, SeqscapeRawMetadataProvider._fetch_studies, self.ss_connection, None, study_name, None)

@skip
class TestFetchLibrariesFromSeqscapeRawMetadataProvider(TestCase):

    def setUp(self):
        self.ss_connection = SeqscapeRawMetadataProvider._get_connection(config.SEQSC_HOST, config.SEQSC_PORT,
                                                                 config.SEQSC_DB_NAME, config.SEQSC_USER)

    def test_fetch_libraries_real_data(self):
        lib_well_id = '6043755'
        libraries_fetched_by_name, libraries_fetched_by_id = SeqscapeRawMetadataProvider._fetch_libraries(self.ss_connection, None, [lib_well_id])
        self.assertIsNone(libraries_fetched_by_name)
        self.assertEqual(len(libraries_fetched_by_id.entities_fetched), 1)

    def test_fetch_libraries_wrong_type_param(self):
        self.assertRaises(ValueError, SeqscapeRawMetadataProvider._fetch_libraries, self.ss_connection, None, 123)

    def test_fetch_libraries_nonexisting(self):
        lib_name = 'apple'
        lib_id = '-22'
        libraries_fetched_by_name, libraries_fetched_by_id = SeqscapeRawMetadataProvider._fetch_libraries(self.ss_connection, [lib_name], [lib_id])
        self.assertIsNone(libraries_fetched_by_id)
        self.assertIsNone(libraries_fetched_by_name)


@skip
class TestFetchRawMetadata(TestCase):

    def setUp(self):
        self.ss_connection = SeqscapeRawMetadataProvider._get_connection(config.SEQSC_HOST, config.SEQSC_PORT,
                                                                 config.SEQSC_DB_NAME, config.SEQSC_USER)

    def test_fetch_1_sample(self):
        samples = {'name': ['SC_BLUE5620006'],
                   'accession_number': ['EGAN00001192046'],
                   'internal_id': [1724102]
        }
        raw_meta = SeqscapeRawMetadataProvider.fetch_raw_metadata(samples, None, None)
        self.assertEqual(len(raw_meta.get_entities_by_type('sample')), 3)


    def test_fetch_with_sample_names(self):
        samples = {'name': ['SC_BLUE5620006', 'DDD_MAIN6028810']}
        raw_meta = SeqscapeRawMetadataProvider.fetch_raw_metadata(samples, None, None)
        print("Raw metadata: %s" % raw_meta.get_entities_by_type('sample'))
        self.assertEqual(len(raw_meta.get_entities_by_type('sample')), 2)


    def test_fetch_sample_names_empty_ids(self):
        samples = {'name': ['SC_BLUE5620006'],
                   'internal_id': [],
                   'accession_number': []
                   }
        raw_meta = SeqscapeRawMetadataProvider.fetch_raw_metadata(samples, None, None)
        self.assertEqual(len(raw_meta.get_entities_by_type('sample')), 1)

    def test_fetch_with_no_data(self):
        empty_dict = {'name': [],
                   'internal_id': [],
                   'accession_number': []
                   }
        raw_meta = SeqscapeRawMetadataProvider.fetch_raw_metadata(empty_dict, empty_dict, empty_dict)
        self.assertEqual(len(raw_meta.get_entities_by_type('sample')), 0)

    def test_fetch_all_types_of_entities(self):
        samples = {'name': ['SC_BLUE5620006'],
                   'accession_number': ['EGAN00001192046'],
                   'internal_id': [1724102]
        }
        studies = {'name': ["IHTP_ISC_Congenital anosmia 2"],
                   'accession_number': ['EGAS00001001429'],
                   'internal_id': [3724]
        }

        libs = {'name': ['APP5117332 3656641'],
                'internal_id': ['3656641']
        }
        raw_meta = SeqscapeRawMetadataProvider.fetch_raw_metadata(samples, libs, studies)
        self.assertEqual(len(raw_meta.get_entities_by_type('sample')), 3)
        self.assertEqual(len(raw_meta.get_entities_by_type('library')), 2)
        self.assertEqual(len(raw_meta.get_entities_by_type('study')), 3)
