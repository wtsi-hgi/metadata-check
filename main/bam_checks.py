"""
Created on Dec 02, 2014

Author: Irina Colgiu <ic4@sanger.ac.uk>

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
 
"""

import os
import argparse
from header_parser import bam_h_analyser as h_analyser
from identifiers import EntityIdentifier as Identif
from irods import api as irods
from irods import api_wrapper as irods_wrapper
from seqscape import queries as seqsc


def extract_fname_from_path(fpath):
    _, fname = os.path.split(fpath)
    return fname


def extract_lanelet_name(lanelet_path):
    lanelet_file = os.path.basename(lanelet_path)
    return lanelet_file


def guess_irods_path(lustre_path):
    fname = extract_fname_from_path(lustre_path)
    run_id = fname.split("_")
    irods_fpath = "/seq/" + run_id[0] + "/" + fname
    return irods_fpath


def get_header_metadata_from_irods_file(irods_path):
    full_header = h_analyser.BAMHeaderAnalyser.extract_header_from_irods_file(irods_path)
    parsed_header = h_analyser.BAMHeaderAnalyser.parse_header(full_header)
    header_metadata = h_analyser.BAMHeaderAnalyser.extract_metadata_from_header(parsed_header)
    return header_metadata.rg


def get_irods_metadata(irods_path):
    return irods.iRODSAPI.get_metadata(irods_path)


def extract_values_by_key_from_irods_metadata(avus_list, key):
    results = []
    for avu in avus_list:
        if avu.attribute == key:
            results.append(avu.value)
    return results


def get_list_of_bams_for_study(study_name):
    avus = {'study': study_name, 'type': 'bam'}
    bams = irods_wrapper.iRODSMetaQueryOperations.query_by_metadata(avus)
    filtered_bams = irods_wrapper.iRODSMetaQueryOperations.filter_out_phix_files(bams)
    return filtered_bams


def get_samples_from_seqsc(ids_list, id_type):
    return seqsc.query_all_samples_as_batch(ids_list, id_type)


def get_libraries_from_seqsc(ids_list, id_type):
    return seqsc.query_all_libraries_as_batch(ids_list, id_type)


def get_all_possible_libraries_from_seqsc(ids_list, id_type):
    libs = seqsc.query_all_libraries_as_batch(ids_list, id_type)
    if not libs:
        libs = seqsc.query_all_wells_as_batch(ids_list, id_type)
    if not libs:
        libs = seqsc.query_all_multiplexed_libraries_as_batch(ids_list, id_type)
    return libs


def get_studies_from_seqsc(ids_list, id_type):
    return seqsc.query_all_studies_as_batch(ids_list, id_type)


def get_diff_seqsc_and_irods_samples_metadata(irods_samples):
    if irods_samples['name']:
        seqsc_samples_by_name = get_samples_from_seqsc(irods_samples['name'], 'name')
        # if not seqsc_samples_by_name:
        #     return ["NO SAMPLES in SEQSCAPE by sample names from iRODS = "+str(irods_samples['name'])]
    if irods_samples['accession_number']:
        seqsc_samples_by_acc_nr = get_samples_from_seqsc(irods_samples['accession_number'], 'accession_number')
        # if not seqsc_samples_by_acc_nr:
        #     return ["NO SAMPLES in SEQSCAPE by sample accession_number from iRODS = "+str(irods_samples['accession_number'])]
    if irods_samples['internal_id']:
        seqsc_samples_by_internal_id = get_samples_from_seqsc(irods_samples['internal_id'], 'internal_id')
        # if not seqsc_samples_by_internal_id:
        #     return ["NO SAMPLES in SEQSCAPE by sample internal_id from iRODS = "+str(irods_samples['internal_id'])]

    seqsc_samples_by_acc_nr, seqsc_samples_by_name, seqsc_samples_by_internal_id = None, None, None
    seqsc_non_empty_dict = {}
    if seqsc_samples_by_acc_nr:
        seqsc_non_empty_dict['accession_number'] = seqsc_samples_by_acc_nr
    if seqsc_samples_by_name:
        seqsc_non_empty_dict['name'] = seqsc_samples_by_name
    if seqsc_samples_by_internal_id:
        seqsc_non_empty_dict['internal_id'] = seqsc_samples_by_internal_id

    differences = []
    if len(seqsc_non_empty_dict) == 3:
        if not (set(seqsc_samples_by_acc_nr) == set(seqsc_samples_by_internal_id) == set(seqsc_samples_by_name)):
            diff = "SAMPLES in iRODS =" + str(irods_samples) + " != SEQSCAPE SAMPLES SEARCHED by name:" + \
                   str(seqsc_samples_by_name) + \
                   " by accession_number:" + str(seqsc_samples_by_acc_nr) + \
                   " by internal_id: " + str(seqsc_samples_by_internal_id)
            differences.append(diff)
    elif len(seqsc_non_empty_dict) == 2:
        id_type_1, samples_by_1 = seqsc_non_empty_dict.popitem()
        id_type_2, samples_by_2 = seqsc_non_empty_dict.popitem()
        if not (set(samples_by_1) == set(samples_by_2)):
            diff = "SAMPLES in iRODS =" + str(irods_samples) + " != SEQSCAPE SAMPLES SEARCHED by "+id_type_1+": " + \
                   str(samples_by_1) + \
                   " by :" + id_type_2 + " : "+ str(samples_by_2)
            differences.append(diff)
    return differences


