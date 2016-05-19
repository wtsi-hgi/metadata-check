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
# from . import constants
# import argcomplete
from mcheck.main import constants


def parse_args():
    parser = argparse.ArgumentParser(prog='metadata_checks', conflict_handler='resolve')#, usage='%(prog)s {fetch_by_path | fetch_by_metadata}') # usage='%(prog)s subcommands [options]',

    # Tests
    parent_parser = argparse.ArgumentParser(add_help=False)
    tests_grp = parent_parser.add_argument_group('TESTS', 'Choose which tests to run on your data')
    tests_grp.add_argument('--test-for-reference',
                           dest='desired_reference',
                           choices=[constants.HS37D5, constants.GRCH38, constants.G1K, constants.GRCH37],
                           help='The desired reference, given by name'

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

    # tests_grp.add_argument('--test_same_files_by_diff_study_ids',
    #                        action='store_true',
    #                         help='This tests that the same set of files is obtained when querying by different '
    #                              'study identifiers -- to be given by --study_internal_id and --study_acc_nr. '
    #                              'Works only when the data is given by study name.'
    # )

    # OUTPUT: how to output the results?
    out = parent_parser.add_argument_group('OUTPUT FORMAT', 'What output to return and how', )
    output_grp = out.add_mutually_exclusive_group()  #(required=True)
    output_grp.add_argument('--output_as_json',
                            dest='json_output',
                            action='store_true',
                            required=False,
                            help='write the output as json')

    output_grp.add_argument('--output_as_text',
                            action='store_true',
                            dest='text_output',
                            required=False,
                            help='write the output as a text report')

    parent_parser.add_argument('--output_dir',
                            dest='output_dir',
                            required=True,
                            help='write the output to this directory')


    # ADDITIONALS:
    additional_outputs_grp = parent_parser.add_argument_group('INCLUDE IN OUTPUT', 'What to include in the output')
    additional_outputs_grp.add_argument("-v", "--verbosity", action="count", help="increase output verbosity")
    additional_outputs_grp.add_argument('--dump_meta',
                                        dest='meta_dir',
                                        required=False,
                                        help='Dump all the metadata extracted to the directory given as parameter'
    )

    additional_outputs_grp.add_argument('--dump_fnames_by_type',
                                        required=False,
                                        dest='fnames_by_ftype',
                                        action='store_true',
                                        help='Output a list of files analyzed grouped by type to a file '
                                             '(by default if no param given - include in the report)'
    )

    subparsers = parser.add_subparsers(title='Fetch metadata in batch or per file', description='One subcommand required: fetch_by_path | fetch_by_metadata', help='Sub-commands',
                                       dest='metadata_fetching_strategy')#, prog='You need to choose a metadata fetching strategy - choices: fetch_by_path or fetch_by_metadata')    # , metavar={'fetch_by_path', 'fetch_by_metadata'})
    subparsers.required = True

    parser_filecheck = subparsers.add_parser('fetch_by_path', parents=[parent_parser],
                                             help='Fetch the metadata of a file by irods filepath')
    parser_filecheck.add_argument('fpaths_irods',
                                  nargs='+',
                                  help='List of file paths in iRODS')

    parser_all_files_metacheck = subparsers.add_parser('fetch_by_metadata', parents=[parent_parser],
                                                       help='Fetch the files matching the meta query')
    parser_all_files_metacheck.add_argument('--irods_zone',
                                            help='The irods zone where the data is found',
                                            choices=['seq', 'humgen', 'Sanger1'],
                                            required=True
    )

    input = parser_all_files_metacheck.add_argument_group('INPUT',
                                                          'Choose one or more ways of getting the list of files to check'
    )
    input_grp = input.add_mutually_exclusive_group(required=True)
    input_grp.add_argument('--study_name', required=False, help='Study name')
    input_grp.add_argument('--study_internal_id',
                           help='The internal_id of the study that you query by for getting a list of files'
    )

    input_grp.add_argument('--study_acc_nr',
                           help='The accession number of the study that you query by for getting a list of files'
    )

    # Filters files by type
    filter_grp = parser_all_files_metacheck.add_argument_group('FILTERS', 'Which files to include based on metadata filters')
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
                            choices=["1", "0", "library"],
                            required=False,
                            help='This flag stopps the default filter on the target=1 irods metadata attribute'
    )

    #
    # additional_outputs_grp.add_argument('--output_header_sample_ids',
    #                                     #nargs='?',
    #                                     #default='samples.header.ids', - for some reason doesn't work
    #                                     dest='header_sample_ids_file',
    #                                     action='store_true',
    #                                     required=False,
    #                                     help='Include in the output also a list of sample ega accession numbers '
    #                                          'as they appears in the tests requested'
    # )

    # additional_outputs_grp.add_argument('--aaaaafile_types2',
    #                         choices=['bam', 'cram'],
    #                         default=['bam', 'cram'],
    #                         nargs='*',
    #                         required=False,
    #                         dest='file_types',
    #                         #action='append',
    #                         help='Options are: bam | cram, you can choose more than 1 param.')


    # additional_outputs_grp.add_argument('--output_samples_by_ega_id',
    #                                     #nargs='?',
    #                                     action='store_true',
    #                                     dest='sample_ega_out_file',
    #                                     required=False,
    #                                     help='Include in the output also a list of sample ega accession numbers '
    #                                          'as they appears in the tests requested'
    # )
    # additional_outputs_grp.add_argument('--output_samples_by_name',
    #                                     #nargs='?',
    #                                     action='store_true',
    #                                     dest='sample_names_out_file',
    #                                     required=False,
    #                                     help='Include in the output also a list of samples names '
    #                                          'as they appears in the tests requested'
    # )
    # additional_outputs_grp.add_argument('--output_only_bad_samples_by_ega_id',
    #                                     #nargs='?',
    #                                     action='store_true',
    #                                     dest='bad_sample_egaids_out_file',
    #                                     required=False,
    #                                     help='Include in the output also a list of samples names '
    #                                          'as they appears in the tests requested'
    # )
    # additional_outputs_grp.add_argument('--output_only_bad_samples_by_name',
    #                                     #nargs='?',
    #                                     action='store_true',
    #                                     dest='bad_sample_names_out_file',
    #                                     required=False,
    #                                     help='Include in the output also a list of samples names '
    #                                          'as they appears in the tests requested'
    # )

    # additional_outputs_grp.add_argument('--output_libraries_by_name',
    #                                     #nargs='?',
    #                                     action='store_true',
    #                                     dest='library_names_out_file',
    #                                     required=False,
    #                                     help='Include in the output also a list of library names '
    #                                          'as they appear in the tests requested'
    # )
    #
    # additional_outputs_grp.add_argument('--output_libraries_by_id',
    #                                     #nargs='?',
    #                                     action='store_true',
    #                                     dest='library_ids_out_file',
    #                                     required=False,
    #                                     help='Include in the output also a list of library internal ids '
    #                                          'as they appear in the tests requested'
    # )
    #
    # additional_outputs_grp.add_argument('--output_header_libraries',
    #                                     #nargs='?',
    #                                     action='store_true',
    #                                     dest='header_library_ids_file',
    #                                     required=False,
    #                                     help='Include in the output also a list of library names '
    #                                          'as they appear in the tests requested'
    # )

    # additional_outputs_grp.add_argument('--output_only_bad_libraries_by_name',
    #                                     #nargs='?',
    #                                     action='store_true',
    #                                     dest='bad_library_names_out_file',
    #                                     required=False,
    #                                     help='Include in the output also a list of problematic libraries by names '
    #                                          'as they appear in the tests requested'
    # )
    #
    # additional_outputs_grp.add_argument('--output_only_bad_libraries_by_id',
    #                                     #nargs='?',
    #                                     action='store_true',
    #                                     dest='bad_library_ids_out_file',
    #                                     required=False,
    #                                     help='Include in the output a list of problematic libraries by id '
    #                                          'as they appear in the tests requested'
    # )
    #
    # additional_outputs_grp.add_argument('--output_studies_by_ega_id',
    #                                     #nargs='?',
    #                                     action='store_true',
    #                                     dest='study_egaids_out_file',
    #                                     required=False,
    #                                     help='Include in the output also a list of study names '
    #                                          'as they appear in the tests requested'
    # )
    #
    # additional_outputs_grp.add_argument('--output_studies_by_name',
    #                                     #nargs='?',
    #                                     action='store_true',
    #                                     dest='study_names_out_file',
    #                                     required=False,
    #                                     help='Include in the output also a list of study names '
    #                                          'as they appear in the tests requested'
    # )
    #
    # additional_outputs_grp.add_argument('--output_all_entities_to_dir',
    #                                     #nargs='?',
    #                                     #action='store_true',
    #                                     dest='entities_out_dir',
    #                                     required=False,
    #                                     help='Output all the entities found to individual files '
    #                                          '(1 file per type of entity (e.g. sample,library) per type of id)'
    # )
    #
    # additional_outputs_grp.add_argument('--output_all_entities_to_file',
    #                                     #nargs='?',
    #                                     action='store_true',
    #                                     dest='entities_out_file',
    #                                     required=False,
    #                                     help='Output all the entities found to a file'
    # )

    # additional_outputs_grp.add_argument('--output_only_bad_entities',
    #                                     nargs='?',
    #                                     dest='bad_entities_out_file',
    #                                     required=False,
    #                                     help='Include a file containing all the entities (samples,libraries, studies) '
    #                                          'found in the tests ran'
    # )

    # additional_outputs_grp.add_argument('--output_files_filtered_out',
    #                                     nargs='?',
    #                                     dest='files_filtered_out',
    #                                     required=False,
    #                                     help='Include all the files filtered out as a result of applying some fiters when querying for data'
    #                                     )

    # additional_outputs_grp.add_argument('--include_tests_not_exec',
    #                                     action='store_true',
    #                                     required=False,
    #                                     help='Include in the output also a report containing '
    #                                          'the list of tests that havent been executed and the reasons')
    #
    # #argcomplete.autocomplete(parser)



    # input_grp.add_argument('--fofn',
    #                        required=False,
    #                        help='The path to a fofn containing file paths from iRODS '
    #                          'for the files one wants to run tests on')
    # input_grp.add_argument('--sample_names',
    #                        required=False,
    #                        nargs='*',
    #                        dest='sample_names',
    #                        help='Test all the files for this sample', action='append')
    # input_grp.add_argument('--file_of_samples',
    #                        required=False,
    #                        dest='fosn',
    #                        help='Path to a file of sample names')

    # additional_outputs_grp.add_argument('--output_file_count', action='store_true')
    # additional_outputs_grp.add_argument('--output_problematic_files',
    #                                     dest='fofn_probl',
    #                                     required=False,
    #                                     help='Write the list of files with problems to this file')
    #

    #
    # tests_grp.add_argument('--test-sample',
    #                        choices=['irods_vs_seqsc', 'irods_vs_header', 'all'],
    #                        nargs='*',
    #                        #action='append',
    #                        #default='all',
    #                        default=[],
    #                        help='Run tests on samples - the options are: irods_vs_seqsc - '
    #                             'which checks the consistency of iRODS metadata against Sequencescape and '
    #                             'irods_vs_header - which checks the consistency of the header against the iRODS metadata'
    # )
    #
    # tests_grp.add_argument('--test-library',
    #                         choices=['irods_vs_seqsc', 'irods_vs_header', 'all'],
    #                         #default='all',
    #                         nargs='*',
    #                         #action='append',
    #                         default=[],
    #                         help='Run tests on libraries - the options are: irods_vs_seqsc - '
    #                              'which checks the consistency of iRODS metadata against Sequencescape and '
    #                              'irods_vs_header - which checks the consistency of the header against the iRODS metadata'
    # )
    #
    # tests_grp.add_argument('--test-study',
    #                        #dest='study_tests',
    #                        action='store_true',
    #                        help='Flag set if one wants to run the tests on study/studies metadata. '
    #                             'Only one test possible: irods_vs_seqsc, so nothing to choose, just set this flag or not'
    # )


    # tests_grp.add_argument('--test-md5',
    #                        action='store_true',
    #                        help='Set this flag for the MD5 of a file to be checked in iRODS metadata '
    #                             'as opposed to ichksum (the calculated MD5 at file submission time).'
    #
    # )




    return parser.parse_args()

#print parse_args()

if __name__ == '__main__':
    print(parse_args())

