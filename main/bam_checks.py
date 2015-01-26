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
from collections import namedtuple
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
    differences = []
    seqsc_samples_by_acc_nr, seqsc_samples_by_name, seqsc_samples_by_internal_id = None, None, None
    if irods_samples['name']:
        seqsc_samples_by_name = get_samples_from_seqsc(irods_samples['name'], 'name')
        if not seqsc_samples_by_name:
            differences.append("NO SAMPLES found in SEQSCAPE by sample names taken from iRODS metadata = " +
                               str(irods_samples['name']))
    if irods_samples['accession_number']:
        seqsc_samples_by_acc_nr = get_samples_from_seqsc(irods_samples['accession_number'], 'accession_number')
        if not seqsc_samples_by_acc_nr:
            differences.append("NO SAMPLES found in SEQSCAPE by sample accession_number from iRODS metadata = " +
                               str(irods_samples['accession_number']))
    if irods_samples['internal_id']:
        seqsc_samples_by_internal_id = get_samples_from_seqsc(irods_samples['internal_id'], 'internal_id')
        if not seqsc_samples_by_internal_id:
            differences.append("NO SAMPLES found in SEQSCAPE by sample internal_id from iRODS metadata = " +
                               str(irods_samples['internal_id']))

    # Compare samples found in Seqscape by different identifiers:
    if seqsc_samples_by_acc_nr and seqsc_samples_by_name:
        if not set(seqsc_samples_by_acc_nr) == set(seqsc_samples_by_name):
            diff = "The samples found in Seqscape when querying it by sample names from iRODS metadata: " + \
                   str(seqsc_samples_by_name) + " != as when querying by accession number from iRODS metadata: " + \
                   str(seqsc_samples_by_acc_nr)
            differences.append(diff)

    if seqsc_samples_by_internal_id and seqsc_samples_by_name:
        if not set(seqsc_samples_by_internal_id) == set(seqsc_samples_by_internal_id):
            diff = "The samples found in Seqscape when querying it by sample names from iRODS metadata: " + \
                   str(seqsc_samples_by_name) + " != as when querying by internal_ids from iRODS metadata: " + \
                   str(seqsc_samples_by_internal_id)
            differences.append(diff)
    return differences


def get_diff_seqsc_and_irods_studies_metadata(irods_studies):
    differences = []
    seqsc_studies_by_name, seqsc_studies_by_acc_nr, seqsc_studies_by_internal_id = None, None, None
    if irods_studies['name']:
        seqsc_studies_by_name = get_studies_from_seqsc(irods_studies['name'], 'name')
        if not seqsc_studies_by_name:
            differences.append("NO STUDIES in SEQSCAPE by study names from iRODS = " + str(irods_studies['name']))
    if irods_studies['accession_number']:
        seqsc_studies_by_acc_nr = get_studies_from_seqsc(irods_studies['accession_number'], 'accession_number')
        if not seqsc_studies_by_acc_nr:
            differences.append("NO STUDIES in SEQSCAPE by study accession_number from iRODS = " + str(
                irods_studies['accession_number']))
    if irods_studies['internal_id']:
        seqsc_studies_by_internal_id = get_studies_from_seqsc(irods_studies['internal_id'], 'internal_id')
        if not seqsc_studies_by_internal_id:
            differences.append(
                "NO STUDIES in SEQSCAPE by study internal_id from iRODS = " + str(irods_studies['internal_id']))

    # Compare studies found in Seqscape by different identifiers:
    if seqsc_studies_by_acc_nr and seqsc_studies_by_name:
        if not set(seqsc_studies_by_acc_nr) == set(seqsc_studies_by_name):
            diff = "The studies found in Seqscape when querying it by name from iRODS metadata: " + \
                   str(seqsc_studies_by_name) + " != as when querying by accession number from iRODS metadata: " + \
                   str(seqsc_studies_by_acc_nr)
            differences.append(diff)

    if seqsc_studies_by_internal_id and seqsc_studies_by_name:
        if not set(seqsc_studies_by_internal_id) == set(seqsc_studies_by_internal_id):
            diff = "The studies found in Seqscape when querying it by name from iRODS metadata: " + \
                   str(seqsc_studies_by_name) + " != as when querying by internal_ids from iRODS metadata: " + \
                   str(seqsc_studies_by_internal_id)
            differences.append(diff)
    return differences


