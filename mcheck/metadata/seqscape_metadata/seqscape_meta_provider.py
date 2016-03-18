"""
Copyright (C) 2015  Genome Research Ltd.

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

This file has been created on Nov 16, 2015.
"""

import typing
from sequencescape import connect_to_sequencescape, Sample, Study, Library
from mcheck.metadata.seqscape_metadata.seqscape_metadata import SeqscapeRawMetadata, SeqscapeEntityQueryAndResults
import config


class SeqscapeRawMetadataProvider:
    @classmethod
    def _get_connection(cls, host, port, db_name, user):
        return connect_to_sequencescape("mysql://" + user + ":@" + host + ":" + str(port) + "/" + db_name)

    @classmethod
    def _fetch_samples(cls, ss_connection, sample_names: typing.List[str], sample_ids: typing.List[str],
                       sample_accession_nrs: typing.List[str]):
        if sample_names and type(sample_names) is not list:
            raise ValueError("Sample_names parameter should be a list, and is a %s" % str(type(sample_names)))
        if sample_ids and type(sample_ids) is not list:
            raise ValueError("Sample_ids parameter should be a list and is a %s" % str(type(sample_ids)))
        if sample_accession_nrs and type(sample_accession_nrs) is not list:
            raise ValueError(
                "Sample_accession_numbers parameter should be a list and is a %s" % str(type(sample_accession_nrs)))

        samples_fetched_by_name = None
        if sample_names:
            print("Sample names: %s" % sample_names)
            samples_by_name = ss_connection.sample.get_by_name(sample_names)
            print("Samples by name found: %s" % samples_by_name)
            if samples_by_name:
                samples_fetched_by_name = SeqscapeEntityQueryAndResults(samples_by_name,
                                                                  query_ids=sample_names,
                                                                  query_id_type='name',
                                                                  query_entity_type='sample',
                                                                  fetched_entity_type='sample')
        samples_fetched_by_id = None
        if sample_ids:
            samples_by_id = ss_connection.sample.get_by_id(sample_ids)
            if samples_by_id:
                samples_fetched_by_id = SeqscapeEntityQueryAndResults(samples_by_id,
                                                                query_ids=sample_ids,
                                                                query_id_type='internal_id',
                                                                query_entity_type='sample',
                                                                fetched_entity_type='sample')
        samples_fetched_by_accession_nr = None
        if sample_accession_nrs:
            samples_by_accession_nr = ss_connection.sample.get_by_accession_number(sample_accession_nrs)
            if samples_by_accession_nr:
                samples_fetched_by_accession_nr = SeqscapeEntityQueryAndResults(samples_by_accession_nr,
                                                                          query_ids=sample_accession_nrs,
                                                                          query_id_type='accession_number',
                                                                          query_entity_type='sample',
                                                                          fetched_entity_type='sample')
        return samples_fetched_by_name, samples_fetched_by_id, samples_fetched_by_accession_nr


    @classmethod
    def _fetch_studies(cls, ss_connection, study_names: typing.List[str], study_ids: typing.List[str],
                       study_accession_nrs: typing.List[str]) -> typing.Tuple:
        if study_names and type(study_names) is not list:
            raise ValueError("Study_names parameter should be a list and it is a %s." % str(type(study_names)))
        if study_ids and type(study_ids) is not list:
            raise ValueError("Study_ids parameter should be a list and it is a %s" % str(type(study_ids)))
        if study_accession_nrs and type(study_accession_nrs) is not list:
            raise ValueError(
                "Study_accession_nrs parameter should be a list and it is a %s" % str(type(study_accession_nrs)))

        studies_fetched_by_name = None
        if study_names:
            studies_by_name = ss_connection.study.get_by_name(study_names)
            if studies_by_name:
                studies_fetched_by_name = SeqscapeEntityQueryAndResults(studies_by_name,
                                                                  query_ids=study_names,
                                                                  query_id_type='name',
                                                                  query_entity_type='study',
                                                                  fetched_entity_type='study')

        studies_fetched_by_accession_nr = None
        if study_accession_nrs:
            studies_by_accession_nr = ss_connection.study.get_by_accession_number(study_accession_nrs)
            if studies_by_accession_nr:
                studies_fetched_by_accession_nr = SeqscapeEntityQueryAndResults(studies_by_accession_nr,
                                                                          query_ids=study_accession_nrs,
                                                                          query_id_type='accession_number',
                                                                          query_entity_type='study',
                                                                          fetched_entity_type='study')

        studies_fetched_by_id = None
        if study_ids:
            studies_by_id = ss_connection.study.get_by_id(study_ids)
            if studies_by_id:
                studies_fetched_by_id = SeqscapeEntityQueryAndResults(studies_by_id,
                                                                query_ids=study_ids,
                                                                query_id_type='internal_id',
                                                                query_entity_type='study',
                                                                fetched_entity_type='study')
        return studies_fetched_by_name, studies_fetched_by_id, studies_fetched_by_accession_nr


    @classmethod
    def _fetch_libraries(cls, ss_connection, library_names: typing.List[str], library_ids: typing.List[str]):
        if library_names and type(library_names) is not list:
            raise ValueError("Library_names parameter should be a list and it is a %s" % str(type(library_names)))
        if library_ids and type(library_ids) is not list:
            raise ValueError("Library_ids parameter should be a list and it is a %s" % str(type(library_ids)))

        libraries_fetched_by_id = None
        if library_ids:
            libraries_by_id = ss_connection.library.get_by_id(library_ids)
            if not libraries_by_id:
                libraries_by_id = ss_connection.well.get_by_id(library_ids)
            if not libraries_by_id:
                libraries_by_id = ss_connection.multiplexed_library.get_by_id(library_ids)

            if libraries_by_id:
                libraries_fetched_by_id = SeqscapeEntityQueryAndResults(libraries_by_id,
                                                                  query_ids=library_ids,
                                                                  query_id_type='internal_id',
                                                                  query_entity_type='library',
                                                                  fetched_entity_type='library')
        libraries_fetched_by_name = None
        if library_names:
            libraries_by_name = ss_connection.library.get_by_name(library_names)
            if libraries_by_name:
                libraries_fetched_by_name = SeqscapeEntityQueryAndResults(libraries_by_name,
                                                                    query_ids=library_names,
                                                                    query_id_type='name',
                                                                    query_entity_type='library',
                                                                    fetched_entity_type='library')
        return libraries_fetched_by_name, libraries_fetched_by_id

    @classmethod
    def _fetch_samples_for_studies(cls, ss_connection, studies):
        print("Studies: %s" % studies)
        samples = ss_connection.sample.get_associated_with_study(studies)
        if samples:
            samples_fetched = SeqscapeEntityQueryAndResults(samples, query_ids=studies, query_id_type='whole study', query_entity_type='study', fetched_entity_type='sample')
            return samples_fetched
        return None

    @classmethod
    def _fetch_studies_for_samples(cls, ss_connection, samples):
        print("Fetch studies for samples where samples = %s" % samples)
        studies = ss_connection.study.get_associated_with_sample(samples)
        if studies:
            studies_fetched = SeqscapeEntityQueryAndResults(studies, query_ids=samples, query_id_type='whole sample', query_entity_type='sample', fetched_entity_type='study')
            return studies_fetched
        return None

    @classmethod
    def fetch_raw_metadata(cls, samples: typing.Mapping, libraries: typing.Mapping, studies: typing.Mapping) -> SeqscapeRawMetadata:
        raw_meta = SeqscapeRawMetadata()
        ss_connection = cls._get_connection(config.SEQSC_HOST, config.SEQSC_PORT, config.SEQSC_DB_NAME,
                                            config.SEQSC_USER)
        if samples:
            samples_fetched_by_names, samples_fetched_by_ids, samples_fetched_by_accession_nrs = \
                cls._fetch_samples(ss_connection, samples.get('name'), samples.get('internal_id'), samples.get('accession_number'))
            raw_meta.add_fetched_entities(samples_fetched_by_names)
            raw_meta.add_fetched_entities(samples_fetched_by_accession_nrs)
            raw_meta.add_fetched_entities(samples_fetched_by_ids)

            samples_set = raw_meta.get_entities_without_duplicates_by_entity_type('sample')
            studies_for_samples = cls._fetch_studies_for_samples(ss_connection, samples_set)
            raw_meta.add_fetched_entities_by_association(studies_for_samples)

        if studies:
            studies_fetched_by_names, studies_fetched_by_ids, studies_fetched_by_accession_nrs = \
                cls._fetch_studies(ss_connection, studies.get('name'), studies.get('internal_id'), studies.get('accession_number'))
            raw_meta.add_fetched_entities(studies_fetched_by_accession_nrs)
            raw_meta.add_fetched_entities(studies_fetched_by_ids)
            raw_meta.add_fetched_entities(studies_fetched_by_names)

            # Getting the sample-study associations:
            studies_set = raw_meta.get_entities_without_duplicates_by_entity_type('study')
            samples_for_study = cls._fetch_samples_for_studies(ss_connection, studies_set)
            raw_meta.add_fetched_entities_by_association(samples_for_study)

        if libraries:
            libraries_fetched_by_names, libraries_fetched_by_ids = \
                cls._fetch_libraries(ss_connection, libraries.get('name'), libraries.get('internal_id'))
            raw_meta.add_fetched_entities(libraries_fetched_by_names)
            raw_meta.add_fetched_entities(libraries_fetched_by_ids)

        return raw_meta