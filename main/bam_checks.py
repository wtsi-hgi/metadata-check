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
from irods import  api_wrapper as irods_wrapper

def extract_fname_from_path(fpath):
    _, fname = os.path.split(fpath)
    return fname


def extract_lanelet_name(lanelet_path):
    lanelet_file = os.path.basename(lanelet_path)
    return lanelet_file


def guess_irods_path(lustre_path):
    fname = extract_fname_from_path(lustre_path)
    run_id = fname.split("_")
    irods_fpath = "/seq/"+run_id[0]+"/"+fname
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


def check_sample_metadata(header_metadata, irods_metadata):
    # samples_identifiers = header_metadata.samples

    irods_sample_names_list = extract_values_by_key_from_irods_metadata(irods_metadata, 'sample')
    irods_sample_acc_nr_list = extract_values_by_key_from_irods_metadata(irods_metadata, 'sample_accession_number')
    irods_sample_internal_id_list = extract_values_by_key_from_irods_metadata(irods_metadata, 'sample_id')

    # print "IRODS samples:"+str(irods_sample_names_list)
    # print "IRODS SAMPLES ACC NRS: "+str(irods_sample_acc_nr_list)+"\n"
    # print "IRODS SAMPLE INTERNAL IDS: "+str(irods_sample_internal_id_list)

    header_samples_identifiers_tuples = [(Identif.guess_identifier_type(sample), sample) for sample in header_metadata.samples]
#    print "HEADER SAMPLES:"+str(header_samples_identifiers_tuples)

    # Compare sample identifiers:
    error = False
    for id_type, id_val in header_samples_identifiers_tuples:
        if id_type == 'accession_number':
            if id_val not in irods_sample_acc_nr_list:
                print "ERROR - this sample accession number appears in the header, but not in the metadata:"+str(id_val)
                print "Header SAMPLE accession numbers: "+str(id_val)
                print "IRODS SAMPLE accession numbers: "+str(irods_sample_acc_nr_list)
                error = True
        elif id_type == 'name':
            if id_val not in irods_sample_names_list:
                print "ERROR - this sample name appears in the header, but not in the irods metadata: "+str(id_val)
                print "Header SAMPLE name: "+str(id_val)
                print "IRODS SAMPLE names: "+str(irods_sample_names_list)
                error = True
        elif id_type == 'internal_id':
            if id_val not in irods_sample_internal_id_list:
                print "ERROR - this sample id appears in the header, but not in the irods metadata: "+str(id_val)
                print "Header SAMPLE internal_id: "+str(id_val)
                print "IRODS SAMPLE internal_id: "+str(irods_sample_internal_id_list)
                error = True
        if not error:
            print "OK"
        else:
            error = False

    # print "SAMPLE name: "+str(irods_sample_names_list)
    # print "sample_ acc nr:"+str(irods_sample_acc_nr_list)
    # print "sample internal id: "+str(irods_sample_internal_id_list)


def check_library_metadata(header_metadata, irods_metadata):
    irods_lib_names_list = extract_values_by_key_from_irods_metadata(irods_metadata, 'library')
    irods_lib_ids_list = extract_values_by_key_from_irods_metadata(irods_metadata, 'library_id')

    header_lib_identifiers_tuples = [(Identif.guess_identifier_type(lib), lib) for lib in header_metadata.libraries]

    print "IRODS LIBRARY names: "+str(irods_lib_names_list)
    print "IRODS LIBRARY ids: "+str(irods_lib_ids_list)
    print "HEADER LIBRARIES: "+str(header_lib_identifiers_tuples)

    error = False
    for lib_identif in header_lib_identifiers_tuples:
        if lib_identif not in irods_lib_ids_list and lib_identif not in irods_lib_names_list:
            print "ERROR Library in the header, but not in the iRODS metadata: "+str(lib_identif)
            print "IRODS libraries name: "+str(irods_lib_names_list)
            print "IRODS library ids: "+str(irods_lib_ids_list)
            error = True
        if error:
            error = False
        else:
            print "File OK"


def test_file_metadata(irods_fpath):
    header_metadata = get_header_metadata_from_irods_file(irods_fpath)
    irods_metadata = get_irods_metadata(irods_fpath)

    print "FILE: "+str(irods_fpath)

    #print "HEADER METADATA: "+str(header_metadata)
    check_sample_metadata(header_metadata, irods_metadata)

    study_internal_id = extract_values_by_key_from_irods_metadata(irods_metadata, 'study_id')
    study_acc_nr = extract_values_by_key_from_irods_metadata(irods_metadata, 'study_accession_number')

    library_name = extract_values_by_key_from_irods_metadata(irods_metadata, 'library')
    library_internal_id = extract_values_by_key_from_irods_metadata(irods_metadata, 'library_id')

    run_id = extract_values_by_key_from_irods_metadata(irods_metadata, 'id_run')
    lane_id = extract_values_by_key_from_irods_metadata(irods_metadata, 'lane')
    tag_id = extract_values_by_key_from_irods_metadata(irods_metadata, 'tag_index')

    md5 = extract_values_by_key_from_irods_metadata(irods_metadata, 'md5')

    reference_file = extract_values_by_key_from_irods_metadata(irods_metadata, 'reference')


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
        print "FPATHS for this study: "+str(fpaths_irods)
    else:
        print "No arguments provided! Exitting"
        return
    for fpath in fpaths_irods:
        test_file_metadata(fpath)


if __name__ == '__main__':
    main()





