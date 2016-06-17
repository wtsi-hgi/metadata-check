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
                           help='The desired reference, given by name',
    )

    tests_grp.add_argument('--test-complete-meta',
                           action='store_true',
                           help='Chose this test if you want the iRODS metadata to be checked that '
                                'it is complete against a config file you give in',
    )

    tests_grp.add_argument('--config_file',
                           dest='config_file',
                           help='The config file for the test regarding iRODS metadata being complete '
                                '(to be given with --all-tests and --test-complete-meta option)',
    )

    # OUTPUT: how to output the results?
    out = parent_parser.add_argument_group('OUTPUT FORMAT', 'What output to return and how', )
    output_grp = out.add_mutually_exclusive_group()  #(required=True)
    output_grp.add_argument('--output_as_json',
                            dest='json_output',
                            action='store_true',
                            required=False,
                            help='write the output as json',
    )

    output_grp.add_argument('--output_as_text',
                            action='store_true',
                            dest='text_output',
                            required=False,
                            help='write the output as a text report',
    )

    parent_parser.add_argument('--output_dir',
                            dest='output_dir',
                            required=True,
                            help='write the output to this directory',
    )


    # ADDITIONALS:
    additional_outputs_grp = parent_parser.add_argument_group('INCLUDE IN OUTPUT', 'What to include in the output')
    additional_outputs_grp.add_argument("-v", "--verbosity", action="count", help="increase output verbosity")
    additional_outputs_grp.add_argument('--dump_meta',
                                        dest='meta_dir',
                                        required=False,
                                        help='Dump all the metadata extracted to the directory given as parameter',
    )

    additional_outputs_grp.add_argument('--dump_fnames_by_type',
                                        required=False,
                                        dest='fnames_by_ftype',
                                        action='store_true',
                                        help='Output a list of files analyzed grouped by type to a file '
                                             '(by default if no param given - include in the report)',
    )

    subparsers = parser.add_subparsers(title='Strategies for fetching iRODS metadata: in batch, per file or given by the user as input',
                                       description='One subcommand required: fetch_by_path | fetch_by_metadata | given_by_user',
                                       help='Sub-commands',
                                       dest='metadata_fetching_strategy'
    )
    subparsers.required = True

    parser_filecheck = subparsers.add_parser('fetch_by_path', parents=[parent_parser],
                                             help='Fetch the metadata of a file by irods filepath')
    parser_filecheck.add_argument('fpaths_irods',
                                  nargs='+',
                                  help='List of file paths in iRODS'
    )

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
    input_grp.add_argument('--study_name', required=False, help='Study name', )
    input_grp.add_argument('--study_internal_id',
                           help='The internal_id of the study that you query by for getting a list of files',
    )

    input_grp.add_argument('--study_acc_nr',
                           help='The accession number of the study that you query by for getting a list of files',
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
                            help='Options are: bam | cram, you can choose more than 1 param.',
    )

    filter_grp.add_argument('--filter_npg_qc',
                            choices=["1", "0"],
                            required=False,
                            help='Filter based on npg qc field',
    )

    filter_grp.add_argument('--filter_target',
                            choices=["1", "0", "library"],
                            required=False,
                            help='This flag stopps the default filter on the target=1 irods metadata attribute',
    )


    return parser.parse_args()

#print parse_args()

if __name__ == '__main__':
    print(parse_args())

