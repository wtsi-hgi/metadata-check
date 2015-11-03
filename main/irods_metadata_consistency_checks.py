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
import metadata_utils


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

def from_seqsc_entity_list_to_list_of_ids(seqsc_entities):
    """
    This function extracts from a list of entities (where an entity is an object as defined in model classes) the lists
    of ids by type of id
    e.g.:
    input = [{ internal_id=1248309, name=APP5201377, accession_number=EGAN00001221878 }]
    output = {'internal_id' : [1248309], 'name': ['APP5201377'], 'accession_number': ['EGAN00001221878']}
    :param seqsc_entities:
    :return:
    """
    result = {'internal_id':[], 'accession_number': [], 'name': []}
    for id_type, entity_list in seqsc_entities.items():
        for entity in entity_list:
            result[id_type].append(getattr(entity, id_type))
    print "RESULTS from from_seqsc_ent: " + str(result)
    return result


def compare_entity_sets_in_seqsc(entities_dict, entity_type):
    problems = []
    seqsc_entities = {}
    # SEARCH FOR ENTITIES in SEQSCAPE BY ID_TYPE:
    for id_type, ids_list in entities_dict.items():
        if ids_list:
            entities = get_entities_from_seqscape(entity_type, ids_list, id_type)
            print "Entities as got from SS: " + str(entities)
            for id in ids_list:
                if is_id_missing(id, id_type, entities):
                    problems.append(str(error_types.NotFoundInSeqscapeError(id_type, id, entity_type)))
                if is_id_duplicated(id, id_type,entities):
                    duplicates = get_entities_by_id(id, id_type, entities)
                    problems.append(str(error_types.TooManyEntitiesSameIdSeqscapeError(id_type, id, duplicates, entity_type)))
            seqsc_entities[id_type] = entities

    # HERE I assume I know what the id_types are (internal_id, etc..):
    problems.extend(metadata_utils.GeneralUtils.check_same_entities(seqsc_entities, entity_type))
    return problems, seqsc_entities



def check_sample_is_in_desired_study(sample_ids, study_name):
    """

    :param sample_ids: a list of sample internal_id
    :param study_name: the name of the study that all the samples should be part of
    :return: Nothing if everything is ok, error_types.SampleDoesntBelongToGivenStudy if there are inconsistencies
    """
    actual_studies_from_seqsc = seqsc.query_all_studies_associated_with_samples(sample_ids)
    studies_by_name = [s.name for s in actual_studies_from_seqsc]
    if study_name not in studies_by_name:
        return error_types.SamplesDontBelongToGivenStudy(sample_ids=sample_ids, actual_study=str(studies_by_name), desired_study=study_name)


