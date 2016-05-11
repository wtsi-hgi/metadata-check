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
    def __init__(self, entities_fetched: NamedModel, query_ids: List, query_id_type: str, query_entity_type: str,
                 fetched_entity_type: str):
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
        self.query_ids = [str(id) for id in query_ids]
        self.query_id_type = query_id_type
        self.query_entity_type = query_entity_type
        self.fetched_entity_type = fetched_entity_type

    def _find_missing_ids(self) -> List:
        ids_found = [str(getattr(ent, self.query_id_type)) for ent in self.entities_fetched]
        ids_missing = list(set(self.query_ids).difference(set(ids_found)))
        return ids_missing

    def _find_duplicated_ids(self) -> List:
        ids_found = [str(getattr(ent, self.query_id_type)) for ent in self.entities_fetched]
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
        self._entities_fetched_by_association = defaultdict(
            list)  # key: tuple(entity_queried_type, entity_fetched_type)

    def add_fetched_entities(self, query_results: SeqscapeEntityQueryAndResults):
        """
        :param query_results: SeqscapeEntitiesFetchedByIdType object
        :param entity_type: str = the type of entity, can be 'sample', or 'library' or 'study'
        :return:
        """
        if query_results:
            entity_type = query_results.fetched_entity_type
            self._entities_dict_by_type[entity_type].append(query_results)

    def add_all_fetched_entities(self, query_results: List[SeqscapeEntityQueryAndResults]):
        if query_results:
            entity_type = query_results[0].fetched_entity_type
            self._entities_dict_by_type[entity_type].extend(query_results)

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
        return results


    def get_entities_without_duplicates_by_entity_type(self, entity_type: str) -> List[NamedModel]:
        entities_by_type = self.get_entities_by_type(entity_type)
        all_entities = set(entities_by_type)
        return all_entities


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

    def get_all_entities_by_association_by_type(self, query_entity_type: str, fetched_entity_type:str) -> List[
        SeqscapeEntityQueryAndResults]:
        query_results = self._entities_fetched_by_association[(query_entity_type, fetched_entity_type)]
        res = []
        for v in query_results:
            res.extend(v.entities_fetched)
        return res


    @classmethod
    def _check_by_comparison_entities_fetched_by_different_id_types(cls, query_results: List[
        SeqscapeEntityQueryAndResults]) -> List:
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
        studies_by_samples_set = set(self.get_all_entities_by_association_by_type('sample', 'study'))
        studies_set = set(self.get_entities_by_type('study'))
        diff_wrong_studies_for_samples_in_irods = studies_set.difference(studies_by_samples_set)
        if not studies_set.issubset(studies_by_samples_set):
            error_msg = "For the %s given seqscape samples, the studies in iRODS: %s and the studies in Seqscape don't agree: %s" % ( str(len(self.get_entities_by_type('sample'))), studies_set, studies_by_samples_set)
            problems.append(
                CheckResult(check_name="Check the samples belong to the same studies in iRODS and Seqscape", error_message=error_msg,
                            severity=SEVERITY.WARNING))
        elif diff_wrong_studies_for_samples_in_irods:
            error_msg = "Studies in Seqscape and in iRODS for %s samples don't agree. Studies in iRODS and not in Seqscape: %s" % (
                str(len(self.get_entities_by_type('sample'))), diff_wrong_studies_for_samples_in_irods)
            problems.append(CheckResult(
                check_name="Check the study in iRODS for the samples given are associated with same sample in Seqscape",
                error_message=error_msg, severity=SEVERITY.IMPORTANT))
        diff_sam_belongs2more_studies = studies_by_samples_set.difference(studies_set)
        if diff_sam_belongs2more_studies:
            error_msg = "Some samples belong to more than one study. For samples: %s we found in Seqscape these studies: %s" % (
                self.get_entities_by_type('sample'), diff_sam_belongs2more_studies)
            problems.append(CheckResult(check_name="Check the studies found in Seqscape when querying by samples",
                                        error_message=error_msg, severity=SEVERITY.WARNING))

        return problems


    def check_samples_fetched_by_studies(self):
        problems = []
        if not self.get_entities_by_type('study'):
            return problems
        samples_by_studies_set = set(self.get_all_entities_by_association_by_type('study', 'sample'))
        samples_set = set(self.get_entities_by_type('sample'))
        diff_not_sequenced_yet = samples_by_studies_set.difference(samples_set)
        if diff_not_sequenced_yet:
            error_msg = "Not all the samples in this study have been sequenced, remaining: %s" % (
                str(len(diff_not_sequenced_yet)))
            problems.append(
                CheckResult(check_name="Check if all samples sequenced", error_message=error_msg,
                            severity=SEVERITY.WARNING))
        if not samples_set.issubset(samples_by_studies_set):
            diff_samples_wrong_study = samples_set.difference(samples_by_studies_set)
            error_msg = "Some samples don't appear under study(s): %s in Sequencescape, but they appear under this study in iRODS. Number of samples: %s, and ids: %s" % (
                self.get_entities_by_type('study'), str(len(diff_samples_wrong_study)), diff_samples_wrong_study)
            problems.append(CheckResult(
                check_name="Check if the sample ids in iRODS for a study belong to the same study in Sqeuencescape ",
                error_message=error_msg, severity=SEVERITY.IMPORTANT))
        return problems


    def check_metadata(self) -> List:
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

    # hmm, it seems that I misunderstood and here everything is a dict of id type - id value...
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
        return [getattr(ent, id_type) for ent in entities if
                hasattr(ent, id_type) and getattr(ent, id_type) is not None]

    @classmethod
    def _group_entity_ids_by_id_type(cls, entities):
        names = cls._extract_list_of_ids_from_entities(entities, 'name')
        accession_nrs = cls._extract_list_of_ids_from_entities(entities, 'accession_number')
        internal_ids = cls._extract_list_of_ids_from_entities(entities, 'internal_id')
        return {'name': {str(name) for name in names},
                'accession_number': {str(acc_nr) for acc_nr in accession_nrs},
                'internal_id': {str(id) for id in internal_ids}
        }

    @property
    def samples(self):
        """
        By default when accessing the samples property you will get a dict of: key = name of the id type, value = set of values.
        :return:
        """
        return self._group_entity_ids_by_id_type(self._samples)

    @samples.setter
    def samples(self, samples):
        self.set_sample_objects(samples)

    def get_samples_as_objects(self):
        return self._samples

    def set_sample_objects(self, samples):
        """
        Tricky this setter cause you can set the field to anything, and they the _group_entitiy_ids blah won't know
        what to do with the data if it is not what it expects.
        :param samples:
        :return:
        """
        self._samples = samples

    def get_sample_ids_by_id_type(self, id_type: str):
        return self._group_entity_ids_by_id_type(self._samples).get(id_type)


    @property
    def libraries(self):
        return self._group_entity_ids_by_id_type(self._libraries)

    @libraries.setter
    def libraries(self, libraries):
        self.set_library_objects(libraries)

    def get_libraries_as_objects(self):
        return self._libraries

    def set_library_objects(self, libraries):
        self._libraries = libraries

    def get_library_ids_by_id_type(self, id_type: str) -> List:
        return self._group_entity_ids_by_id_type(self._libraries).get(id_type)


    @property
    def studies(self):
        return self._group_entity_ids_by_id_type(self._studies)

    @studies.setter
    def studies(self, studies):
        self.set_study_objects(studies)

    def get_studies_as_objects(self):
        return self._studies

    def set_study_objects(self, studies):
        self._studies = studies

    def get_studies_as_objects(self):
        return self._studies

    def set_study_objects(self, studies):
        self._studies = studies

    def get_study_ids_by_id_type(self, id_type) -> List:
        return self._group_entity_ids_by_id_type(self._studies).get(id_type)

    def check_samples_have_all_types_of_ids(self):
        problems = []
        mandatory_ids = ['name', 'accession_number', 'internal_id']
        for sample in self._samples:
            for id in mandatory_ids:
                if not getattr(sample, id):
                    problems.append(CheckResult(check_name='Check for all sample id types',
                                                error_message='Missing sample id %s from sample: %s' % (id, sample)))
        return problems

    def check_studies_have_all_types_of_ids(self):
        problems = []
        mandatory_ids = ['name', 'accession_number', 'internal_id']
        for sample in self._samples:
            for id in mandatory_ids:
                if not getattr(sample, id):
                    problems.append(CheckResult(check_name='Check for all sample id types', severity=SEVERITY.WARNING,
                                                error_message='Missing sample id %s from sample: %s' % (id, sample)))
        return problems

    def check_metadata(self):
        problems = []
        problems.extend(self.check_samples_have_all_types_of_ids())
        problems.extend(self.check_studies_have_all_types_of_ids())
        return problems

    @staticmethod
    def from_raw_metadata(raw_metadata: SeqscapeRawMetadata):
        """
        This method creates an SeqscapeMetadata object based on a SeqqscapeRawFetchedMetadata
        :param raw_metadata:
        :return:
        """
        ss_metadata = SeqscapeMetadata()
        ss_metadata.set_sample_objects(raw_metadata.get_entities_without_duplicates_by_entity_type('sample'))
        ss_metadata.set_library_objects(raw_metadata.get_entities_without_duplicates_by_entity_type('library'))
        ss_metadata.set_study_objects(raw_metadata.get_entities_without_duplicates_by_entity_type('study'))
        return ss_metadata


    def __str__(self):
        return "SAMPLE: " + str(self._samples) + ", LIBRARIES: " + str(self._libraries) + ", STUDIES: " + str(
            self._studies)

    def __repr__(self):
        return self.__str__()