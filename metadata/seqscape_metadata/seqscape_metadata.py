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
from typing import List
import collections

from results.checks_results import CheckResult
from results.constants import SEVERITY


# class CheckResult:
#
# def __init__(self, check_name, executed=True, result=RESULT.FAILURE.value, severity=SEVERITY.IMPORTANT.value, error_message=None):
# self.check_name = check_name
# self.severity = severity
# self.error_message = error_message
# self.executed = executed
#         self.result = result        # Can be: FAILURE, SUCCESSFUL, NONE - if the test wasn't executed

# example of usage:
# if not self._is_true_comparison(actual_count, threshold, avu_count.operator):
#                 error_msg = "Attribute: " + str(avu_count.attribute) + " appears: " + str(actual_count) + \
#                             " and should appear: " + str(avu_count.operator) + " " + str(threshold)
#                 problems.append(CheckResult(check_name="Check attribute count is as configured",
#                                             severity=SEVERITY.IMPORTANT, error_message=error_msg))
#
class SeqscapeEntitiesFetched:
    def __init__(self, entities_fetched, query_ids, query_id_type, query_entity_type, fetched_entity_type):
        """
        This is a class used to store data retrieved from Sequencescape DB.
        It holds entities are fetched from Seqscape when querying by a list of ids of type query_id_type.
        :param entities_fetched: entities fetched from Seqscape
        :param query_id_type: a type of id - e.g. "accession_number", "internal_id", "name"
        :param query_ids: a list of strings = the list of ids that Seqscape was queried by,
        :return:
        """
        self.entities_fetched = entities_fetched
        self.query_ids = query_ids
        self.query_id_type = query_id_type
        self.query_entity_type = query_entity_type
        self.fetched_entity_type = fetched_entity_type

    def _find_missing_ids(self):
        ids_found = [str(getattr(ent, self.query_id_type)) for ent in self.entities_fetched]
        ids_missing = set(ids_found).difference(set(self.query_ids))
        return ids_missing

    def _find_duplicated_ids(self):
        ids_found = [getattr(ent, self.query_id_type) for ent in self.entities_fetched]
        ids_duplicated = [item for item, count in collections.Counter(ids_found).items() if count > 1]
        return ids_duplicated

    def check_all_ids_were_found(self):
        problems = []
        ids_missing = self._find_missing_ids()
        if ids_missing:
            problems.append(CheckResult(check_name="Check all ids were found",
                                        error_message="The following ids weren't found in SequencescapeDB: %s " %
                                                      ids_missing))
        return problems

    def check_no_duplicates_found(self):
        problems = []
        ids_dupl = self._find_duplicated_ids()
        if ids_dupl:
            entities_dupl = [ent for ent in self.entities_fetched if getattr(ent, self.query_id_type) in ids_dupl]
            problems.append(CheckResult("Check for duplicated ids",
                                        error_message="The following ids: %s are duplicated - entities: %s" % (
                                            ids_dupl, entities_dupl)))
        return problems


    def __str__(self):
        return str(self.query_entity_type) + " ID TYPE: " + str(self.query_id_type) + ", query_ids =  " + \
               str(self.query_ids) + ", fetched entities: " + str(self.entities_fetched)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.query_id_type == other.query_id_type and self.query_ids == other.query_ids and \
               self.entities_fetched == other.entities_fetched and self.query_entity_type == other.entity_type

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

    def add_fetched_entities(self, entities_fetched: SeqscapeEntitiesFetched):
        """
        :param entities_fetched: SeqscapeEntitiesFetchedByIdType object
        :param entity_type: str = the type of entity, can be 'sample', or 'library' or 'study'
        :return:
        """
        if entities_fetched:
            entity_type = entities_fetched.fetched_entity_type
            self._entities_dict_by_type[entity_type].append(entities_fetched)

    def add_all_fetched_entities(self, entities_fetched: List[SeqscapeEntitiesFetched]):
        if entities_fetched:
            entity_type = entities_fetched[0].fetched_entity_type
            self._entities_dict_by_type[entity_type].extend(entities_fetched)

    def add_fetched_entities_by_association(self, entities_fetched) -> None:
        """
        This method adds a new entry in the dict of entities fetched from Seqscape in association with others.
        :param entities_fetched: list[SeqscapeEntitiesFetchedBasedOnIds] to be added to the internal dict
        :return:
        """
        if entities_fetched:
            entity_type = (entities_fetched[0].query_entity_type, entities_fetched[0].fetched_entity_type)
            self._entities_fetched_by_association[entity_type] = entities_fetched

    def get_fetched_entities_by_type(self, entity_type: str):
        return self._entities_dict_by_type[entity_type]

    def get_entities_without_duplicates_by_entity_type(self, entity_type: str) -> List[SeqscapeEntitiesFetched]:
        fetched_entities = self.get_fetched_entities_by_type(entity_type)
        all_fetched = set()
        for fetched_ent in fetched_entities:
            entities = set()
            entities.update(fetched_ent.entities_fetched)
            all_fetched.update(entities)
        return list(all_fetched)


    def get_all_fetched_entity_types(self):
        return self._entities_dict_by_type.keys()

    def get_all_fetched_entities(self) -> List[SeqscapeEntitiesFetched]:
        """
        Returns a list of SeqscapeEntitiesFetchedBasedOnIds for all the entity types concatenated together.
        """
        result = []
        for _, fetched_entities in self._entities_dict_by_type:
            result.extend(fetched_entities)
        return result

    def get_fetched_entities_by_association(self):
        return self._entities_fetched_by_association

    def get_fetched_entities_by_association_by_type(self, query_entity_type, fetched_entity_type):
        return self._entities_fetched_by_association[(query_entity_type, fetched_entity_type)]


    # @classmethod
    # def _compare_entity_sets(cls, entities_list: List[SeqscapeEntitiesFetched]) -> List[CheckResult]:
    #     problems = []
    #     for i in range(1, len(entities_list) - 1):
    #         if not set(entities_list[i - 1].entities_fetched) == set(entities_list[i].entities_fetched):
    #             problems.append(CheckResult(check_name="C"))
    #             # problems.append(error_types.DiffEntitiesRetrievedFromSeqscapeByDiffIdTypesError(
    #             #     entity_type=entities_list[i].entity_type,
    #             #     id_type1=entities_list[i].query_id_type,
    #             #     id_type2=entities_list[i - 1].query_id_type,
    #             #     entities_set1=entities_list[i - 1].entities_fetched,
    #             #     entities_set2=entities_list[i].entities_fetched
    #             # ))
    #     return problems


    @classmethod
    def _check_by_comparison_entities_fetched_by_different_id_types(cls, entities_list):
        problems = []
        for i in range(1, len(entities_list) - 1):
            entities_1 = entities_list[i - 1].entities_fetched
            entities_2 = entities_list[i].entities_fetched
            if not set(entities_1) == set(entities_2):
                id_type_1 = entities_1.query_id_type
                id_type_2 = entities_2.query_id_type
                diff_1 = set(entities_1).difference(set(entities_2))
                diff_2 = set(entities_2).difference(set(entities_1))

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
    def _check_entities_fetched(cls, entities_fetched_list: List[SeqscapeEntitiesFetched]) -> None:
        problems = []
        for entity_fetched in entities_fetched_list:
            problems.extend(entity_fetched.check_all_ids_were_found(entity_fetched))
            problems.extend(entity_fetched.check_no_duplicates_found)
        return problems

    def check_samples_fetched_by_study(self):
        problems = []
        samples = self.get_fetched_entities_by_association_by_type('sample', 'study')
        studies = self.get_fetched_entities_by_type('study')
        if not set(samples).issubset(set(studies)):
            diff = set(samples).difference(set(studies))
            error_msg = "Samples that don't appear in the metadata but are associated with the study(s) from metadata: %s that aren't part of metadata: %s" % diff
            problems.append(CheckResult(check_name="Check the samples returned by querying by study(s)", error_message=error_msg, severity=SEVERITY.WARNING))
        return problems


    def check_studies_fetched_by_samples(self):
        problems = []
        studies = self.get_fetched_entities_by_association_by_type('study', 'sample')
        samples = self.get_fetched_entities_by_type('sample')
        if not set(studies).issubset(set(samples)):
            diff = set(studies).issubset(set(samples))
            error_msg = "Studies that don't appear in the metadata but are associated with samples from metadata: %s " % diff
            problems.append(CheckResult(check_name="Check the studies returned by querying by sample(s)", error_message=error_msg, severity=SEVERITY.CRITICAL))
        return problems

    # def check_associated_entities(self):
    #     problems = []
    #     for entity_type_tuple, entities_fetched_list in self._entities_fetched_by_association.items():
    #         entity_type_query_by = entity_type_tuple[0]
    #         entity_type_fetched = entity_type_tuple[1]
    #         entities = self.get_fetched_entities_by_type(entity_type_fetched)
    #         if not set(entities_fetched_list).issubset(set(entities)):
    #             diff = set(entities_fetched_list).difference(set(entities))
    #             error_msg = "%s associated with %s that aren't part of metadata so far: %s" % (entity_type_fetched, entity_type_query_by, diff)
    #             problems.append(CheckResult(check_name="Check the %s returned by querying by %s" % (entity_type_fetched, entity_type_query_by), error_message=error_msg, severity=SEVERITY.WARNING))


    def check_raw_metadata(self):#, raw_metadata: SeqscapeRawMetadata) -> None:
        """
        Checks the raw metadata and throws exceptions if any problem is found
        :param raw_metadata:
        :return:
        """
        problems = []
        entity_types = self.get_all_fetched_entity_types()
        for entity_type in entity_types:
            entities_fetched = self.get_fetched_entities_by_type(entity_type)
            problems.extend(self._check_entities_fetched(entities_fetched))
            problems.extend(self._check_by_comparison_entities_fetched_by_different_id_types(entities_fetched))
            problems.extend(self.check_samples_fetched_by_study())
            problems.extend(self.check_studies_fetched_by_samples())
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
        self.samples = samples
        self.libraries = libraries
        self.studies = studies

        # I think these fields are used only for self-checks, not for the metadata to be "exported"
        # to be compared with other types of metadata
        # self.samples_by_study = samples_by_study
        # self.studies_by_sample = studies_by_sample

    def _extract_list_of_ids_from_entities(self, entities: List, id_type):
        return [getattr(ent, id_type) for ent in entities if hasattr(ent, id_type)]

    def _group_entity_ids_by_id_type(self, entities):
        return {'name': self._extract_list_of_ids_from_entities(entities, 'name'),
                'accession_number': self._extract_list_of_ids_from_entities(entities, 'accession_number'),
                'internal_id': self._extract_list_of_ids_from_entities(entities, 'internal_id')
        }


    @staticmethod
    def from_raw_metadata(raw_metadata: SeqscapeRawMetadata):
        """
        This method creates an SeqscapeMetadata object based on a SeqqscapeRawFetchedMetadata
        :param raw_metadata:
        :return:
        """
        ss_metadata = SeqscapeMetadata()
        samples = raw_metadata.get_entities_without_duplicates_by_entity_type('sample')
        ss_metadata.samples = ss_metadata._group_entity_ids_by_id_type(samples)

        libraires = raw_metadata.get_entities_without_duplicates_by_entity_type('library')
        ss_metadata.libraries = ss_metadata._group_entity_ids_by_id_type(libraires)

        studies = raw_metadata.get_entities_without_duplicates_by_entity_type('study')
        ss_metadata.studies = ss_metadata._group_entity_ids_by_id_type(studies)

        return ss_metadata


    def __str__(self):
        return "SAMPLE: " + str(self.samples) + ", LIBRARIES: " + str(self.libraries) + ", STUDIES: " + str(
            self.studies)

    def __repr__(self):
        return self.__str__()