# TODO: I am not currently reporting when a study is not found in seqscape...
def get_diff_seqsc_and_irods_studies_metadata(irods_studies):
    # if not irods_studies['name']:
    #     return ["NO STUDY_NAMES in IRODS metadata"]
    # if not irods_studies['internal_id']:
    #     return ["NO STUDY INTERNAL_ID in IRODS metadata"]
    # if not irods_studies['accession_number']:
    #     return ["NO STUDY ACCESSION_NUMBER in IRODS metadata"]

    seqsc_studies_by_name, seqsc_studies_by_acc_nr, seqsc_studies_by_internal_id = None, None, None
    if irods_studies['name']:
        seqsc_studies_by_name = get_studies_from_seqsc(irods_studies['name'], 'name')
        # if not seqsc_studies_by_name:
            # return ["NO STUDIES in SEQSCAPE by study names from iRODS = "+str(irods_studies['name'])]
    if irods_studies['accession_number']:
        seqsc_studies_by_acc_nr = get_studies_from_seqsc(irods_studies['accession_number'], 'accession_number')
        # if not seqsc_studies_by_acc_nr:
            # return ["NO STUDIES in SEQSCAPE by study accession_number from iRODS = "+str(irods_studies['accession_number'])]
    if irods_studies['internal_id']:
        seqsc_studies_by_internal_id = get_studies_from_seqsc(irods_studies['internal_id'], 'internal_id')
        # if not seqsc_studies_by_internal_id:
            # return ["NO STUDIES in SEQSCAPE by study internal_id from iRODS = "+str(irods_studies['internal_id'])]

    seqsc_non_empty_dict = {}
    if seqsc_studies_by_acc_nr:
        seqsc_non_empty_dict['accession_number'] = seqsc_studies_by_acc_nr
    if seqsc_studies_by_name:
        seqsc_non_empty_dict['name'] = seqsc_studies_by_name
    if seqsc_studies_by_internal_id:
        seqsc_non_empty_dict['internal_id'] = seqsc_studies_by_internal_id


    differences = []
    if len(seqsc_non_empty_dict) == 3:
        if not (set(seqsc_studies_by_acc_nr) == set(seqsc_studies_by_internal_id) == set(seqsc_studies_by_name)):
            diff = "STUDY in iRODS =" + str(irods_studies) + " != SEQSCAPE STUDIES SEARCHED by name: " + \
                   str(seqsc_studies_by_name) + \
                   " != by accession_number:" + str(seqsc_studies_by_acc_nr) + \
                   " != by internal_id: " + str(seqsc_studies_by_internal_id)
            differences.append(diff)
    elif len(seqsc_non_empty_dict) == 2:
        id_type_1, studies_by_1 = seqsc_non_empty_dict.popitem()
        id_type_2, studies_by_2 = seqsc_non_empty_dict.popitem()
        if not (set(studies_by_1) == set(studies_by_2)):
            diff = "STUDIES in iRODS =" + str(irods_studies) + " != SEQSCAPE STUDIES SEARCHED by "+id_type_1+": " + \
                   str(studies_by_1) + \
                   " by :" + id_type_2 + " : "+ str(studies_by_2)
            differences.append(diff)
    return differences


