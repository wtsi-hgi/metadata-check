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
from header_parser import bam_hparser
from irods import api as irods

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


def get_header_metadata(path):
    full_header = bam_hparser.BAMHeaderParser.extract_header(path)
    return full_header.rg


def get_irods_metadata(irods_path):
    return irods.iRODSAPI.get_metadata(irods_path)


def extract_values_by_key_from_irods_metadata(avus_list, key):
    results = []
    for avu in avus_list:
        if avu.attribute == key:
            results.append(avu.value)
    return results


def get_list_of_files_for_study(study_name):
    return irods.iRODSAPI.get_files_list_by_metadata('study', study_name)


def check_samples():
    pass


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
        fpaths_irods = get_list_of_files_for_study(study_name)
    else:
        print "No arguments provided! Exitting"
        return
    for fpath in fpaths_irods:
        metadata = get_irods_metadata(fpath)
        sample_name = extract_values_by_key_from_irods_metadata(metadata, 'sample')
        sample_acc_nr = extract_values_by_key_from_irods_metadata(metadata, 'sample_accession_number')
        sample_internal_id = extract_values_by_key_from_irods_metadata(metadata, 'sample_id')
        print "SAMPLE name: "+str(sample_name)
        print "sample_ acc nr:"+str(sample_acc_nr)
        print "sample internal id: "+str(sample_internal_id)

        study_internal_id = extract_values_by_key_from_irods_metadata(metadata, 'study_id')
        study_acc_nr = extract_values_by_key_from_irods_metadata(metadata, 'study_accession_number')

        library_name = extract_values_by_key_from_irods_metadata(metadata, 'library')
        library_internal_id = extract_values_by_key_from_irods_metadata(metadata, 'library_id')

        run_id = extract_values_by_key_from_irods_metadata(metadata, 'id_run')
        lane_id = extract_values_by_key_from_irods_metadata(metadata, 'lane')
        tag_id = extract_values_by_key_from_irods_metadata(metadata, 'tag_index')

        md5 = extract_values_by_key_from_irods_metadata(metadata, 'md5')

        reference_file = extract_values_by_key_from_irods_metadata(metadata, 'reference')



if __name__ == '__main__':
    main()