def get_diff_seqsc_and_irods_libraries_metadata(irods_libraries):
    differences = []
    seqsc_libraries_by_name, seqsc_libraries_by_internal_id = None, None
    if irods_libraries['name']:
        seqsc_libraries_by_name = get_all_possible_libraries_from_seqsc(irods_libraries['name'], 'name')
        if not seqsc_libraries_by_name:
            differences.append("NO LIBRARIES in SEQSCAPE by library names from iRODS = " + str(irods_libraries['name']))
    if irods_libraries['internal_id']:
        seqsc_libraries_by_internal_id = get_all_possible_libraries_from_seqsc(irods_libraries['internal_id'],
                                                                               'internal_id')
        if not seqsc_libraries_by_internal_id:
            differences.append(
                "NO LIBRARIES in SEQSCAPE by library internal_id from iRODS = " + str(irods_libraries['internal_id']))

    if seqsc_libraries_by_internal_id and seqsc_libraries_by_name:
        if not (set(seqsc_libraries_by_internal_id) == set(seqsc_libraries_by_name)):
            diff = "LIBRARIES in iRODS= " + str(irods_libraries) + " != LIBRARIES IN SEQSCAPE SEARCHED by name: " + \
                   str(seqsc_libraries_by_name) + \
                   " != LIBRARIES IN SEQSCAPE searched by internal_id: " + str(seqsc_libraries_by_internal_id)
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
        # if not irods_dict.get(id_type):
        # differences.append(" HEADER " + str(id_type) + " (" + str(head_ids_list) + ") != iRODS  " + str(irods_dict))
        if irods_dict.get(id_type) and header_dict.get(id_type):
            if set(head_ids_list).difference(set(irods_dict[id_type])):
                differences.append(
                    " HEADER " + str(id_type) + " (" + str(head_ids_list) + ") != iRODS  " + str(irods_dict))
    return differences


def get_samples_from_irods_metadata(irods_metadata):
    irods_sample_names_list = extract_values_by_key_from_irods_metadata(irods_metadata, 'sample')
    irods_sample_acc_nr_list = extract_values_by_key_from_irods_metadata(irods_metadata, 'sample_accession_number')
    irods_sample_internal_id_list = extract_values_by_key_from_irods_metadata(irods_metadata, 'sample_id')
    irods_samples = {'name': irods_sample_names_list,
                     'accession_number': irods_sample_acc_nr_list,
                     'internal_id': irods_sample_internal_id_list
    }
    return irods_samples


def get_library_from_irods_metadata(irods_metadata):
    irods_lib_names_list = extract_values_by_key_from_irods_metadata(irods_metadata, 'library')
    irods_lib_internal_id_list = extract_values_by_key_from_irods_metadata(irods_metadata, 'library_id')
    irods_libraries = {'name': irods_lib_names_list,
                       'internal_id': irods_lib_internal_id_list}
    return irods_libraries


def get_studies_from_irods_metadata(irods_metadata):
    irods_study_names_list = extract_values_by_key_from_irods_metadata(irods_metadata, 'study')
    irods_study_internal_id_list = extract_values_by_key_from_irods_metadata(irods_metadata, 'study_id')
    irods_study_acc_nr_list = extract_values_by_key_from_irods_metadata(irods_metadata, 'study_accession_number')
    irods_studies = {'name': irods_study_names_list,
                     'internal_id': irods_study_internal_id_list,
                     'accession_number': irods_study_acc_nr_list
    }
    return irods_studies


def get_entities_from_header_metadata(header_entities):
    grouped_entities = {'name': [], 'accession_number': [], 'internal_id': []}
    for sample_id in header_entities:
        id_type = Identif.guess_identifier_type(sample_id)
        grouped_entities[id_type].append(sample_id)
    return grouped_entities


