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
#from __builtin__ import getattr

import seqscape.queries as seqsc
from main import metadata_utils
from main import error_types



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


def compare_sample_sets_in_seqsc(samples_dict):
    '''
        This function extracts a list of samples for each list of ids, and then compares the samples obtained by
        querying seqscape per id. If a list of ids is empty, it won't do anything about it. It will output an error
        only when querying by an id that doesn't exist in Seqscape.
        :param samples_dict: a dict like: {'name' : ['sang1', 'sang2'], 'accession_number' : ['EGA123', 'EGA345'], 'internal_id' : []}
        :return: a list of exceptions from error_types module

    '''
    problems = []
    seqsc_samples = {}

    # SEARCH FOR ENTITIES in SEQSCAPE BY ID_TYPE:
    for id_type, ids_list in samples_dict.items():
        samples = seqsc.query_all_samples_as_batch(ids_list, id_type)
        for id in ids_list:
            if is_id_missing(id, id_type, samples):
                problems.append(str(error_types.NotFoundInSeqscapeError(id_type, id, 'sample')))
            if is_id_duplicated(id, id_type, samples):
                duplicates = get_entities_by_id(id, id_type, samples)
                problems.append(str(error_types.TooManyEntitiesSameIdSeqscapeError(id_type, id, duplicates, 'sample')))
        seqsc_samples[id_type] = samples

    # HERE I assume I know what the id_types are (internal_id, etc..):
    if seqsc_samples.get('name') and seqsc_samples.get('internal_id'):
        if not set(seqsc_samples['name']) == set(seqsc_samples['internal_id']):
            problems.append(str(error_types.DifferentEntitiesFoundInSeqscapeQueryingByDiffIdTypesError(entity_type='sample',
                                                                                     id_type1='name',
                                                                                     id_type2='internal_id',
                                                                                     entities_set1=seqsc_samples['name'],
                                                                                     entities_set2=seqsc_samples['internal_id'])))
    if seqsc_samples.get('name') and seqsc_samples.get('accession_number'):
        if not set(seqsc_samples['name']) == set(seqsc_samples['accession_number']):
            problems.append(str(error_types.DifferentEntitiesFoundInSeqscapeQueryingByDiffIdTypesError(entity_type='sample',
                                                                                     id_type1='name',
                                                                                     id_type2='accession_number',
                                                                                     entities_set1=seqsc_samples['name'],
                                                                                     entities_set2=seqsc_samples['accession_number'])))

    return problems
