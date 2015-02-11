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

from irods import api as irods_api
from irods import icommands_wrapper
from header_parser import bam_h_analyser as header_analyser
import os
from identifiers import EntityIdentifier as Identif



def check_all_identifiers_in_metadata(metadata, name=True, internal_id=True, accession_number=True):
    error_report = []
    if name and not metadata.get('name'):
        error_report.append("NO names in IRODS metadata")
    if internal_id and not metadata.get('internal_id'):
        error_report.append("NO  internal_ids in IRODS metadata")
    if accession_number and not metadata.get('accession_number'):
        error_report.append("NO accession numbers in IRODS metadata")
    return error_report


def get_diff_irods_and_header_metadata(header_dict, irods_dict):
    """
        where: (e.g.)
         irods_dict = dict('name': [sample_name], accession_number: [samples_acc_nr], internal_id: [internal_id])
         header_dict = dict('name': [sample_name], accession_number: [samples_acc_nr], internal_id: [internal_id])
    """
    differences = []
    for id_type, head_ids_list in header_dict.iteritems():
        if irods_dict.get(id_type) and header_dict.get(id_type):
            if set(head_ids_list).difference(set(irods_dict[id_type])):
                differences.append(
                    " HEADER " + str(id_type) + " (" + str(head_ids_list) + ") != iRODS  " + str(irods_dict))
    return differences


def _get_file_header_metadata(path, location):
    if location == 'irods':
        full_header = header_analyser.BAMHeaderAnalyser.extract_header_from_irods_file(path)
    elif location == 'lustre':
        full_header = header_analyser.BAMHeaderAnalyser.extract_header_from_file(path)
    else:
        raise ValueError("This function accepts as file location only irods or lustre.")
    parsed_header = header_analyser.BAMHeaderAnalyser.parse_header(full_header)
    header_metadata = header_analyser.BAMHeaderAnalyser.extract_metadata_from_header(parsed_header)
    return header_metadata.rg


def get_header_metadata_from_irods_file(irods_path):
    return _get_file_header_metadata(irods_path, 'irods')


def get_header_metadata_from_lustre_file(lustre_path):
    return _get_file_header_metadata(lustre_path, 'lustre')


def retrieve_list_of_bams_by_study_from_irods(study_name):
    avus = {'study': study_name, 'type': 'bam'}
    bams = icommands_wrapper.iRODSMetaQueryOperations.query_by_metadata(avus)
    filtered_bams = icommands_wrapper.iRODSMetaQueryOperations.filter_out_phix_files(bams)
    return filtered_bams



def extract_fname_from_path(fpath):
    _, fname = os.path.split(fpath)
    return fname


def extract_lanelet_name(lanelet_path):
    lanelet_file = os.path.basename(lanelet_path)
    return lanelet_file


# TODO: test - what if the lanelet is a whole lane (x10 data)? TO add unittest for this!
def guess_seq_irods_path_from_lustre_path(lustre_path):
    """
        Applies only for the data delivered by NPG.

    """
    fname = extract_fname_from_path(lustre_path)
    run_id = fname.split("_")
    irods_fpath = "/seq/" + run_id[0] + "/" + fname
    return irods_fpath


def retrieve_irods_metadata(irods_path):
    return irods_api.iRODSAPI.retrieve_metadata_for_file(irods_path)


def extract_values_for_key_from_irods_metadata(avus_list, key):
    results = []
    for avu in avus_list:
        if avu.attribute == key:
            results.append(avu.value)
    return results


def sort_entities_by_guessing_id_type(ids_list):
    """
        This function takes a list of ids, which it doesn't know what type they are,
        guesses the id type and then returns a dict containing 3 lists - one for each type of id
        (internal_id, accession_number, name).
        Parameters
        ----------
            ids_list : list - containing together all sorts of ids that identify entities.
        Returns
        -------
            sorted_ids : dict - {'name': list, 'accession_number': list, 'internal_id': list}
    """
    sorted_ids = {'name': [], 'accession_number': [], 'internal_id': []}
    for entity_id in ids_list:
        id_type = Identif.guess_identifier_type(entity_id)
        sorted_ids[id_type].append(entity_id)
    return sorted_ids


def get_run_from_irods_path(irods_fpath):
    tokens = irods_fpath.split("/")
    if len(tokens) >= 2 and tokens[1] == 'seq':
        return tokens[-2]
    return ''


def get_lane_from_irods_path(irods_fpath):
    fname = os.path.basename(irods_fpath)
    if fname.find("_") != -1:
        lane_id = ''
        lane_token = fname.split("_")[1]
        if lane_token.find("#") != -1:
            lane_id = lane_token.split("#")[0]
        elif lane_token.find(".bam") != -1:
            lane_id = lane_token.split(".bam")[0]
        return lane_id
    return ''


def extract_reference_name_from_path(ref_path):
    ref_file_name = os.path.basename(ref_path)
    if ref_file_name.find(".fa") != -1:
        ref_name = ref_file_name.split(".fa")[0]
        return ref_name
    return ''


def extract_lanelet_name_from_irods_fpath(irods_fpath):
    fname = os.path.basename(irods_fpath)
    if fname.find("_") == -1:
        return ''
    if fname.find(".bam") != -1:
        return fname.split(".bam")[0]
    return ''


def extract_samples_from_irods_metadata(irods_metadata):
    irods_sample_names_list = extract_values_for_key_from_irods_metadata(irods_metadata, 'sample')
    irods_sample_acc_nr_list = extract_values_for_key_from_irods_metadata(irods_metadata, 'sample_accession_number')
    irods_sample_internal_id_list = extract_values_for_key_from_irods_metadata(irods_metadata, 'sample_id')
    irods_samples = {'name': irods_sample_names_list,
                     'accession_number': irods_sample_acc_nr_list,
                     'internal_id': irods_sample_internal_id_list
    }
    return irods_samples


def extract_studies_from_irods_metadata(irods_metadata):
    irods_study_names_list = extract_values_for_key_from_irods_metadata(irods_metadata, 'study')
    irods_study_internal_id_list = extract_values_for_key_from_irods_metadata(irods_metadata, 'study_id')
    irods_study_acc_nr_list = extract_values_for_key_from_irods_metadata(irods_metadata, 'study_accession_number')
    irods_studies = {'name': irods_study_names_list,
                     'internal_id': irods_study_internal_id_list,
                     'accession_number': irods_study_acc_nr_list
    }
    return irods_studies


def extract_libraries_from_irods_metadata(irods_metadata):
    irods_lib_internal_id_list = extract_values_for_key_from_irods_metadata(irods_metadata, 'library_id')
    if not irods_lib_internal_id_list:
        irods_lib_names_list = extract_values_for_key_from_irods_metadata(irods_metadata, 'library')
        irods_libraries = {'name': irods_lib_names_list}
    else:
        irods_libraries = {'internal_id': irods_lib_internal_id_list}
    return irods_libraries
