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
from irods import icommands_wrapper as irods_wrapper
from seqscape import queries as seqsc

import utils
import library_tests, study_tests, sample_tests


def check_md5_metadata(irods_metadata, irods_fpath):
    md5_metadata = utils.extract_values_by_key_from_irods_metadata(irods_metadata, 'md5')
    if not md5_metadata:
        print "This file doesn't have md5 in irods metadata"
        return []


    md5_chksum = irods_wrapper.iRODSChecksumOperations.get_checksum(irods_fpath)
    if md5_chksum:
        if not md5_metadata[0] == md5_chksum.md5:
            return [
                "iRODS metadata md5 (" + str(md5_metadata) + ") != ichksum (" + str(md5_chksum) + ") "]
    return []


def check_run_id(irods_metadata, irods_fpath):
    """
    This test assumes that all the files in iRODS have exactly 1 run (=LANELETS)
    """
    irods_run_ids = utils.extract_values_by_key_from_irods_metadata(irods_metadata, 'id_run')
    path_run_id = utils.get_run_from_irods_path(irods_fpath)
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
    lane_id = utils.get_lane_from_irods_path(irods_fpath)
    irods_lane_ids = utils.extract_values_by_key_from_irods_metadata(irods_metadata, 'lane')
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



def check_lanelet_name(irods_fpath, header_lanelets):
    if len(header_lanelets) != 1:
        return [" > 1 lanelets in the header."]
    irods_lanelet_name = utils.extract_lanelet_name_from_irods_fpath(irods_fpath)
    if irods_lanelet_name != header_lanelets[0]:
        return [
            "HEADER LANELET = " + str(header_lanelets[0]) + " different from FILE NAME = " + str(irods_lanelet_name)]
    return []



def check_reference(irods_metadata, desired_ref):
    ref_paths = utils.extract_values_by_key_from_irods_metadata(irods_metadata, 'reference')
    if len(ref_paths) > 1:
        return [" > 1 REFERENCE ATTRIBUTE in iRODS metadata"]
    elif len(ref_paths) < 1:
        return ["NO REFERENCE ATTRIBUTE in iRODS metadata"]
    else:
        ref_path = ref_paths[0]
    ref_name = utils.extract_reference_name_from_path(ref_path)
    if ref_name != desired_ref:
        return ["WANTED REFERENCE =: " + str(desired_ref) + " different from ACTUAL REFERENCE = " + str(ref_name)]
    return []


def run_irods_seq_specific_tests(irods_path, irods_metadata, header_metadata, desired_ref=None):
    issues = []
    checksum_issues = check_md5_metadata(irods_metadata, irods_path)
    if checksum_issues:
        print "CHECKSUM: " + str(checksum_issues)
        issues.extend(checksum_issues)

    run_id_issues = check_run_id(irods_metadata, irods_path)
    if run_id_issues:
        print "RUN IDS: " + str(run_id_issues)
        issues.extend(run_id_issues)

    lane_metadata_issues = check_lane_metadata(irods_metadata, irods_path)
    if lane_metadata_issues:
        print "LANE METADATA: " + str(lane_metadata_issues)
        issues.extend(lane_metadata_issues)

    lane_name_issues = check_lanelet_name(irods_path, header_metadata.lanelets)
    if lane_name_issues:
        print "LANE METADATA: " + str(lane_metadata_issues)
        issues.extend(lane_name_issues)

    if desired_ref:
        ref_issues = check_reference(irods_metadata, desired_ref)
        if ref_issues:
            print "REFERENCE: " + str(ref_issues)
            issues.extend(ref_issues)
    return issues


