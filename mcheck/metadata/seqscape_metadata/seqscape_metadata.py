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

This file has been created on Nov 09, 2015.
"""

from collections import defaultdict
import collections
from typing import List

from sequencescape import NamedModel, Sample, Study, Library
from mcheck.results.checks_results import CheckResult
from mcheck.results.constants import SEVERITY


class SeqscapeEntityQueryAndResults:
    def __init__(self, entities_fetched, query_ids, query_id_type, query_entity_type, fetched_entity_type):
        """
        This is a class used to store data retrieved from Sequencescape DB.
        It holds entities are fetched from Seqscape when querying by a list of ids of type query_id_type.
        :param entities_fetched: entities fetched from Seqscape
        :param query_id_type: a type of id - e.g. "accession_number", "internal_id", "name"
        :param query_ids: a list of strings = the list of ids that Seqscape was queried by,
        :return:
        """
        if type(entities_fetched) == list:
            self.entities_fetched = entities_fetched
        else:
            self.entities_fetched = [entities_fetched]
        self.query_ids = query_ids
        self.query_id_type = query_id_type
        self.query_entity_type = query_entity_type
        self.fetched_entity_type = fetched_entity_type

    def _find_missing_ids(self) -> List:
        ids_found = [str(getattr(ent, self.query_id_type)) for ent in self.entities_fetched]
        ids_missing = list(set(self.query_ids).difference(set(ids_found)))
        return ids_missing

    def _find_duplicated_ids(self) -> List:
        ids_found = [getattr(ent, self.query_id_type) for ent in self.entities_fetched]
        ids_duplicated = [item for item, count in collections.Counter(ids_found).items() if count > 1]
        return ids_duplicated

    def check_all_ids_were_found(self) -> List:
        problems = []
        ids_missing = self._find_missing_ids()
        if ids_missing:
            problems.append(CheckResult(check_name="Check all ids were found",
                                        error_message="The following ids weren't found in SequencescapeDB: %s " %
                                                      ids_missing))
        return problems

    def check_no_duplicates_found(self) -> List:
        problems = []
        ids_dupl = self._find_duplicated_ids()
        if ids_dupl:
            entities_dupl = [ent for ent in self.entities_fetched if getattr(ent, self.query_id_type) in ids_dupl]
            problems.append(CheckResult("Check for duplicated ids",
                                        error_message="The following ids: %s are duplicated - entities: %s" % (
                                            ids_dupl, entities_dupl)))
        return problems


    def __str__(self):
        return str(self.query_entity_type) + " ID type: " + str(self.query_id_type) + ", query_ids =  " + \
               str(self.query_ids) + ", fetched entities: " + str(self.entities_fetched)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if not type(self) is type(other):
            return False
        return self.query_id_type == other.query_id_type and self.query_ids == other.query_ids and \
               self.entities_fetched == other.entities_fetched and self.query_entity_type == other.query_entity_type

    def __hash__(self):
        return hash(frozenset(self.entities_fetched))


class SeqscapeRawMetadata(object):
    """
    This class holds the metadata fetched from sequencescapeDB before being tested for sanity on its own.
    """

    def __init__(self):
        """
        Constructor - initializez the internal field keeping all the entities by entity type.
        _entities_dict_by_type = { 'sample' : [SeqscapeEntitiesFetchedByIdType(), SeqscapeEntitiesFetchedByIdType(),..]}
        _entities_fetched_by_association = {('sample', 'study'): [SeqscapeEntitiesFetchedBasedOnIds(), ..]}
        :return:
        """
        self._entities_dict_by_type = defaultdict(list)
        self._entities_fetched_by_association = defaultdict(list)   # key: tuple(entity_queried_type, entity_fetched_type)

    def add_fetched_entities(self, query_results: SeqscapeEntityQueryAndResults):
        """
        :param query_results: SeqscapeEntitiesFetchedByIdType object
        :param entity_type: str = the type of entity, can be 'sample', or 'library' or 'study'
        :return:
        """
        if query_results:
            entity_type = query_results.fetched_entity_type
            self._entities_dict_by_type[entity_type].append(query_results)

    def add_all_fetched_entities(self, entities_fetched: List[SeqscapeEntityQueryAndResults]):
        if entities_fetched:
            entity_type = entities_fetched[0].fetched_entity_type
            self._entities_dict_by_type[entity_type].extend(entities_fetched)

    def add_fetched_entities_by_association(self, query_results: SeqscapeEntityQueryAndResults) -> None:
        """
        This method adds a new entry in the dict of entities fetched from Seqscape in association with others.
        :param query_results: list[SeqscapeEntitiesFetchedBasedOnIds] to be added to the internal dict
        :return:
        """
        if query_results and not type(query_results) == SeqscapeEntityQueryAndResults:
            raise ValueError("Expected SeqscapeEntitiesFetched type and got: %s " % str(type(query_results)))
        if query_results:
            entity_type = (query_results.query_entity_type, query_results.fetched_entity_type)
            self._entities_fetched_by_association[entity_type].append(query_results)

    def get_fetched_entities_by_type(self, entity_type: str):
        return self._entities_dict_by_type[entity_type]

    def get_entities_by_type(self, entity_type: str):
        results = []

        for entities in self._entities_dict_by_type[entity_type]:
            results.extend(entities.entities_fetched)
        #     results.extend(entities)
        return results
#        return [ent.entities_fetched for ent in self._entities_dict_by_type[entity_type]]


    def get_entities_without_duplicates_by_entity_type(self, entity_type: str) -> List[NamedModel]:
        entities_by_type = self.get_entities_by_type(entity_type)
        print("Entities by type: %s" % entities_by_type)
        all_entities = set(entities_by_type)
        # for ent in entities_by_type:
        #     # entities_by_type = set()
        #     # entities_by_type.update(ent)
        #     all_entities.update(entities_by_type)
        return list(all_entities)


    def get_all_fetched_entity_types(self) -> List[str]:
        return list(self._entities_dict_by_type.keys())

    def get_all_entities_from_query_results(self) -> List[NamedModel]:
        """
        Returns a list of SeqscapeEntitiesFetchedBasedOnIds for all the entity types concatenated together.
        """
        res = []
        for v in self._entities_dict_by_type.values():
            res.extend(v)
        return res


    def get_all_fetched_entities_by_association(self) -> List[SeqscapeEntityQueryAndResults]:
        return self._entities_fetched_by_association

    def get_all_fetched_entities_by_association_by_type(self, query_entity_type, fetched_entity_type):
        return self._entities_fetched_by_association[(query_entity_type, fetched_entity_type)]

    def get_all_entities_by_association_by_type(self, query_entity_type: str, fetched_entity_type:str) -> List[SeqscapeEntityQueryAndResults]:
        query_results = self._entities_fetched_by_association[(query_entity_type, fetched_entity_type)]
        res = []
        for v in query_results:
            res.extend(v.entities_fetched)
        return res


    @classmethod
    def _check_by_comparison_entities_fetched_by_different_id_types(cls, query_results: List[SeqscapeEntityQueryAndResults]) -> List:
        problems = []
        for i in range(1, len(query_results)):
            entities_1 = query_results[i - 1]
            entities_2 = query_results[i]
            if not set(entities_1.entities_fetched) == set(entities_2.entities_fetched):
                id_type_1 = entities_1.query_id_type
                id_type_2 = entities_2.query_id_type
                diff_1 = set(entities_1.entities_fetched).difference(set(entities_2.entities_fetched))
                diff_2 = set(entities_2.entities_fetched).difference(set(entities_1.entities_fetched))
                error_message = ""
                if diff_1:
                    error_message = "Extra %s found when querying by %s compared to %s: %s." % (
                        entities_1.query_entity_type, id_type_1, id_type_2, diff_1)
                if diff_2:
                    error_message += "Extra %s found when querying by %s compared to %s: %s." % (
                        entities_2.query_entity_type, id_type_2, id_type_1, diff_2)
                if not diff_2 and not diff_1:
                    raise ValueError("Somehow the entity sets are different, but I can't detect any difference.")

                problems.append(CheckResult(check_name="Check entities fetched by different types of ids",
                                            error_message=error_message))
        return problems

    @classmethod
    def _check_entities_fetched(cls, query_results: List[SeqscapeEntityQueryAndResults]) -> None:
        problems = []
        for entity_fetched in query_results:
            problems.extend(entity_fetched.check_all_ids_were_found())
            problems.extend(entity_fetched.check_no_duplicates_found())
        return problems

    def check_studies_fetched_by_samples(self):
        problems = []
        if not self.get_entities_by_type('sample'):
            return problems
        studies_by_samples = self.get_all_entities_by_association_by_type('sample', 'study')
        studies = self.get_entities_by_type('study')
        if not set(studies_by_samples).issubset(set(studies)):
            diff = set(studies_by_samples).difference(set(studies))
            print("Difference: %s" % diff)
            error_msg = "These samples: %s are associated with the study(s): %s but aren't part of metadata" % (diff, studies)
            problems.append(CheckResult(check_name="Check the samples returned by querying by study(s)", error_message=error_msg, severity=SEVERITY.WARNING))
        return problems


    def check_samples_fetched_by_studies(self):
        problems = []
        if not self.get_entities_by_type('study'):
            return problems
        samples_by_studies = self.get_all_entities_by_association_by_type('study', 'sample')
        samples = self.get_entities_by_type('sample')
        print("Samples by studies: %s" % samples_by_studies)
        print("Samples: %s" % samples)
        if not set(samples).issubset(set(samples_by_studies)):
            diff = set(samples).difference(set(samples_by_studies))
            print("Difference: %s" % diff)
            error_msg = "These studies:%s are associated with the samples: %s but aren't part of metadata " % (diff, samples)
            problems.append(CheckResult(check_name="Check the studies returned by querying by sample(s)", error_message=error_msg, severity=SEVERITY.CRITICAL))
        return problems


    def check_raw_metadata(self) -> List:
        """
        Checks the raw metadata and throws exceptions if any problem is found
        :param raw_metadata:
        :return:
        """
        problems = []
        entity_types = self.get_all_fetched_entity_types()
        for ent_type in entity_types:
            entities_fetched = self.get_fetched_entities_by_type(ent_type)
            problems.extend(self._check_entities_fetched(entities_fetched))
            problems.extend(self._check_by_comparison_entities_fetched_by_different_id_types(entities_fetched))
            problems.extend(self.check_studies_fetched_by_samples())
            problems.extend(self.check_samples_fetched_by_studies())
        return problems


    def __str__(self):
        return "ENTITIES FETCHED: " + str(self._entities_dict_by_type) + " and ASSOCIATED ENTITIED: " + str(
            self._entities_fetched_by_association)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return type(self) is type(other) and self._entities_dict_by_type == other._entities_dict_by_type

    def __hash__(self):
        return hash(
            frozenset(self._entities_dict_by_type))  # + hash(frozenset(self.libraries)) + hash(frozenset(self.studies))


class SeqscapeMetadata:
    """
    This class holds the metadata that has been tested for sanity and is meant to be used
    for comparison with other metadata (fetched from different sources).
    """

    def __init__(self, samples=None, libraries=None, studies=None):
        """
        :param samples: a dict like: {'internal_id': [1,2,3], 'name': ['s1',..], 'accession_number': []}
        :param libraries: a dict like above
        :param studies: a dict like above
        :return:
        """
        self._samples = samples
        self._libraries = libraries
        self._studies = studies

        # I think these fields are used only for self-checks, not for the metadata to be "exported"
        # to be compared with other types of metadata
        # self.samples_by_study = samples_by_study
        # self.studies_by_sample = studies_by_sample

    @classmethod
    def _extract_list_of_ids_from_entities(cls, entities: List, id_type):
        return [getattr(ent, id_type) for ent in entities if hasattr(ent, id_type) and getattr(ent, id_type) is not None]

    @classmethod
    def _group_entity_ids_by_id_type(cls, entities):
        return {'name': cls._extract_list_of_ids_from_entities(entities, 'name'),
                'accession_number': cls._extract_list_of_ids_from_entities(entities, 'accession_number'),
                'internal_id': cls._extract_list_of_ids_from_entities(entities, 'internal_id')
        }

    def get_samples(self):
        return self._samples

    def get_all_sample_ids_grouped_by_id_type(self):
        return self._group_entity_ids_by_id_type(self._samples)

    def get_sample_ids_by_id_type(self, id_type: str):
        return self._group_entity_ids_by_id_type(self._samples).get(id_type)

    def get_libraries(self):
        return self._libraries

    def get_all_library_ids_grouped_by_id_type(self):
        return self._group_entity_ids_by_id_type(self._libraries)

    def get_library_ids_by_id_type(self, id_type: str) -> List:
        return self._group_entity_ids_by_id_type(self._libraries).get(id_type)

    def get_studies(self):
        return self._studies

    def get_all_study_ids_group_by_id_type(self):
        return self._group_entity_ids_by_id_type(self._studies)

    def get_study_ids_by_id_type(self, id_type) -> List:
        return self._group_entity_ids_by_id_type(self._studies).get(id_type)

    @staticmethod
    def from_raw_metadata(raw_metadata: SeqscapeRawMetadata):
        """
        This method creates an SeqscapeMetadata object based on a SeqqscapeRawFetchedMetadata
        :param raw_metadata:
        :return:
        """
        ss_metadata = SeqscapeMetadata()
        ss_metadata._samples = raw_metadata.get_entities_without_duplicates_by_entity_type('sample')
        ss_metadata._libraries = raw_metadata.get_entities_without_duplicates_by_entity_type('library')
        ss_metadata._studies = raw_metadata.get_entities_without_duplicates_by_entity_type('study')
        return ss_metadata


    def __str__(self):
        return "SAMPLE: " + str(self._samples) + ", LIBRARIES: " + str(self._libraries) + ", STUDIES: " + str(
            self._studies)

    def __repr__(self):
        return self.__str__()