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
from main import irods_seq_data_tests as seq_tests


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
        collateral_issues = seq_tests.run_irods_seq_specific_tests(irods_fpath, irods_metadata, header_metadata, desired_ref)
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
    return utils.retrieve_list_of_bams_by_study_from_irods(study_name)


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
        location = 'irods' # for now
        header_metadata = None
        if args.samples_irods_vs_header or args.libraries_irods_vs_header:
            if location == 'irods':
                irods_metadata = utils.retrieve_irods_metadata(fpath)
                header_metadata = utils.get_header_metadata_from_irods_file(fpath)

                run_metadata_tests(fpath, irods_metadata, header_metadata,
                       args.samples_irods_vs_header, args.samples_irods_vs_seqscape,
                       args.libraries_irods_vs_header, args.libraries_irods_vs_seqscape,
                       args.study_irods_vs_seqscape, args.desired_ref)
            else:
                header_metadata = utils.get_header_metadata_from_lustre_file(fpath)
                #TODO: Think of use cases in which we check a file on lustre...
                pass

if __name__ == '__main__':
    main()


