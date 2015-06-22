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

This file has been created on Jun 18, 2015.
"""

from main import error_types
import seqscape.queries as seqsc


def is_id_missing(id, id_type, entities):
    for entity in entities:
        if str(id) == str(getattr(entity, id_type)):
            return False
    return True

def is_id_duplicated(id, id_type, entities):
    found_already = False
    for entity in entities:
        if getattr(entity, id_type) == id:
            if found_already:
                return True
            else:
                found_already = True
    return False

def get_entities_by_id(id, id_type, entities):
    result = []
    for ent in  entities:
        if getattr(ent, id_type) == id:
            result.append(ent)
    return result



# def search_library_ids_in_different_tables_from_seqsc(ids_list, id_type):
#     libs = seqsc.query_all_libraries_as_batch(ids_list, id_type)
#     if not libs:
#         libs = seqsc.query_all_wells_as_batch(ids_list, id_type)
#     if not libs:
#         libs = seqsc.query_all_multiplexed_libraries_as_batch(ids_list, id_type)
#     return libs


def get_entities_from_seqscape(entity_type, ids_list, id_type):
    if entity_type == 'library':
        libs = seqsc.query_all_libraries_as_batch(ids_list, id_type)
        if not libs:
            libs = seqsc.query_all_wells_as_batch(ids_list, id_type)
        if not libs:
            libs = seqsc.query_all_multiplexed_libraries_as_batch(ids_list, id_type)
        return libs
    elif entity_type == 'sample':
        return seqsc.query_all_samples_as_batch(ids_list, id_type)
    elif entity_type == 'study':
        return seqsc.query_all_studies_as_batch(ids_list, id_type)
    raise ValueError("Entity type = " + str(entity_type) + " unknown")



def compare_entity_sets_in_seqsc(entities_dict, entity_type):

    problems = []
    seqsc_entities = {}
    # SEARCH FOR ENTITIES in SEQSCAPE BY ID_TYPE:
    for id_type, ids_list in entities_dict.items():
        entities = get_entities_from_seqscape(entity_type, ids_list, id_type)
        for id in ids_list:
            if is_id_missing(id, id_type, entities):
                problems.append(str(error_types.NotFoundInSeqscapeError(id_type, id, entity_type)))
            if is_id_duplicated(id, id_type,entities):
                duplicates = get_entities_by_id(id, id_type, entities)
                problems.append(str(error_types.TooManyEntitiesSameIdSeqscapeError(id_type, id, duplicates, entity_type)))
        seqsc_entities[id_type] = entities


    # HERE I assume I know what the id_types are (internal_id, etc..):
    id_types = seqsc_entities.keys()
    for i in xrange(1, len(id_types)-1):
        if seqsc_entities.get(id_types[i-1]) and seqsc_entities.get(id_types[i]):
            if not set(seqsc_entities.get(id_types[i-1])) == set(seqsc_entities.get(id_types[i])):
                problems.append(str(error_types.DifferentEntitiesFoundInSeqscapeQueryingByDiffIdTypesError(entity_type=entity_type,
                                                                                     id_type1=id_types[i-1],
                                                                                     id_type2=id_types[i],
                                                                                     entities_set1=seqsc_entities[id_types[i-1]],
                                                                                     entities_set2=seqsc_entities[id_types[i]])))
    return problems

#