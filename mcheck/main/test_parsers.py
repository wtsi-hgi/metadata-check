
import argparse



def parse_argsC():
    parser = argparse.ArgumentParser(description='ATAC and stuff', conflict_handler='resolve')

    parser.add_argument('--study', required=False, help='Study name')

    subparsers = parser.add_subparsers(title='subcommands', dest='subparser_name')

    parser_division = subparsers.add_parser('show-species', help='show all species in a division', parents=[parser], conflict_handler='resolve')
    parser_division.add_argument('--division', help='division for which species will be listed', choices=['a', 'b'])

    parser_species = subparsers.add_parser('show-dbs',
                                           help='show databases with distinct assembly versions for a species')
    parser_species.add_argument('species', help='species for which assembly-distinct databases will be listed')

    parser_test = argparse.ArgumentParser(add_help=False)
    parser_test.add_argument('--test', action='store_true',
                             help='save mappings in "...core_x_y_z_atactest" (must exist) instead of "...core_x_y_z"')

    parser_map_h = subparsers.add_parser('map-historic', parents=[parser_test],
                                         help='create mappings from all "old" db versions to the latest on db on mirror')
    parser_map_h.add_argument('server', help='database server in which to store the mappings')
    parser_map_h.add_argument('species', help='species for which mappings will be created')

    parser.parse_args()

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
                           action='append',
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
    filter_grp.add_argument('--file_type',
                            choices=['bam', 'cram'],
                            default=['bam', 'cram'],
                            nargs='*',
                            required=False,
                            dest='file_types',
                            action='append',
                            help='Options are: bam | cram, you can choose more than 1 param.')


    # Tests
    tests_grp = parser.add_argument_group('TESTS', 'Choose which tests to run on your data')
    tests_grp.add_argument('--test-all',
                           action='store_true',
                           help='Run all the tests that can be run'
    )

    tests_grp.add_argument('--sample-tests',
                           dest='sample_tests',
                           choices=['irods_vs_seqsc', 'irods_vs_header', 'all'],
                           nargs='*',
                           action='append',
                           default=['all'],
                           help='Run tests on samples - the options are: irods_vs_seqsc - '
                                'which checks the consistency of iRODS metadata against Sequencescape and '
                                'irods_vs_header - which checks the consistency of the header against the iRODS metadata'
    )

    tests_grp.add_argument('--library-tests',
                            dest='lib_tests',
                            choices=['irods_vs_seqsc', 'irods_vs_header', 'all'],
                            nargs='*',
                            action='append',
                            help='Run tests on libraries - the options are: irods_vs_seqsc - '
                                 'which checks the consistency of iRODS metadata against Sequencescape and '
                                 'irods_vs_header - which checks the consistency of the header against the iRODS metadata'
    )

    tests_grp.add_argument('--study-tests',
                           dest='study_tests',
                           action='store_true',
                           help='Flag set if one wants to run the tests on study/studies metadata. '
                                'Only one test possible: irods_vs_seqsc, so nothing to choose, just set this flag or not'
    )

    tests_grp.add_argument('--reference-test',
                            dest='reference',
                            choices=['hs37d5', 'GRCh37', 'human_g1k_v37'],
                            help='Check if the reference in iRODS metadata is the same as this one'
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
                           dest='config_file',
                           help='Chose this test if you want the iRODS metadata to be checked that '
                                'it is complete against a config file you give in'
    )

    # OUTPUT: how to output the results?
    out = parser.add_argument_group('OUTPUT', 'What output to return and how', )
    output_grp = out.add_mutually_exclusive_group(required=True)
    output_grp.add_argument('--output_as_json',
                            nargs='?',
                            dest='out_file',
                            default='stdout',
                            required=False,
                            help='write the output as json')

    output_grp.add_argument('--output_as_report',
                            nargs='?',
                            dest='out_file',
                            default='stdout',
                            required=False,
                            help='write the output as a text report')

    # ADDITIONALS:
    additional_outputs_grp = parser.add_argument_group('INCLUDE IN OUTPUT', 'What to include in the output')
    additional_outputs_grp.add_argument('--output_nr_samples', action='store_true')
    additional_outputs_grp.add_argument('--output_file_count', action='store_true')
    additional_outputs_grp.add_argument('--output_problematic_entities')

    additional_outputs_grp.add_argument('--include_not_exec', action='store_true', required=False,
                             help='include also the tests that havent been executed and the reasons')

    return parser.parse_args()

