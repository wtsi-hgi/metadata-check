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


def get_studies_from_seqsc(ids_list, id_type):
    return seqsc.query_all_studies_as_batch(ids_list, id_type)


def get_diff_seqsc_and_irods_samples_metadata(irods_samples):
    seqsc_samples_by_name = get_samples_from_seqsc(irods_samples['name'], 'name')
    seqsc_samples_by_acc_nr = get_samples_from_seqsc(irods_samples['accession_number'], 'accession_number')
    seqsc_samples_by_internal_id = get_samples_from_seqsc(irods_samples['internal_id'], 'internal_id')

    print "BY NAME: "+str(seqsc_samples_by_name)
    print "BY ACC NR: "+str(seqsc_samples_by_acc_nr)
    print set(seqsc_samples_by_acc_nr) == set(seqsc_samples_by_internal_id) == set(seqsc_samples_by_name)
    differences = []
    if not (set(seqsc_samples_by_acc_nr) == set(seqsc_samples_by_internal_id) == set(seqsc_samples_by_name)):
        diff = "Sample identifiers from iRODS don't identify the same set of samples: by name: " + \
               str(seqsc_samples_by_name) + \
               " by accession_number:" + str(seqsc_samples_by_acc_nr) + \
               " by internal_id: " + str(seqsc_samples_by_internal_id)
        differences.append(diff)
        print "DIFFS: "+str(differences)
    return differences


def get_diff_seqsc_and_irods_studies_metadata(irods_studies):
    seqsc_studies_by_name = get_studies_from_seqsc(irods_studies['name'], 'name')
    seqsc_studies_by_acc_nr = get_studies_from_seqsc(irods_studies['accession_number'], 'accession_number')
    seqsc_studies_by_internal_id = get_studies_from_seqsc(irods_studies['internal_id'], 'internal_id')

    differences = []
    if not (set(seqsc_studies_by_acc_nr) == set(seqsc_studies_by_internal_id) == set(seqsc_studies_by_name)):
        diff = "Study identifiers from iRODS don't identify the same set of studies: by name: " + \
               str(seqsc_studies_by_name) + \
               " by accession_number:" + str(seqsc_studies_by_acc_nr) + \
               " by internal_id: " + str(seqsc_studies_by_internal_id)
        differences.append(diff)
    return differences


def get_diff_seqsc_and_irods_libraries_metadata(irods_libraries):
    seqsc_libraries_by_name = get_libraries_from_seqsc(irods_libraries['name'], 'name')
    seqsc_libraries_by_internal_id = get_libraries_from_seqsc(irods_libraries['internal_id'], 'internal_id')

    differences = []
    if not (set(seqsc_libraries_by_internal_id) == set(seqsc_libraries_by_name)):
        diff = "Libraries identifiers from iRODS don't identify the same set of studies: by name: " + \
               str(seqsc_libraries_by_name) + \
               " by internal_id: " + str(seqsc_libraries_by_internal_id)
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
            differences.append("The header contains entities that are not present in iRODS: " + str(head_ids_list))
        elif set(head_ids_list).difference(set(irods_dict[id_type])):
            differences.append("The header contains entities that are not present in iRODS: " + str(head_ids_list))
    return differences


def check_sample_metadata(header_metadata, irods_metadata):
    irods_sample_names_list = extract_values_by_key_from_irods_metadata(irods_metadata, 'sample')
    irods_sample_acc_nr_list = extract_values_by_key_from_irods_metadata(irods_metadata, 'sample_accession_number')
    irods_sample_internal_id_list = extract_values_by_key_from_irods_metadata(irods_metadata, 'sample_id')
    irods_samples = {'name': irods_sample_names_list,
                     'accession_number': irods_sample_acc_nr_list,
                     'internal_id': irods_sample_internal_id_list
    }
    header_samples = {'name': [], 'accession_number': [], 'internal_id': []}
    for sample in header_metadata.samples:
        id_type = Identif.guess_identifier_type(sample)
        header_samples[id_type].append(sample)

    # Compare IRODS vs. HEADER:
    irods_vs_head_diffs = get_diff_irods_and_header_metadata(header_samples, irods_samples)

    # Compare IRODS vs. SEQSCAPE:
    irods_vs_seqsc_diffs = get_diff_seqsc_and_irods_samples_metadata(irods_samples)
    return irods_vs_head_diffs + irods_vs_seqsc_diffs


