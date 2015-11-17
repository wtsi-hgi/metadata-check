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

from main.seqscape_metadata import SeqscapeRawFetchedMetadata, SeqscapeMetadata, SeqscapeEntitiesFetchedBasedOnIds
from sequencescape import connect_to_sequencescape, Sample, Study, Library, MultiplexedLibrary, Well, Model


class SeqscapeRawMetadataProvider:

    @classmethod
    def get_connection(cls, host, port, db_name, user):
        # sequencescape = connect_to_sequencescape("mysql://"+config.SEQSC_USER+":@"+config.SEQSC_HOST+":"+str(config.SEQSC_PORT)+"/"+config.SEQSC_DB_NAME)
        return connect_to_sequencescape("mysql://" + user + ":@" + host + ":" + str(port) + "/" + db_name)

    @classmethod
    def retrieve_samples(cls, ss_connection, sample_names, sample_ids, sample_accession_nrs):
        samples_by_name = ss_connection.sample.get_by_name(sample_names)
        samples_fetched_by_name = SeqscapeEntitiesFetchedBasedOnIds(samples_by_name,
                                                                    query_ids=sample_names,
                                                                    query_id_type='name',
                                                                    query_entity_type='sample',
                                                                    fetched_entity_type='sample')

        samples_by_id = ss_connection.sample.get_by_id(sample_ids)
        samples_fetched_by_id = SeqscapeEntitiesFetchedBasedOnIds(samples_by_id,
                                                                  query_ids=sample_ids,
                                                                  query_id_type='internal_id',
                                                                  query_entity_type='sample',
                                                                  fetched_entity_type='sample')

        samples_by_accession_nr = ss_connection.sample.get_by_accession_number(sample_accession_nrs)
        samples_fetched_by_accession_nr = SeqscapeEntitiesFetchedBasedOnIds(samples_by_accession_nr,
                                                                            query_ids=sample_accession_nrs,
                                                                            query_id_type='accession_number',
                                                                            query_entity_type='sample',
                                                                            fetched_entity_type='sample')

        return samples_fetched_by_name, samples_fetched_by_id, samples_fetched_by_accession_nr

    @classmethod
    def retrieve_studies(cls, ss_connection, study_names, study_ids, study_accession_nrs):
        studies_by_name = ss_connection.study.get_by_name(study_names)
        studies_fetched_by_name = SeqscapeEntitiesFetchedBasedOnIds(studies_by_name,
                                                                    query_ids=study_names,
                                                                    query_id_type='name',
                                                                    query_entity_type='study',
                                                                    fetched_entity_type='study'
        )

        studies_by_accession_nr = ss_connection.study.get_by_accession_number(study_accession_nrs)
        studies_fetched_by_accession_nr = SeqscapeEntitiesFetchedBasedOnIds(studies_by_accession_nr,
                                                                            query_ids=study_accession_nrs,
                                                                            query_id_type='accession_number',
                                                                            query_entity_type='study',
                                                                            fetched_entity_type='study'
        )

        studies_by_id = ss_connection.study.get_by_id(study_ids)
        studies_fetched_by_id = SeqscapeEntitiesFetchedBasedOnIds(studies_by_id,
                                                                  query_ids=study_ids,
                                                                  query_id_type='internal_id',
                                                                  query_entity_type='study',
                                                                  fetched_entity_type='study'
        )

        return studies_fetched_by_name, studies_fetched_by_id, studies_fetched_by_accession_nr


    @classmethod
    def retrieve_libraries(cls, ss_connection, library_names, library_ids):
        libraries_by_id = ss_connection.library.get_by_id(library_ids)
        if not libraries_by_id:
            libraries_by_id = ss_connection.well.get_by_id(library_ids)
        if not libraries_by_id:
            libraries_by_id = ss_connection.multiplexed_library(library_ids)

        libraries_fetched_by_id = SeqscapeEntitiesFetchedBasedOnIds(libraries_by_id,
                                                                    query_ids=library_ids,
                                                                    query_id_type='internal_id',
                                                                    query_entity_type='library',
                                                                    fetched_entity_type='library')

        # if i_meta.libraries['name']:
        libraries_by_name = ss_connection.library.get_by_name(library_names)
        libraries_fetched_by_name = SeqscapeEntitiesFetchedBasedOnIds(libraries_by_name,
                                                                      query_ids=library_names,
                                                                      query_id_type='name',
                                                                      query_entity_type='library',
                                                                      fetched_entity_type='library')
        return libraries_fetched_by_name, libraries_fetched_by_id

    @classmethod
    def retrieve_samples_for_studies(cls, ss_connection, studies):
        return ss_connection.sample.get_associated_with_study(studies)

    @classmethod
    def retrieve_studies_for_samples(cls, ss_connection, samples):
        return ss_connection.study.get_associated_with_sample(samples)

    @classmethod
    def retrieve_raw_metadata(cls, samples, libraries, studies):
        import config

        ss_connection = cls.get_connection(config.SEQSC_HOST, config.SEQSC_PORT, config.SEQSC_DB_NAME,
                                            config.SEQSC_USER)

        samples_fetched_by_names, samples_fetched_by_ids, samples_fetched_by_accession_nrs = \
            cls.retrieve_samples(ss_connection, samples['name'], samples['internal_id'], samples['accession_number'])

        studies_fetched_by_names, studies_fetched_by_ids, studies_fetched_by_accession_nrs = \
            cls.retrieve_studies(ss_connection, studies['name'], studies['internal_id'], studies['accession_number'])

        libraries_fetched_by_names, libraries_fetched_by_ids = cls.retrieve_libraries(ss_connection, libraries['name'],
                                                                                       libraries['internal_id'])
        raw_meta = SeqscapeRawFetchedMetadata()
        raw_meta.add_fetched_entities(samples_fetched_by_names)
        raw_meta.add_fetched_entities(samples_fetched_by_accession_nrs)
        raw_meta.add_fetched_entities(samples_fetched_by_ids)

        raw_meta.add_fetched_entities(studies_fetched_by_accession_nrs)
        raw_meta.add_fetched_entities(studies_fetched_by_ids)
        raw_meta.add_fetched_entities(studies_fetched_by_names)

        raw_meta.add_fetched_entities(libraries_fetched_by_names)
        raw_meta.add_fetched_entities(libraries_fetched_by_ids)


        # Getting the sample-study associations:
        studies_set = raw_meta.get_entities_without_duplicates_by_entity_type('study')
#        print("UNIQ STUDIES: :::::::::::::::::::::", studies_set)
        samples_for_study = cls.retrieve_samples_for_studies(ss_connection, studies_set)

        raw_meta.add_fetched_entities_by_association(samples_for_study)
#        print("SAMPLES FOR STUDYYYYYYYYYYYYYYYYYYYY : ", samples_for_study)


        samples_set = raw_meta.get_entities_without_duplicates_by_entity_type('sample')
#        print("Samples UNIQ:::::::::::::::::::::", samples_set)
        studies_for_samples = cls.retrieve_studies_for_samples(ss_connection, samples_set)


        raw_meta.add_fetched_entities_by_association(studies_for_samples)
#        print("Studies for SAMPLESSSS: ", studies_for_samples)

        return raw_meta