def report_missing_identifiers(metadata):
    error_report = []
    if not 'name' in metadata or not metadata['name']:
        error_report.append("NO names in IRODS metadata")
    if not 'internal_id' in metadata or not metadata['internal_id']:
        error_report.append("NO  internal_ids in IRODS metadata")
    if not 'accession_number' in metadata or not metadata['accession_number']:
        error_report.append("NO accession numbers in IRODS metadata")
    return error_report


def check_sample_metadata(header_metadata, irods_metadata):
    errors = []

    header_samples = get_entities_from_header_metadata(header_metadata.samples)
    irods_samples = get_samples_from_irods_metadata(irods_metadata)

    missing_ids = report_missing_identifiers(irods_samples)
    errors.extend(missing_ids)

    # Compare IRODS vs. HEADER:
    irods_vs_head_diffs = get_diff_irods_and_header_metadata(header_samples, irods_samples)

    # Compare IRODS vs. SEQSCAPE:
    irods_vs_seqsc_diffs = get_diff_seqsc_and_irods_samples_metadata(irods_samples)
    return errors + irods_vs_head_diffs + irods_vs_seqsc_diffs


def check_library_metadata(header_metadata, irods_metadata):
    errors = []

    header_libraries = get_entities_from_header_metadata(header_metadata.libraries)
    irods_libraries = get_library_from_irods_metadata(irods_metadata)

    missing_ids = report_missing_identifiers(irods_libraries)
    errors.extend(missing_ids)

    # Compare IRODS vs. HEADER:
    irods_vs_head_diffs = get_diff_irods_and_header_metadata(header_libraries, irods_libraries)

    # Compare IRODS vs. SEQSCAPE:
    irods_vs_seqsc_diffs = get_diff_seqsc_and_irods_libraries_metadata(irods_libraries)
    return irods_vs_head_diffs + irods_vs_seqsc_diffs + errors


def check_study_metadata(irods_metadata):
    errors = []

    irods_studies = get_studies_from_irods_metadata(irods_metadata)

    missing_ids = report_missing_identifiers(irods_studies)
    errors.extend(missing_ids)

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
                "iRODS metadata md5 (" + str(md5_metadata) + ") != ichksum (" + str(md5_chksum) + ") "]
    return []


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
        return [
            "HEADER LANELET = " + str(header_lanelets[0]) + " different from FILE NAME = " + str(irods_lanelet_name)]
    return []


def extract_reference_name_from_path(ref_path):
    # print "REF PATH: "+str(ref_path)
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
        return ["WANTED REFERENCE =: " + str(desired_ref) + " different from ACTUAL REFERENCE = " + str(ref_name)]
    return []


def run_tests_on_samples(irods_metadata, header_metadata=None,
                         irods_vs_header=True, irods_vs_seqscape=True):
    if not irods_vs_header and not irods_vs_seqscape:
        print "Called tests_on_samples, but nothing to be done because both " \
              "irods_vs_header and irods_vs_seqscape parameters are False."
        return
    if header_metadata and not irods_vs_header:
        print "ERROR - called tests_on_samples, but irods_vs_header parameter is false."
        return
    if not header_metadata and irods_vs_header:
        print "ERROR - called tests_on_samples, but header_metadata is None."
        return

    diffs = []
    if irods_vs_header or irods_vs_seqscape:
        irods_samples = get_samples_from_irods_metadata(irods_metadata)
        missing_ids = report_missing_identifiers(irods_samples)
        diffs.extend(missing_ids)

    # Compare IRODS vs. HEADER:
    if irods_vs_header:
        header_samples = get_entities_from_header_metadata(header_metadata.samples)
        irods_vs_head_diffs = get_diff_irods_and_header_metadata(header_samples, irods_samples)
        diffs.extend(irods_vs_head_diffs)

    # Compare IRODS vs. SEQSCAPE:
    if irods_vs_seqscape:
        irods_vs_seqsc_diffs = get_diff_seqsc_and_irods_samples_metadata(irods_samples)
        diffs.extend(irods_vs_seqsc_diffs)
    return diffs