def run_metadata_tests(irods_fpath, irods_metadata, header_metadata=None,
                       samples_irods_vs_header=True, samples_irods_vs_seqscape=True,
                       libraries_irods_vs_header=True, libraries_irods_vs_seqscape=True,
                       study_irods_vs_seqscape=True, collateral_irods_seq_tests=True, desired_ref=None):

    print "File: "+irods_fpath
    issues = []
    if samples_irods_vs_header or samples_irods_vs_seqscape:
        sample_issues = sample_tests.run_tests_on_samples(irods_metadata, header_metadata, samples_irods_vs_header, samples_irods_vs_seqscape)
        if sample_issues:
            issues.extend(sample_issues)
            print "SAMPLES: " + str(sample_issues)

    if libraries_irods_vs_header or libraries_irods_vs_seqscape:
        library_issues = library_tests.run_tests_on_libraries(irods_metadata, header_metadata, libraries_irods_vs_header, libraries_irods_vs_seqscape)
        if library_issues:
            issues.extend(library_issues)
            print "LIBRARIES: " + str(library_issues)

    if study_irods_vs_seqscape:
        study_issues = study_tests.run_tests_on_studies(irods_metadata)
        if study_issues:
            issues.extend(study_issues)
            print "STUDIES: " + str(study_issues)

    if collateral_irods_seq_tests:
        collateral_issues = run_irods_seq_specific_tests(irods_fpath, irods_metadata, header_metadata, desired_ref)
        if collateral_issues:
            issues.extend(collateral_issues)
            print "IRODS SEQUENCING SPECIFIC TESTS - ISSUES: " + str(collateral_issues)

    if not issues:
        print "OK"



def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--study', required=False, help='Study name')
    parser.add_argument('--fpath_irods', required=False, help='Path in iRODS to a BAM')
    parser.add_argument('--samples_irods_vs_header', action='store_true', required=False,
                        help='Add this flag if you want the samples to be checked - irods vs header')
    parser.add_argument('--samples_irods_vs_seqscape', action='store_true', required=False,
                        help='Add this flag if you want the samples to be checked - irods vs sequencescape')
    parser.add_argument('--libraries_irods_vs_header', action='store_true', required=False,
                        help='Add this flag if you want the libraries to he checked - irods vs header')

    parser.add_argument('--libraries_irods_vs_seqscape', action='store_true', required=False,
                        help='Add this flag if you want to check the libraries irods vs sequencescape')
    parser.add_argument('--study_irods_vs_seqscape', action='store_true', required=False,
                        help='Add this flag if you want to check the study from irods metadata')
    parser.add_argument('--desired_ref', required=False,
                        help='Add this parameter if you want the reference in irods metadata to be checked '
                             'against this reference.')
    parser.add_argument('--collateral_irods_seq_tests', required=False,
                        help='This is a test suite consisting of checks specific for sequencing data released by NPG, '
                             'such as md5, lane id, run id')



    args = parser.parse_args()

    if not args.fpath_irods and not args.study:
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



def get_files_by_study_in_irods(study_name):
    return utils.get_list_of_bams_for_study(study_name)


def get_files_from_fofn(fofn_path):
    pass


def main():
    args = parse_args()

    if args.fpath_irods:
        fpaths_irods = [args.fpath_irods]
    elif args.study:
        fpaths_irods = get_files_by_study_in_irods(args.study)
        print "fpaths for this study: " + str(fpaths_irods)
    else:
        print "No study provided, no BAM path given => NOTHING TO DO! EXITTING"
        return

    for fpath in fpaths_irods:
#        test_file_metadata(fpath)
        if not fpath:
            continue

        # determine location....
        location = 'irods'
        irods_metadata = None
        if location is 'irods':
            irods_metadata = utils.get_irods_metadata(fpath)

        header_metadata = None
        if args.samples_irods_vs_header or args.libraries_irods_vs_header:
            if location == 'irods':
                header_metadata = utils.get_header_metadata_from_irods_file(fpath)
            else:
                header_metadata = utils.get_header_metadata_from_lustre_file(fpath)

        run_metadata_tests(fpath, irods_metadata, header_metadata,
                       args.samples_irods_vs_header, args.samples_irods_vs_seqscape,
                       args.libraries_irods_vs_header, args.libraries_irods_vs_seqscape,
                       args.study_irods_vs_seqscape, args.desired_ref)

if __name__ == '__main__':
    main()


