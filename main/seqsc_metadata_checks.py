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

This file has been created on Nov 10, 2015.
"""

from typing import List
import collections
from main import error_types

from main.seqscape_metadata import SeqscapeMetadata, SeqscapeEntitiesFetchedByIdType

class SeqscapeFetchedEntitiesChecks(object):

    def _find_missing_ids(self, ids_found, ids_given):
        return set(ids_given).difference(set(ids_found))

    def _find_duplicated_ids(self, ids_found):
        return [item for item, count in collections.Counter(ids_found).items() if count > 1]


    def check_all_ids_were_found(self, entities_fetched_obj):
        ids_found = [getattr(ent, entities_fetched_obj.query_id_type) for ent in entities_fetched_obj.entities_fetched]
        ids_missing = self._find_missing_ids(ids_found, entities_fetched_obj.query_ids)
        if ids_missing:
            raise error_types.NotFoundInSeqscapeError(entities_fetched_obj.query_id_type, ids_missing, entities_fetched_obj.entity_type)

    def check_no_duplicates_found(self, entities_fetched_obj):
        ids_found = [getattr(ent, entities_fetched_obj.query_id_type) for ent in entities_fetched_obj.entities_fetched]
        ids_duplicated = self._find_duplicated_ids(ids_found)
        entities_dupl_ids = [ent for ent in entities_fetched_obj.entities_fetched
                                  if getattr(ent, entities_fetched_obj.query_id_type) in ids_duplicated]
        if ids_duplicated:
            raise error_types.TooManyEntitiesSameIdSeqscapeError(entities_fetched_obj.query_id_type, ids_duplicated, entities_dupl_ids)



    # @classmethod
    # def check_same_entities(cls, seqsc_entities, entity_type):
    #     problems = []
    #     id_types = seqsc_entities.keys()
    #     for i in xrange(1, len(id_types)-1):
    #         if seqsc_entities.get(id_types[i-1]) and seqsc_entities.get(id_types[i]):
    #             if not set(seqsc_entities.get(id_types[i-1])) == set(seqsc_entities.get(id_types[i])):
    #                 problems.append(str(error_types.DifferentEntitiesFoundInSeqscapeQueryingByDiffIdTypesError(entity_type=entity_type,
    #                                                                                      id_type1=id_types[i-1],
    #                                                                                      id_type2=id_types[i],
    #                                                                                      entities_set1=seqsc_entities[id_types[i-1]],
    #                                                                                      entities_set2=seqsc_entities[id_types[i]])))
    #     return problems


class SeqscapeMetadataChecks(object):

    def _compare_entity_sets(self, entities_list: List[SeqscapeEntitiesFetchedByIdType]):
        problems = []
        for i in xrange(1, len(entities_list)-1):
            if not set(entities_list[i-1]) == set(entities_list[i]):
                problems.append(error_types.DiffEntitiesRetrievedFromSeqscapeByDiffIdTypesError(entity_type=entities_list[i].entity_type,
                                                                                      id_type1=entities_list[i].query_id_type,
                                                                                      id_type2=entities_list[i-1].query_id_type,
                                                                                      entities_set1=entities_list[i-1],
                                                                                      entities_set2=entities_list[i]
                                                                                    ))
        return problems

    def check_same_entity_sets_fetched_by_different_ids(self, seqscape_meta: SeqscapeMetadata) -> None:
        problems = []
        for entity_type, entities_fetched_list in seqscape_meta.get_all_fetched_entities():
            entity_type_pbs = self._compare_entity_sets(entities_fetched_list)
            problems.extend(entity_type_pbs)
        return problems


        # prototype_entity_set = None
        # #for entity_type in seqscape_meta.get_all_fetched_entities():   # _entities_dict_by_type = { 'sample' : [SeqscapeEntitiesFetchedByIdType(), SeqscapeEntitiesFetchedByIdType(),..]}
        # all_fetched_entities = seqscape_meta.get_all_fetched_entities().items()
        # for i in xrange(1, len(all_fetched_entities)-1):
        #     entity_sets = all_fetched_entities[i]
        #     if not prototype_entity_set:
        #         prototype_entity_set = set(seqscape_meta.get_fetched_entities_by_type(entity_type))
        #     else:
        #         if not prototype_entity_set == set(seqscape_meta.get_fetched_entities_by_type(entity_type)):
        #             #raise error_types.DifferentEntitiesFoundInSeqscapeQueryingByDiffIdTypesError(entity_type=entity_type, id_type1=)
        #             pass



# class SeqscapeEntitiesFetchedByIdType(object):
#
#     def __init__(self, entities_fetched, query_ids, query_id_type, entity_type):
#         """
#         This is a class used to store data retrieved from Sequencescape DB.
#         It holds entities are fetched from Seqscape when querying by a list of ids of type query_id_type.
#         :param entities_fetched: entities fetched from Seqscape
#         :param query_id_type: a type of id - e.g. "accession_number", "internal_id", "name"
#         :param query_ids: a list of strings = the list of ids that Seqscape was queried by,
#         :return:
#         """
#         self.entities_fetched = entities_fetched
#         self.query_ids = query_ids
#         self.query_id_type = query_id_type
#         self.entity_type = entity_type


# class SeqscapeMetadata(object):
#
#     def __init__(self):
#         self._entities_dict_by_type = defaultdict(list)
#
#     def add_fetched_entities_by_type(self, entities_fetched, entity_type):
#         self._entities_dict_by_type[entity_type].append(entities_fetched)
#
#     def get_fetched_entities_by_type(self, entity_type):
#         return self._entities_dict_by_type[entity_type]