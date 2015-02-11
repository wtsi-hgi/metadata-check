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
# from collections import namedtuple
# from header_parser import bam_h_analyser as h_analyser
# from identifiers import EntityIdentifier as Identif
# from irods import api as irods
# from irods import icommands_wrapper as irods_wrapper
# from seqscape import queries as seqsc

import utils
import library_tests, study_tests, sample_tests
from main import irods_seq_data_tests as seq_tests



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



def run_metadata_tests(irods_fpath, irods_metadata, header_metadata=None,
                       samples_irods_vs_header=True, samples_irods_vs_seqscape=True,
                       libraries_irods_vs_header=True, libraries_irods_vs_seqscape=True,
                       study_irods_vs_seqscape=True, collateral_irods_seq_tests=True, desired_ref=None):

    if not irods_metadata and (samples_irods_vs_header or samples_irods_vs_seqscape
                               or libraries_irods_vs_header or libraries_irods_vs_seqscape or study_irods_vs_seqscape):
        raise ValueError("ERROR - the irods_metadata param hasn't been given, though the irods tests were requested.")
    if not header_metadata and (samples_irods_vs_header or libraries_irods_vs_header):
        raise ValueError("ERROR - the header_metadata param hasn't been given, though the header tests were requested.")

    print "File: "+irods_fpath

    # SAMPLE TESTS:
    issues = []
    if samples_irods_vs_header or samples_irods_vs_seqscape:
        irods_samples = sample_tests.extract_samples_from_irods_metadata(irods_metadata)
        missing_ids = check_all_identifiers_in_metadata(irods_samples)
        issues.extend(missing_ids)

    if samples_irods_vs_header:
        header_samples = utils.HeaderUtils.sort_entities_by_guessing_id_type(header_metadata.samples)
        irods_vs_head_diffs = get_diff_irods_and_header_metadata(header_samples, irods_samples)
        issues.extend(irods_vs_head_diffs)

    if samples_irods_vs_seqscape:
        irods_vs_seqsc_diffs = sample_tests.compare_sample_sets_obtained_by_seqscape_ids_lookup(irods_samples)
        issues.extend(irods_vs_seqsc_diffs)


    # LIBRARY TESTS:
    if libraries_irods_vs_header or libraries_irods_vs_seqscape:
        irods_libraries = utils.iRODSUtils.extract_libraries_from_irods_metadata(irods_metadata)
        missing_ids = check_all_identifiers_in_metadata(irods_libraries, accession_number=False, name=False)
        issues.extend(missing_ids)

    if libraries_irods_vs_header:
        header_libraries = utils.HeaderUtils.sort_entities_by_guessing_id_type(header_metadata.libraries)
        irods_vs_head_diffs = get_diff_irods_and_header_metadata(header_libraries, irods_libraries)
        issues.extend(irods_vs_head_diffs)

    if libraries_irods_vs_seqscape:
        irods_vs_seqsc_diffs = library_tests.compare_library_sets_obtained_by_seqscape_ids_lookup(irods_libraries)
        issues.extend(irods_vs_seqsc_diffs)


    # STUDY TESTS:
    if study_irods_vs_seqscape:
        irods_studies = utils.iRODSUtils.extract_studies_from_irods_metadata(irods_metadata)
        missing_ids = check_all_identifiers_in_metadata(irods_studies)
        issues.extend(missing_ids)

        # Compare IRODS vs. SEQSCAPE:
        irods_vs_seqsc_diffs = study_tests.compare_study_sets_obtained_by_seqscape_ids_lookup(irods_studies)
        issues.extend(irods_vs_seqsc_diffs)


    # OTHER TESTS:
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


def get_files_from_fofn(fofn_path):
    pass


# TODO: write in README - actually all these tests apply only to irods seq data...
def main():
    args = parse_args()

    if args.fpath_irods:
        fpaths_irods = [args.fpath_irods]
    elif args.study:
        fpaths_irods = utils.retrieve_list_of_bams_by_study_from_irods(args.study)
        print "fpaths for this study: " + str(fpaths_irods)
    else:
        print "No study provided, no BAM path given => NOTHING TO DO! EXITTING"
        return

    for fpath in fpaths_irods:
        if not fpath:
            continue

        header_metadata = None
        if args.samples_irods_vs_header or args.libraries_irods_vs_header:
            irods_metadata = utils.iRODSUtils.retrieve_irods_metadata(fpath)
            header_metadata = utils.iRODSUtils.get_header_metadata_from_irods_file(fpath)

            run_metadata_tests(fpath, irods_metadata, header_metadata,
                   args.samples_irods_vs_header, args.samples_irods_vs_seqscape,
                   args.libraries_irods_vs_header, args.libraries_irods_vs_seqscape,
                   args.study_irods_vs_seqscape, args.desired_ref)
            # else:
            #     header_metadata = utils.get_header_metadata_from_lustre_file(fpath)
            #     #TODO: Think of use cases in which we check a file on lustre...
            #     pass

if __name__ == '__main__':
    main()


