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
                       study_irods_vs_seqscape=True, collateral_tests=True, desired_ref=None):

    if not irods_metadata and (samples_irods_vs_header or samples_irods_vs_seqscape
                               or libraries_irods_vs_header or libraries_irods_vs_seqscape or study_irods_vs_seqscape):
        raise ValueError("ERROR - the irods_metadata param hasn't been given, though the irods tests were requested.")
    if not header_metadata and (samples_irods_vs_header or libraries_irods_vs_header):
        raise ValueError("ERROR - the header_metadata param hasn't been given, though the header tests were requested.")

    print "File: "+irods_fpath

    # SAMPLE TESTS:
    issues = []
    if samples_irods_vs_header or samples_irods_vs_seqscape:
        irods_samples = utils.iRODSUtils.extract_samples_from_irods_metadata(irods_metadata)
        missing_ids = check_all_identifiers_in_metadata(irods_samples)
        issues.extend(["SAMPLE IDENTIFIERS MISSING - inconsistencies between irods metadata that identifies samples : " + id for id in missing_ids])

    if samples_irods_vs_header:
        header_samples = utils.HeaderUtils.sort_entities_by_guessing_id_type(header_metadata.samples)
        irods_vs_head_diffs = get_diff_irods_and_header_metadata(header_samples, irods_samples)
        issues.extend(["SAMPLE differences IRODS vs HEADER METADATA: " + diff for diff in irods_vs_head_diffs])

    if samples_irods_vs_seqscape:
        irods_vs_seqsc_diffs = sample_tests.compare_sample_sets_obtained_by_seqscape_ids_lookup(irods_samples)
        issues.extend(["SAMPLE differences IRODS vs SEQSCAPE METADATA: " + diff for diff in irods_vs_seqsc_diffs])


    # LIBRARY TESTS:
    if libraries_irods_vs_header or libraries_irods_vs_seqscape:
        irods_libraries = utils.iRODSUtils.extract_libraries_from_irods_metadata(irods_metadata)
        missing_ids = check_all_identifiers_in_metadata(irods_libraries, accession_number=False, name=False)
        issues.extend(["LIBRARY IDENTIFIERS MISSING - inconsistencies between sample identifiers extracted from IRODS metadata :" + id for id in missing_ids])

    if libraries_irods_vs_header:
        header_libraries = utils.HeaderUtils.sort_entities_by_guessing_id_type(header_metadata.libraries)
        irods_vs_head_diffs = get_diff_irods_and_header_metadata(header_libraries, irods_libraries)
        issues.extend(["LIBRARY differences IRODS vs HEADER:" + diff for diff in irods_vs_head_diffs])

    if libraries_irods_vs_seqscape:
        irods_vs_seqsc_diffs = library_tests.compare_library_sets_obtained_by_seqscape_ids_lookup(irods_libraries)
        issues.extend(["LIBRARY differences IRODS vs SEQSCAPE: " + diff for diff in irods_vs_seqsc_diffs])


    # STUDY TESTS:
    if study_irods_vs_seqscape:
        irods_studies = utils.iRODSUtils.extract_studies_from_irods_metadata(irods_metadata)
        missing_ids = check_all_identifiers_in_metadata(irods_studies)
        issues.extend(["STUDY IDENTIFIERS MISSING  - inconsistencies between study identifiers extracted from IRODS metadata" + id for id in missing_ids])

        # Compare IRODS vs. SEQSCAPE:
        irods_vs_seqsc_diffs = study_tests.compare_study_sets_obtained_by_seqscape_ids_lookup(irods_studies)
        issues.extend(["STUDY differences IRODS vs. SEQSCAPE: " + diff for diff in irods_vs_seqsc_diffs])


    # OTHER TESTS:
    if collateral_tests:
        collateral_issues = seq_tests.run_irods_seq_specific_tests(irods_fpath, irods_metadata, header_metadata, desired_ref)
        if collateral_issues:
            issues.extend(collateral_issues)
            print "IRODS SEQUENCING SPECIFIC TESTS - ISSUES: " + str(collateral_issues)

    if not issues:
        print "OK"
    else:
        print issues



def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--study', required=False, help='Study name')
    parser.add_argument('--fpaths_irods', required=False, help='List of file paths in iRODS')
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
    parser.add_argument('--collateral_tests', required=False,
                        help='This is a test suite consisting of checks specific for sequencing data released by NPG, '
                             'such as md5, lane id, run id')
    parser.add_argument('--fofn', required=False,
                        help='The path to a fofn containing file paths from iRODS '
                             'for the files one wants to run tests on')


    args = parser.parse_args()

    if not args.fpaths_irods and not args.study:
        parser.print_help()
        print "No study provided, no BAM path given => NOTHING TO DO! EXITTING"
        exit(0)

    if not args.samples_irods_vs_header and not args.samples_irods_vs_seqscape \
            and not args.libraries_irods_vs_header \
            and not args.libraries_irods_vs_seqscape \
            and not args.study_irods_vs_seqscape:
        print "WARNING! You haven't selected neither samples to be checked, nor libraries, nor study. " \
              "Nothing to be done!"
        parser.print_help()
        exit(0)

    return args


def read_fofn_into_list(fofn_path):
    fofn_fd = open(fofn_path)
    files_list = [f for f in fofn_fd]
    fofn_fd.close()
    return files_list


def collect_fpaths_from_args(study=None, files_list=None, fofn_path=None):
    if study:
        fpaths_irods = utils.iRODSUtils.retrieve_list_of_bams_by_study_from_irods(study)
        print "fpaths for this study: " + str(fpaths_irods)
    elif fofn_path:
        fpaths_irods = read_fofn_into_list(fofn_path)
    elif files_list:
        fpaths_irods = files_list
    return fpaths_irods


def start_tests(study=None, fpaths=None, fofn_path=None, samples_irods_vs_header=True, samples_irods_vs_seqscape=True,
                libraries_irods_vs_header=True, libraries_irods_vs_seqscape=True, study_irods_vs_seqscape=True,
                collateral_tests=True, desired_ref=None):

    fpaths_irods = collect_fpaths_from_args(study, fpaths, fofn_path)
    for fpath in fpaths_irods:
        if not fpath:
            continue
        if samples_irods_vs_header or libraries_irods_vs_header:
            irods_metadata = utils.iRODSUtils.retrieve_irods_metadata(fpath)
            header_metadata = utils.HeaderUtils.get_header_metadata_from_irods_file(fpath)
            run_metadata_tests(fpath, irods_metadata, header_metadata,
                   samples_irods_vs_header, samples_irods_vs_seqscape,
                   libraries_irods_vs_header, libraries_irods_vs_seqscape,
                   study_irods_vs_seqscape, collateral_tests, desired_ref)


# TODO: write in README - actually all these tests apply only to irods seq data...
def main():
    args = parse_args()
    start_tests(args.study, args.fpaths_irods, args.fofn, args.samples_irods_vs_header, args.samples_irods_vs_seqscape,
                args.libraries_irods_vs_header, args.libraries_irods_vs_seqscape, args.study_irods_vs_seqscape,
                args.collateral_tests, args.desired_ref)


if __name__ == '__main__':
    main()


