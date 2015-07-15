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

This file has been created on Jun 23, 2015.
"""

import argparse
import constants


def parse_args():

    parser = argparse.ArgumentParser(prog='Metadata Checks')
    input = parser.add_argument_group('INPUT',
                                            'Choose one or more ways of getting the list of files to check'
    )
    input_grp = input.add_mutually_exclusive_group(required=True)
    input_grp.add_argument('--study', required=False, help='Study name')
    input_grp.add_argument('--fpath_irods',
                           required=False,
                           nargs='*',
                           dest='files',
                           #action='append',
                           help='List of file paths in iRODS')
    input_grp.add_argument('--fofn',
                           required=False,
                           help='The path to a fofn containing file paths from iRODS '
                             'for the files one wants to run tests on')
    input_grp.add_argument('--sample',
                           required=False,
                           nargs='*',
                           dest='samples',
                           help='Test all the files for this sample', action='append')
    input_grp.add_argument('--file_of_samples',
                           required=False,
                           dest='fosn',
                           help='Path to a file of sample names')

    # Filters files by type
    filter_grp = parser.add_argument_group('FILTERS', 'Which files to exclude from the list')
    filter_grp.add_argument('--file_types',
                            choices=['bam', 'cram'],
                            default=['bam', 'cram'],
                            nargs='*',
                            required=False,
                            dest='file_types',
                            #action='append',
                            help='Options are: bam | cram, you can choose more than 1 param.')

    filter_grp.add_argument('--filter_npg_qc',
                            choices=["1", "0"],
                            required=False,
                            help='Filter based on npg qc field'
                            )

    filter_grp.add_argument('--filter_target',
                            choices=["1", "0"],
                            required=False,
                            help='This flag stopps the default filter on the target=1 irods metadata attribute'
    )

    # Tests
    tests_grp = parser.add_argument_group('TESTS', 'Choose which tests to run on your data')
    tests_grp.add_argument('--all-tests',
                           action='store_true',
                           help='Run all the tests that can be run'
    )

    tests_grp.add_argument('--test-sample',
                           choices=['irods_vs_seqsc', 'irods_vs_header', 'all'],
                           nargs='*',
                           #action='append',
                           #default='all',
                           default=[],
                           help='Run tests on samples - the options are: irods_vs_seqsc - '
                                'which checks the consistency of iRODS metadata against Sequencescape and '
                                'irods_vs_header - which checks the consistency of the header against the iRODS metadata'
    )

    tests_grp.add_argument('--test-library',
                            choices=['irods_vs_seqsc', 'irods_vs_header', 'all'],
                            #default='all',
                            nargs='*',
                            #action='append',
                            default=[],
                            help='Run tests on libraries - the options are: irods_vs_seqsc - '
                                 'which checks the consistency of iRODS metadata against Sequencescape and '
                                 'irods_vs_header - which checks the consistency of the header against the iRODS metadata'
    )

    tests_grp.add_argument('--test-study',
                           #dest='study_tests',
                           action='store_true',
                           help='Flag set if one wants to run the tests on study/studies metadata. '
                                'Only one test possible: irods_vs_seqsc, so nothing to choose, just set this flag or not'
    )

    tests_grp.add_argument('--test-reference',
                            dest='test_reference',
                            help='Check if the reference in iRODS metadata is the same as this one'
    )

    tests_grp.add_argument('--ref',
                            dest='desired_reference',
                            choices=[constants.HS37D5, constants.GRCH38, constants.G1K, constants.GRCH37],
                            help='The desired reference, given by name'

    )

    tests_grp.add_argument('--test-filename',
                            action='store_true',
                            help='This flag applies only for iRODS seq data. Check that the lanelet name '
                                 'is according to what is in the bam/cram header, under PU tag.'

    )

    tests_grp.add_argument('--test-md5',
                           action='store_true',
                           help='Set this flag for the MD5 of a file to be checked in iRODS metadata '
                                'as opposed to ichksum (the calculated MD5 at file submission time).'

    )

    tests_grp.add_argument('--test-complete-meta',
                           action='store_true',
                           help='Chose this test if you want the iRODS metadata to be checked that '
                                'it is complete against a config file you give in'
    )

    tests_grp.add_argument('--config_file',
                           dest='config_file',
                           help='The config file for the test regarding iRODS metadata being complete '
                                '(to be given with --all-tests and --test-complete-meta option)'
    )

    tests_grp.add_argument('--test_same_files_by_diff_study_ids',
                            help='This tests that the same set of files is obtained when querying by different '
                                 'study identifiers -- to be given by --study_internal_id and --study_acc_nr'
    )

    tests_grp.add_argument('--study_internal_id',
                           help='The internal_id of the study that you query by for getting a list of files'
                           )

    tests_grp.add_argument('--study_acc_nr',
                           help='The accession number of the study that you query by for getting a list of files'
                           )


    # OUTPUT: how to output the results?
    out = parser.add_argument_group('OUTPUT FORMAT', 'What output to return and how', )
    output_grp = out.add_mutually_exclusive_group(required=True)
    output_grp.add_argument('--output_as_json',
                            nargs='?',
                            dest='out_file',
                            #default='stdout',
                            required=False,
                            help='write the output as json')

    output_grp.add_argument('--output_as_report',
                            nargs='?',
                            dest='out_file',
                            #default='stdout',
                            required=False,
                            help='write the output as a text report')

    # ADDITIONALS:
    additional_outputs_grp = parser.add_argument_group('INCLUDE IN OUTPUT', 'What to include in the output')
    additional_outputs_grp.add_argument('--output_file_count', action='store_true')
    additional_outputs_grp.add_argument('--output_samples',
                                        nargs='?',
                                        dest='samples_file',
                                        required=False,
                                        help='Include in the output also a list of samples names '
                                             'as they appears in the tests requested'
    )
    additional_outputs_grp.add_argument('--output_only_bad_samples',
                                        nargs='?',
                                        dest='bad_samples_file',
                                        required=False,
                                        help='Include in the output also a list of samples names '
                                             'as they appears in the tests requested'
    )
    additional_outputs_grp.add_argument('--output_libraries',
                                        nargs='?',
                                        dest='libraries_file',
                                        required=False,
                                        help='Include in the output also a list of library names '
                                             'as they appear in the tests requested'
    )
    additional_outputs_grp.add_argument('--output_only_bad_libraries',
                                        nargs='?',
                                        dest='bad_libraries_file',
                                        required=False,
                                        help='Include in the output also a list of library names '
                                             'as they appear in the tests requested'
    )

    additional_outputs_grp.add_argument('--output_all_entities',
                                        nargs='?',
                                        dest='entities_file',
                                        required=False,
                                        help='Include a file containing all the entities (samples,libraries, studies) '
                                             'found in the tests ran'
    )
    additional_outputs_grp.add_argument('--output_only_bad_entities',
                                        nargs='?',
                                        dest='bad_entities_file',
                                        required=False,
                                        help='Include a file containing all the entities (samples,libraries, studies) '
                                             'found in the tests ran'
    )

    additional_outputs_grp.add_argument('--output_files_filtered_out',
                                        nargs='?',
                                        dest='filtered_out',
                                        required=False,
                                        help='Include all the files filtered out as a result of applying some fiters when querying for data'
                                        )

    additional_outputs_grp.add_argument('--include_tests_not_exec',
                                        action='store_true',
                                        required=False,
                                        help='Include in the output also a report containing '
                                             'the list of tests that havent been executed and the reasons')

    return parser.parse_args()

#print parse_args()

if __name__ == '__main__':
    print parse_args()