def get_diff_seqsc_and_irods_libraries_metadata(irods_libraries):
    # if not irods_libraries['name']:
    #     return ["NO LIBRARY_NAMES in IRODS metadata"]
    # elif not irods_libraries['internal_id']:
    #     return ["NO LIBRARY INTERNAL_ID in IRODS metadata"]

    seqsc_libraries_by_name, seqsc_libraries_by_internal_id = None, None
    if irods_libraries['name']:
        seqsc_libraries_by_name = get_all_possible_libraries_from_seqsc(irods_libraries['name'], 'name')
    if irods_libraries['internal_id']:
        seqsc_libraries_by_internal_id = get_all_possible_libraries_from_seqsc(irods_libraries['internal_id'], 'internal_id')

    # TODO: fit this in somehow, somewhere, report it back...
    # if not seqsc_libraries_by_name:
    #     return ["NO LIBRARIES in SEQSCAPE by library names from iRODS = "+str(irods_libraries['name'])]
    # if not seqsc_libraries_by_internal_id:
    #     return ["NO LIBRARIES in SEQSCAPE by library internal_id from iRODS = "+str(irods_libraries['internal_id'])]

    differences = []
    if seqsc_libraries_by_internal_id and seqsc_libraries_by_name:
        if not (set(seqsc_libraries_by_internal_id) == set(seqsc_libraries_by_name)):
            diff = "LIBRARIES in iRODS= "+ str(irods_libraries) + " != SEQSCAPE LIBRARIES SEARCHED by name: " + \
                   str(seqsc_libraries_by_name) + \
                   " != SEQSCAPE LIBRARIES searched by internal_id: " + str(seqsc_libraries_by_internal_id)
            differences.append(diff)
    return differences


def get_diff_irods_and_header_metadata(header_dict, irods_dict):
    """
        where: (e.g.)
         irods_dict = dict('name': [sample_name], accession_number: [samples_acc_nr], internal_id: [internal_id])
         header_dict = dict('name': [sample_name], accession_number: [samples_acc_nr], internal_id: [internal_id])
    """
    differences = []
    for id_type, head_ids_list in header_dict.iteritems():
        if not irods_dict.get(id_type):
            differences.append(" HEADER " + str(id_type) + " (" + str(head_ids_list) + ") != iRODS  " + str(irods_dict))
        elif set(head_ids_list).difference(set(irods_dict[id_type])):
            differences.append(" HEADER " + str(id_type) + " (" + str(head_ids_list) + ") != iRODS  " + str(irods_dict))
    return differences


def check_sample_metadata(header_metadata, irods_metadata):
    errors = []
    irods_sample_names_list = extract_values_by_key_from_irods_metadata(irods_metadata, 'sample')
    irods_sample_acc_nr_list = extract_values_by_key_from_irods_metadata(irods_metadata, 'sample_accession_number')
    irods_sample_internal_id_list = extract_values_by_key_from_irods_metadata(irods_metadata, 'sample_id')
    irods_samples = {'name': irods_sample_names_list,
                     'accession_number': irods_sample_acc_nr_list,
                     'internal_id': irods_sample_internal_id_list
    }
    if not irods_samples['name']:
        errors.append("NO SAMPLE_NAMES in IRODS metadata")
    elif not irods_samples['internal_id']:
        errors.append("NO SAMPLE INTERNAL_ID in IRODS metadata")
    elif not irods_samples['accession_number']:
        errors.append("NO SAMPLE ACCESSION_NUMBER in IRODS metadata")


    header_samples = {'name': [], 'accession_number': [], 'internal_id': []}
    for sample in header_metadata.samples:
        id_type = Identif.guess_identifier_type(sample)
        header_samples[id_type].append(sample)

    # Compare IRODS vs. HEADER:
    irods_vs_head_diffs = get_diff_irods_and_header_metadata(header_samples, irods_samples)

    # Compare IRODS vs. SEQSCAPE:
    irods_vs_seqsc_diffs = get_diff_seqsc_and_irods_samples_metadata(irods_samples)
    return errors + irods_vs_head_diffs + irods_vs_seqsc_diffs