def run_tests_on_libraries(irods_metadata, header_metadata=None,
                           irods_vs_header=True, irods_vs_seqscape=True):
    if not irods_vs_header and not irods_vs_seqscape:
        print "Called tests_on_libraries, but nothing to be done because both " \
              "irods_vs_header and irods_vs_seqscape parameters are False."
        return
    if header_metadata and not irods_vs_header:
        print "ERROR - called tests_on_libraries, but irods_vs_header parameter is false."
        return
    if not header_metadata and irods_vs_header:
        print "ERROR - called tests_on_libraries, but header_metadata is None."
        return

    diffs = []
    if irods_vs_header or irods_vs_seqscape:
        irods_libraries = get_library_from_irods_metadata(irods_metadata)
        missing_ids = report_missing_identifiers(irods_libraries)
        diffs.extend(missing_ids)

    # Compare IRODS vs. HEADER:
    if irods_vs_header:
        header_libraries = get_entities_from_header_metadata(header_metadata.libraries)
        irods_vs_head_diffs = get_diff_irods_and_header_metadata(header_libraries, irods_libraries)
        diffs.extend(irods_vs_head_diffs)

    # Compare IRODS vs. SEQSCAPE:
    if irods_vs_seqscape:
        irods_vs_seqsc_diffs = get_diff_seqsc_and_irods_libraries_metadata(irods_libraries)
        diffs.extend(irods_vs_seqsc_diffs)
    return diffs


def run_tests_on_studies(irods_metadata):
    if not irods_metadata:
        print "ERROR - irods_metadata parameter missing. Returning now!"
        return

    diffs = []
    irods_studies = get_studies_from_irods_metadata(irods_metadata)
    missing_ids = report_missing_identifiers(irods_studies)
    diffs.extend(missing_ids)

    # Compare IRODS vs. SEQSCAPE:
    irods_vs_seqsc_diffs = get_diff_seqsc_and_irods_studies_metadata(irods_studies)
    diffs.extend(irods_vs_seqsc_diffs)
    return diffs


def run_metadata_tests(irods_fpath, irods_metadata, header_metadata=None,
                       samples_irods_vs_header=True, samples_irods_vs_seqscape=True,
                       libraries_irods_vs_header=True, libraries_irods_vs_seqscape=True,
                       study_irods_vs_seqscape=True, desired_ref=None):
    # if not irods_fpath:
    #     print "No file path provided. Returning."
    #     return
    #
    # irods_metadata = get_irods_metadata(irods_fpath)
    # header_metadata = None
    # if samples_irods_vs_header or libraries_irods_vs_header:
    #     header_metadata = get_header_metadata_from_irods_file(irods_fpath)

    issues = []
    if samples_irods_vs_header or samples_irods_vs_seqscape:
        sample_issues = run_tests_on_samples(irods_metadata, header_metadata, samples_irods_vs_header, samples_irods_vs_seqscape)
        if sample_issues:
            issues.extend(sample_issues)
            print "SAMPLES: " + str(sample_issues)

    if libraries_irods_vs_header or libraries_irods_vs_seqscape:
        library_issues = run_tests_on_libraries(irods_metadata, header_metadata, libraries_irods_vs_header, libraries_irods_vs_seqscape)
        if library_issues:
            issues.extend(library_issues)
            print "LIBRARIES: " + str(library_issues)

    if study_irods_vs_seqscape:
        study_issues = run_tests_on_studies(irods_metadata)
        if study_issues:
            issues.extend(study_issues)
            print "STUDIES: " + str(study_issues)

    checksum_issues = check_md5_metadata(irods_metadata, irods_fpath)
    if checksum_issues:
        print "CHECKSUM: " + str(checksum_issues)
        issues.extend(checksum_issues)

    run_id_issues = check_run_id(irods_metadata, irods_fpath)
    if run_id_issues:
        print "RUN IDS: " + str(run_id_issues)
        issues.extend(run_id_issues)

    lane_metadata_issues = check_lane_metadata(irods_metadata, irods_fpath)
    if lane_metadata_issues:
        print "LANE METADATA: " + str(lane_metadata_issues)
        issues.extend(lane_metadata_issues)

    lane_name_issues = check_lanelet_name(irods_fpath, header_metadata.lanelets)
    if lane_name_issues:
        print "LANE METADATA: " + str(lane_metadata_issues)
        issues.extend(lane_name_issues)

    if desired_ref:
        ref_issues = check_reference(irods_metadata, desired_ref)
        if ref_issues:
            print "REFERENCE: " + str(ref_issues)
            issues.extend(ref_issues)




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
        print "FILE: " + str(irods_fpath) + " has issues with:"
        if sample_issues:
            print "SAMPLES: " + str(sample_issues)
        if library_issues:
            print "LIBRARIES: " + str(library_issues)
        if study_issues:
            print "STUDIES: " + str(study_issues)
        if checksum_issues:
            print "CHECKSUM: " + str(checksum_issues)
        if run_id_issues:
            print "RUN IDS: " + str(run_id_issues)
        if lane_name_issues:
            print "LANE METADATA: " + str(lane_metadata_issues)
        if lane_name_issues:
            print "LANE NAME: " + str(lane_name_issues)
        if desired_ref and ref_issues:
            print "REFERENCE: " + str(ref_issues)


            # print "FILE: " + str(irods_fpath) + " ERRORS: " + str(diffs)
            # reference_file = extract_values_by_key_from_irods_metadata(irods_metadata, 'reference')