def parse_args1():

    # INPUT: What files?
    #parser.add_argument()
    input_parser = argparse.ArgumentParser(conflict_handler='resolve')
    input_grp = input_parser.add_argument_group('INPUT', 'Different ways of getting the list of files to check')
    input_grp.add_argument('--study', required=False, help='Study name')
    input_grp.add_argument('--fpath_irods', required=False, dest='files', help='List of file paths in iRODS', action='append')
    input_grp.add_argument('--fofn', required=False,
                        help='The path to a fofn containing file paths from iRODS '
                             'for the files one wants to run tests on')
    input_grp.add_argument('--sample', required=False, dest='samples', help='Test all the files for this sample', action='append')
    input_grp.add_argument('--file_of_samples', required=False, dest='fosn', help='path to a file of sample names')


    parser = argparse.ArgumentParser(prog='Metadata Checks', conflict_handler='resolve', parents=[input_parser])


    # Filters files by type
    filter_grp = parser.add_argument_group('FILTERS', 'Which files to exclude from the list')
    filter_grp.add_argument('--file_type', choices=['bam', 'cram'], required=False, dest='file_types', action='append',
                        help='Options are: bam | cram, you can choose more than 1 param.')


    # SUBPARSERS - per TEST TYPE:
#   test_sample_parser = argparse.ArgumentParser(parents=[parser])
    subparsers = parser.add_subparsers(title='TESTS as subcommands', #dest='subparsers',
                                       description='Choose the subcommands corresponding to the set of tests to be executed')
    #subparsers.required = True

    parser_samples = subparsers.add_parser('test_samples', parents=[input_parser], help='Run tests on samples', conflict_handler='resolve') # parents=[parser],
    parser_samples.add_argument('--irods_vs_seqsc', action='store_true', required=False,
                                help='Add this flag if you want the samples to be checked for iRODS metadata consistency vs Sequencescape')
    #parser_samples.set_defaults(func='test_samples')

    parser_libs = subparsers.add_parser('test_libs', help='Run tests on libraries') #parents=[parser],
    parser_libs.add_argument('--irods_vs_seqsc', action='store_true', required=False,
                             help='Add this flag if you want the libraries to be checked for iRODS metadata consistency vs. Seqscuncescape')

    # OUTPUT: how to output the results?
    output_grp = parser.add_argument_group('OUTPUT', 'What output to return and how')
    output_grp.add_argument('--output_as_json', action='store_true', required=False, help='write the output as json')
    return parser.parse_args()


# >>> parser = argparse.ArgumentParser(prog='PROG')
# >>> parser.add_argument('--foo', action='store_true', help='foo help')
# >>> subparsers = parser.add_subparsers(help='sub-command help')
# >>>
# >>> # create the parser for the "a" command
# >>> parser_a = subparsers.add_parser('a', help='a help')
# >>> parser_a.add_argument('bar', type=int, help='bar help')
# >>>
# >>> # create the parser for the "b" command
# >>> parser_b = subparsers.add_parser('b', help='b help')
# >>> parser_b.add_argument('--baz', choices='XYZ', help='baz help')




def test_samples():
    print("HEllo from test_samples!")




# >>> parser = argparse.ArgumentParser(prog='PROG', add_help=False)
# >>> group1 = parser.add_argument_group('group1', 'group1 description')
# >>> group1.add_argument('foo', help='foo help')
# >>> group2 = parser.add_argument_group('group2', 'group2 description')
# >>> group2.add_argument('--bar', help='bar help')
# >>> parser.print_help()

#  parent_parser = argparse.ArgumentParser(add_help=False)
# >>> parent_parser.add_argument('--parent', type=int)
#
# >>> foo_parser = argparse.ArgumentParser(parents=[parent_parser])
# >>> foo_parser.add_argument('foo')
# >>> foo_parser.parse_args(['--parent', '2', 'XXX'])
# Namespace(foo='XXX', parent=2)


args = parse_args()
print(str(args))