def check_library_metadata(header_metadata, irods_metadata):
    irods_lib_names_list = extract_values_by_key_from_irods_metadata(irods_metadata, 'library')
    irods_lib_internal_id_list = extract_values_by_key_from_irods_metadata(irods_metadata, 'library_id')
    irods_libraries = {'name': irods_lib_names_list,
                       'internal_id': irods_lib_internal_id_list}
    errors = []
    if not irods_libraries['name']:
        errors.append("NO LIBRARY_NAMES in IRODS metadata")
    elif not irods_libraries['internal_id']:
        errors.append("NO LIBRARY INTERNAL_ID in IRODS metadata")

    header_libraries = {'name': [], 'internal_id': []}

    for lib in header_metadata.libraries:
        id_type = Identif.guess_identifier_type(lib)
        header_libraries[id_type].append(lib)

    # Compare IRODS vs. HEADER:
    irods_vs_head_diffs = get_diff_irods_and_header_metadata(header_libraries, irods_libraries)

    # Compare IRODS vs. SEQSCAPE:
    irods_vs_seqsc_diffs = get_diff_seqsc_and_irods_libraries_metadata(irods_libraries)
    return irods_vs_head_diffs + irods_vs_seqsc_diffs + errors


def check_study_metadata(irods_metadata):
    irods_study_names_list = extract_values_by_key_from_irods_metadata(irods_metadata, 'study')
    irods_study_internal_id_list = extract_values_by_key_from_irods_metadata(irods_metadata, 'study_id')
    irods_study_acc_nr_list = extract_values_by_key_from_irods_metadata(irods_metadata, 'study_accession_number')
    irods_studies = {'name': irods_study_names_list,
                     'internal_id': irods_study_internal_id_list,
                     'accession_number': irods_study_acc_nr_list
    }

    errors = []
    if not irods_studies['name']:
        errors.append("NO STUDY_NAMES in IRODS metadata")
    if not irods_studies['internal_id']:
        errors.append("NO STUDY INTERNAL_ID in IRODS metadata")
    if not irods_studies['accession_number']:
        errors.append("NO STUDY ACCESSION_NUMBER in IRODS metadata")

    # Compare IRODS vs. SEQSCAPE:
    irods_vs_seqsc_diffs = get_diff_seqsc_and_irods_studies_metadata(irods_studies)
    return irods_vs_seqsc_diffs + errors


def check_md5_metadata(irods_metadata, irods_fpath):
    md5_metadata = extract_values_by_key_from_irods_metadata(irods_metadata, 'md5')
    if not md5_metadata:
        print "This file doesn't have md5 in irods metadata"
        return []


    md5_chksum = irods_wrapper.iRODSChecksumOperations.get_checksum(irods_fpath)
    if md5_chksum:
        if not md5_metadata[0] == md5_chksum.md5:
            return [
                "iRODS metadata md5 ("+ str(md5_metadata) + ") != ichksum (" + str(md5_chksum) + ") "]
    return []


def check_sample_metadata_old(header_metadata, irods_metadata):
    file_ok = True
    irods_sample_names_list = extract_values_by_key_from_irods_metadata(irods_metadata, 'sample')
    irods_sample_acc_nr_list = extract_values_by_key_from_irods_metadata(irods_metadata, 'sample_accession_number')
    irods_sample_internal_id_list = extract_values_by_key_from_irods_metadata(irods_metadata, 'sample_id')

    # Compare sample identifiers HEADER vs IRODS:
    error = False
    for sample_id in header_metadata.samples:
        id_type = Identif.guess_identifier_type(sample_id)
        if id_type == 'accession_number':
            if sample_id not in irods_sample_acc_nr_list:
                print "ERROR - this sample accession number appears in the header, but not in the metadata:" + str(
                    sample_id)
                print "Header SAMPLE accession numbers: " + str(sample_id)
                print "IRODS SAMPLE accession numbers: " + str(irods_sample_acc_nr_list)
                error = True
                file_ok = False
        elif id_type == 'name':
            if sample_id not in irods_sample_names_list:
                print "ERROR - this sample name appears in the header, but not in the irods metadata: " + str(sample_id)
                print "Header SAMPLE name: " + str(sample_id)
                print "IRODS SAMPLE names: " + str(irods_sample_names_list)
                error = True
                file_ok = False
        elif id_type == 'internal_id':
            if sample_id not in irods_sample_internal_id_list:
                print "ERROR - this sample id appears in the header, but not in the irods metadata: " + str(sample_id)
                print "Header SAMPLE internal_id: " + str(sample_id)
                print "IRODS SAMPLE internal_id: " + str(irods_sample_internal_id_list)
                error = True
                file_ok = False
        if error:
            error = False

    # Compare samples IRODS vs. SEQSCAPE:
    get_diff_seqsc_and_irods_samples_metadata()
    return file_ok