Args = namedtuple('Args', ['study', 'fpath_irods', 'check_samples',
                           'check_libraries', 'check_study_per_sample',
                           'check_irods_vs_header', 'check_irods_vs_seqscape'
])


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--study', required=False, help='Study name')
    parser.add_argument('--fpath_irods', required=False, help='Path in iRODS to a BAM')
    parser.add_argument('--samples_irods_vs_header', required=False, help='Add this flag if you want the samples '
                                                                          'to be checked - irods vs header')
    parser.add_argument('--samples_irods_vs_seqscape', required=False, help='Add this flag if you want the samples '
                                                                            'to be checked - irods vs sequencescape')
    parser.add_argument('--libraries_irods_vs_header', required=False, help='Add this flag if you want the libraries '
                                                                            'to he checked - irods vs header')

    parser.add_argument('--libraries_irods_vs_seqscape', required=False, help='Add this flag if you want to check '
                                                                              'the libraries irods vs sequencescape')
    parser.add_argument('--study_irods_vs_seqscape', required=False, help='Add this flag if you want to check '
                                                                          'the study from irods metadata')
    parser.add_argument('--desired_ref', required=False, help='Add this parameter if you want the reference '
                                                              'in irods metadata to be checked against this reference.')


    args = parser.parse_args()

    if not args.path_irods and not args.study:
        parser.print_help()
        print "No study provided, no BAM path given => NOTHING TO DO! EXITTING"
        exit(0)

    if not args.samples_irods_vs_header and not args.samples_irods_vs_seqscape \
            and not args.libraries_irods_vs_header \
            and not args.libraries_irods_vs_seqscape \
            and not args.study_irods_vs_seqscape:
        print "WARNING! You haven't selected neither samples to be checked, nor libraries, nor study. " \
              "Is this what you want? I will only check the adjacent metadata."
        parser.print_help()
        exit(0)

    return args


# CHECK LANELETS:

def main():
    args = parse_args()

    if args.path_irods:
        fpaths_irods = [args.path_irods]
    elif args.study:
        fpaths_irods = get_list_of_bams_for_study(args.study)
        print "fpaths for this study: " + str(fpaths_irods)

    for fpath in fpaths_irods:
#        test_file_metadata(fpath)
        if not fpath:
            continue

        irods_metadata = get_irods_metadata(fpath)
        header_metadata = None
        if args.samples_irods_vs_header or args.libraries_irods_vs_header:
            header_metadata = get_header_metadata_from_irods_file(fpath)

        run_metadata_tests(fpath, irods_metadata, header_metadata,
                       args.samples_irods_vs_header, args.samples_irods_vs_seqscape,
                       args.libraries_irods_vs_header, args.libraries_irods_vs_seqscape,
                       args.study_irods_vs_seqscape, args.desired_ref)

if __name__ == '__main__':
    main()





