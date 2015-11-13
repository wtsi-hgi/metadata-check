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
from seqscape import queries as seqsc_q

from main.seqscape_metadata import SeqscapeRawFetchedMetadata, SeqscapeEntitiesFetchedBasedOnIds

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


class SeqscapeMetadataChecks(object):

    def _compare_entity_sets(self, entities_list: List[SeqscapeEntitiesFetchedBasedOnIds]) -> List[error_types.DiffEntitiesRetrievedFromSeqscapeByDiffIdTypesError]:
        problems = []
        for i in range(1, len(entities_list)-1):
            if not set(entities_list[i-1]) == set(entities_list[i]):
                problems.append(error_types.DiffEntitiesRetrievedFromSeqscapeByDiffIdTypesError(entity_type=entities_list[i].entity_type,
                                                                                      id_type1=entities_list[i].query_id_type,
                                                                                      id_type2=entities_list[i-1].query_id_type,
                                                                                      entities_set1=entities_list[i-1],
                                                                                      entities_set2=entities_list[i]
                                                                                    ))
        return problems

    def check_same_entity_sets_fetched_by_different_ids(self, seqscape_meta: SeqscapeRawFetchedMetadata) -> None:
        problems = []
        for entity_type, entities_fetched_list in seqscape_meta.get_all_fetched_entities():
            entity_type_pbs = self._compare_entity_sets(entities_fetched_list)
            problems.extend(entity_type_pbs)
        return problems


    def check_samples_belong_to_studies_given(self, seqscape_meta: SeqscapeRawFetchedMetadata) -> None:
        studies_by_samples = seqsc_q.query_for_studies_by_samples(seqscape_meta.samples)


    # actual_studies_from_seqsc = seqsc.query_for_studies_by_samples(sample_ids)
    # studies_by_name = [s.name for s in actual_studies_from_seqsc]
    # if study_name not in studies_by_name:
    #     return error_types.SamplesDontBelongToGivenStudy(sample_ids=sample_ids, actual_study=str(studies_by_name), desired_study=study_name)
    #