def check_library_metadata_old(header_metadata, irods_metadata):
    irods_lib_names_list = extract_values_by_key_from_irods_metadata(irods_metadata, 'library')
    irods_lib_ids_list = extract_values_by_key_from_irods_metadata(irods_metadata, 'library_id')

    header_lib_identifiers_tuples = [(Identif.guess_identifier_type(lib), lib) for lib in header_metadata.libraries]

    print "IRODS LIBRARY names: " + str(irods_lib_names_list)
    print "IRODS LIBRARY ids: " + str(irods_lib_ids_list)
    print "HEADER LIBRARIES: " + str(header_lib_identifiers_tuples)

    error = False
    for lib_identif in header_lib_identifiers_tuples:
        if lib_identif not in irods_lib_ids_list and lib_identif not in irods_lib_names_list:
            print "ERROR Library in the header, but not in the iRODS metadata: " + str(lib_identif)
            print "IRODS libraries name: " + str(irods_lib_names_list)
            print "IRODS library ids: " + str(irods_lib_ids_list)
            error = True
        if error:
            error = False
        else:
            print "File OK"


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


def check_run_id(irods_metadata, irods_fpath):
    """
    This test assumes that all the files in iRODS have exactly 1 run (=LANELETS)
    """
    irods_run_ids = extract_values_by_key_from_irods_metadata(irods_metadata, 'id_run')
    path_run_id = get_run_from_irods_path(irods_fpath)
    if len(irods_run_ids) > 1:
        return ["ERROR: > 1 runs for this file."]
    elif len(irods_run_ids) < 1:
        return ["ERROR: MISSING run_id from iRODS metadata"]
    else:
        irods_run_id = irods_run_ids[0]
    if not irods_run_id == path_run_id:
        return ["The run id in the iRODS file path is not the same as the run id in the iRODS metadata: " + \
                str(irods_run_id) + " vs. " + str(path_run_id)]
    return []


def check_lane_metadata(irods_metadata, irods_fpath):
    lane_id = get_lane_from_irods_path(irods_fpath)
    irods_lane_ids = extract_values_by_key_from_irods_metadata(irods_metadata, 'lane')
    if len(irods_lane_ids) > 1:
        return [" > 1 LANE in iRODS metadata"]
    elif len(irods_lane_ids) < 1:
        return ["NO LANE in iRODS metadata"]
    else:
        irods_lane_id = irods_lane_ids[0]
    if not irods_lane_id == lane_id:
        return ["iRODS fpath lane_id != lane_id in iRODS metadata: " +
                str(irods_lane_id) + " vs. " + str(lane_id)]
    return []


def extract_lanelet_name_from_irods_fpath(irods_fpath):
    fname = os.path.basename(irods_fpath)
    if fname.find("_") == -1:
        return ''
    if fname.find(".bam") != -1:
        return fname.split(".bam")[0]
    return ''


def check_lanelet_name(irods_fpath, header_lanelets):
    if len(header_lanelets) != 1:
        return [" > 1 lanelets in the header."]
    irods_lanelet_name = extract_lanelet_name_from_irods_fpath(irods_fpath)
    if irods_lanelet_name != header_lanelets[0]:
        return ["HEADER LANELET = "+str(header_lanelets[0]) + " different from FILE NAME = "+str(irods_lanelet_name)]
    return []


def extract_reference_name_from_path(ref_path):
    #print "REF PATH: "+str(ref_path)
    ref_file_name = os.path.basename(ref_path)
    if ref_file_name.find(".fa") != -1:
        ref_name = ref_file_name.split(".fa")[0]
        return ref_name
    return ''


