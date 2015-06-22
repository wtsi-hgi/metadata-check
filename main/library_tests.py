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

This file has been created on Feb 10, 2015.
"""

import seqscape.queries as seqsc
from main import metadata_utils, error_types


# def get_libraries_from_seqsc(ids_list, id_type):
#     return seqsc.query_all_libraries_as_batch(ids_list, id_type)

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


def search_library_ids_in_different_tables_from_seqsc(ids_list, id_type):
    libs = seqsc.query_all_libraries_as_batch(ids_list, id_type)
    if not libs:
        libs = seqsc.query_all_wells_as_batch(ids_list, id_type)
    if not libs:
        libs = seqsc.query_all_multiplexed_libraries_as_batch(ids_list, id_type)
    return libs


def compare_library_sets_in_seqsc(libraries_dict):

    problems = []
    seqsc_samples = {}
    # SEARCH FOR ENTITIES in SEQSCAPE BY ID_TYPE:
    for id_type, ids_list in libraries_dict.items():
        libraries = search_library_ids_in_different_tables_from_seqsc(ids_list, id_type)
        for id in ids_list:
            if is_id_missing(id, id_type, libraries):
                problems.append(str(error_types.NotFoundInSeqscapeError(id_type, id, 'library')))
            if is_id_duplicated(id, id_type, libraries):
                duplicates = get_entities_by_id(id, id_type, libraries)
                problems.append(str(error_types.TooManyEntitiesSameIdSeqscapeError(id_type, id, duplicates, 'library')))
        seqsc_samples[id_type] = libraries


    # HERE I assume I know what the id_types are (internal_id, etc..):
    id_types = seqsc_samples.keys()
    for i in xrange(1, len(id_types)-1):
        if seqsc_samples.get(id_types[i-1]) and seqsc_samples.get(id_types[i]):
            if not set(seqsc_samples.get(id_types[i-1])) == set(seqsc_samples.get(id_types[i])):
                problems.append(str(error_types.DifferentEntitiesFoundInSeqscapeQueryingByDiffIdTypesError(entity_type='library',
                                                                                     id_type1=id_types[i-1],
                                                                                     id_type2=id_types[i],
                                                                                     entities_set1=seqsc_samples[id_types[i-1]],
                                                                                     entities_set2=seqsc_samples[id_types[i]])))
    return problems

#
#
# def compare_library_sets_obtained_by_seqscape_ids_lookup(irods_libraries):
#     """
#         This function checks consistencies across different types of ids against Seqscape
#     """
#     differences = []
#     seqsc_libraries_by_name, seqsc_libraries_by_internal_id = None, None
#     if irods_libraries.get('name'):
#         seqsc_libraries_by_name = search_library_ids_in_different_tables_from_seqsc(irods_libraries['name'], 'name')
#         if not seqsc_libraries_by_name:
#             differences.append("NO LIBRARIES in SEQSCAPE by library names from iRODS = " + str(irods_libraries['name']))
#     if irods_libraries.get('internal_id'):
#         seqsc_libraries_by_internal_id = search_library_ids_in_different_tables_from_seqsc(irods_libraries['internal_id'],
#                                                                                'internal_id')
#         if not seqsc_libraries_by_internal_id:
#             differences.append(
#                 "NO LIBRARIES in SEQSCAPE by library internal_id from iRODS = " + str(irods_libraries['internal_id']))
#
#     if seqsc_libraries_by_internal_id and seqsc_libraries_by_name:
#         if not (set(seqsc_libraries_by_internal_id) == set(seqsc_libraries_by_name)):
#             diff = "LIBRARIES in iRODS= " + str(irods_libraries) + " != LIBRARIES IN SEQSCAPE SEARCHED by name: " + \
#                    str(seqsc_libraries_by_name) + \
#                    " != LIBRARIES IN SEQSCAPE searched by internal_id: " + str(seqsc_libraries_by_internal_id)
#             differences.append(diff)
#     return differences
#