def check_library_metadata(header_metadata, irods_metadata):
    irods_lib_names_list = extract_values_by_key_from_irods_metadata(irods_metadata, 'library')
    irods_lib_internal_id_list = extract_values_by_key_from_irods_metadata(irods_metadata, 'library_id')
    irods_libraries = {'name': irods_lib_names_list,
                       'internal_id': irods_lib_internal_id_list}
    header_libraries = {'name': [], 'internal_id': []}

    for lib in header_metadata.libraries:
        id_type = Identif.guess_identifier_type(lib)
        header_libraries[id_type].append(lib)

    # Compare IRODS vs. HEADER:
    irods_vs_head_diffs = get_diff_irods_and_header_metadata(header_libraries, irods_libraries)

    # Compare IRODS vs. SEQSCAPE:
    irods_vs_seqsc_diffs = get_diff_seqsc_and_irods_libraries_metadata(irods_libraries)
    return irods_vs_head_diffs + irods_vs_seqsc_diffs


def check_study_metadata(irods_metadata):
    irods_study_names_list = extract_values_by_key_from_irods_metadata(irods_metadata, 'study')
    irods_study_internal_id_list = extract_values_by_key_from_irods_metadata(irods_metadata, 'study_id')
    irods_study_acc_nr_list = extract_values_by_key_from_irods_metadata(irods_metadata, 'study_accession_number')
    irods_studies = {'name': irods_study_names_list,
                     'internal_id': irods_study_internal_id_list,
                     'accession_number': irods_study_acc_nr_list
    }

    # Compare IRODS vs. SEQSCAPE:
    irods_vs_seqsc_diffs = get_diff_seqsc_and_irods_studies_metadata(irods_studies)
    return irods_vs_seqsc_diffs


def check_md5_metadata(irods_metadata, irods_fpath):
    md5_metadata = extract_values_by_key_from_irods_metadata(irods_metadata, 'md5')
    md5_chksum = irods_wrapper.iRODSChecksumOperations.get_checksum(irods_fpath)
    if not md5_metadata == md5_chksum:
        return [
            "The md5 in the iRODS metadata is different from what ichksum returns: " + str(md5_chksum) + " vs. " + str(
                md5_metadata)]
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
    return irods_fpath.split("\\")[-2]


def get_lane_from_irods_path(irods_fpath):
    fname = irods_fpath.split("\\")[-1]
    lane_id = fname.split("_")[1].split("#")[1]
    return lane_id


def check_run_metadata(irods_metadata, irods_fpath):
    irods_run_id = extract_values_by_key_from_irods_metadata(irods_metadata, 'id_run')
    path_run_id = get_run_from_irods_path(irods_fpath)
    if not irods_run_id == path_run_id:
        return ["The run id in the iRODS file path is not the same as the run id in the iRODS metadata: " + \
                str(irods_run_id) + " vs. " + str(path_run_id)]
    return []


def check_lane_metadata(irods_metadata, irods_fpath):
    irods_lane_id = extract_values_by_key_from_irods_metadata(irods_metadata, 'lane')
    lane_id = get_lane_from_irods_path(irods_fpath)
    if not irods_lane_id == lane_id:
        return ["The lane id in the iRODS file path is not the same as the lane id in the iRODS metadata: " +
                str(irods_lane_id) + " vs. " + str(lane_id)]
    return []


def check_reference(irods_metadata, desired_ref):
    irods_ref = extract_values_by_key_from_irods_metadata(irods_metadata, 'reference')
    ref_file_name = os.path.basename(irods_ref)
    ref_name = ref_file_name.split(".")[0]
    if ref_name != desired_ref:
        return ["This file hasn't been mapped to the reference I want: " + str(irods_ref)]
    return []


def test_file_metadata(irods_fpath):
    header_metadata = get_header_metadata_from_irods_file(irods_fpath)
    irods_metadata = get_irods_metadata(irods_fpath)

    diffs = []
    diffs.extend(check_sample_metadata(header_metadata, irods_metadata))
    diffs.extend(check_library_metadata(header_metadata, irods_metadata))
    diffs.extend(check_study_metadata(header_metadata, irods_metadata))

    # study_internal_id = extract_values_by_key_from_irods_metadata(irods_metadata, 'study_id')
    # study_acc_nr = extract_values_by_key_from_irods_metadata(irods_metadata, 'study_accession_number')
    #
    # library_name = extract_values_by_key_from_irods_metadata(irods_metadata, 'library')
    # library_internal_id = extract_values_by_key_from_irods_metadata(irods_metadata, 'library_id')

    # run_id = extract_values_by_key_from_irods_metadata(irods_metadata, 'id_run')
    # lane_id = extract_values_by_key_from_irods_metadata(irods_metadata, 'lane')
    # tag_id = extract_values_by_key_from_irods_metadata(irods_metadata, 'tag_index')

    # md5 = extract_values_by_key_from_irods_metadata(irods_metadata, 'md5')
    diffs.extend(check_md5_metadata(irods_metadata, irods_fpath))
    print "FILE: " + str(irods_fpath) + " ERRORS: " + str(diffs)


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