def check_reference(irods_metadata, desired_ref):
    ref_paths = extract_values_by_key_from_irods_metadata(irods_metadata, 'reference')
    if len(ref_paths) > 1:
        return [" > 1 REFERENCE ATTRIBUTE in iRODS metadata"]
    elif len(ref_paths) < 1:
        return ["NO REFERENCE ATTRIBUTE in iRODS metadata"]
    else:
        ref_path = ref_paths[0]
    ref_name = extract_reference_name_from_path(ref_path)
    if ref_name != desired_ref:
        return ["WANTED REFERENCE =: " + str(desired_ref)+ " different from ACTUAL REFERENCE = " + str(ref_name)]
    return []


def test_file_metadata(irods_fpath, desired_ref=None):
    header_metadata = get_header_metadata_from_irods_file(irods_fpath)
    irods_metadata = get_irods_metadata(irods_fpath)

    diffs = []
    sample_issues = check_sample_metadata(header_metadata, irods_metadata)
    diffs.extend(sample_issues)

    library_issues = check_library_metadata(header_metadata, irods_metadata)
    diffs.extend(library_issues)

    study_issues = check_study_metadata(irods_metadata)
    diffs.extend(study_issues)

    # study_internal_id = extract_values_by_key_from_irods_metadata(irods_metadata, 'study_id')
    # study_acc_nr = extract_values_by_key_from_irods_metadata(irods_metadata, 'study_accession_number')
    #
    # library_name = extract_values_by_key_from_irods_metadata(irods_metadata, 'library')
    # library_internal_id = extract_values_by_key_from_irods_metadata(irods_metadata, 'library_id')

    # run_id = extract_values_by_key_from_irods_metadata(irods_metadata, 'id_run')
    # lane_id = extract_values_by_key_from_irods_metadata(irods_metadata, 'lane')
    # tag_id = extract_values_by_key_from_irods_metadata(irods_metadata, 'tag_index')

    # md5 = extract_values_by_key_from_irods_metadata(irods_metadata, 'md5')
    checksum_issues = check_md5_metadata(irods_metadata, irods_fpath)
    diffs.extend(checksum_issues)

    run_id_issues = check_run_id(irods_metadata, irods_fpath)
    diffs.extend(run_id_issues)

    lane_metadata_issues = check_lane_metadata(irods_metadata, irods_fpath)
    diffs.extend(lane_metadata_issues)

    lane_name_issues = check_lanelet_name(irods_fpath, header_metadata.lanelets)
    diffs.extend(lane_name_issues)

    if desired_ref:
        ref_issues = check_reference(irods_metadata, desired_ref)
        diffs.extend(ref_issues)

    if diffs:
        print "FILE: "+str(irods_fpath) + " has issues with:"
        if sample_issues:
            print "SAMPLES: "+str(sample_issues)
        if library_issues:
            print "LIBRARIES: "+str(library_issues)
        if study_issues:
            print "STUDIES: "+ str(study_issues)
        if checksum_issues:
            print "CHECKSUM: "+str(checksum_issues)
        if run_id_issues:
            print "RUN IDS: "+str(run_id_issues)
        if lane_name_issues:
            print "LANE METADATA: "+str(lane_metadata_issues)
        if lane_name_issues:
            print "LANE NAME: "+str(lane_name_issues)
        if desired_ref and ref_issues:
            print "REFERENCE: "+str(ref_issues)

    
    #print "FILE: " + str(irods_fpath) + " ERRORS: " + str(diffs)
    # reference_file = extract_values_by_key_from_irods_metadata(irods_metadata, 'reference')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--study', required=False, help='Study name')
    parser.add_argument('--path_irods', required=False, help='Path in iRODS to a BAM')

    args = parser.parse_args()
    if not args.study and not args.path_irods:
        print "No study provided, no BAM path given => NOTHING TO DO! EXITTING"
        exit(0)
    return args


# CHECK LANELETS:

def main():
    args = parse_args()
    if args.path_irods:
        fpaths_irods = [args.path_irods]
    elif args.study:
        fpaths_irods = get_list_of_bams_for_study(args.study)
        print "FPATHS for this study: " + str(fpaths_irods)
    else:
        print "No arguments provided! Exitting"
        return
    for fpath in fpaths_irods:
        test_file_metadata(fpath)


if __name__ == '__main__':
    main()





