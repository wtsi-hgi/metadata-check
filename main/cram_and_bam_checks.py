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
import arg_parser
import metadata_utils
#from main import irods_seq_data_tests as seq_tests
import irods_metadata_consistency_checks as seq_consistency_checks
import error_types
import complete_irods_metadata_checks
import irods_metadata_consistency_checks as irods_checks
import irods_metadata as irods_meta_module
import header_metadata as header_meta_module
#from ... import config
import config

CRAM_FILE_TYPE = 'cram'
BAM_FILE_TYPE = 'bam'
BOTH_FILE_TYPES = 'both'


def check_irods_vs_header_metadata(irods_path, header_dict, irods_dict, entity_type):
    """
        where: (e.g.)
         irods_dict = dict('name': [sample_name], accession_number: [samples_acc_nr], internal_id: [internal_id])
         header_dict = dict('name': [sample_name], accession_number: [samples_acc_nr], internal_id: [internal_id])
    """
    problems = []
    for id_type, head_ids_list in header_dict.iteritems():
        if irods_dict.get(id_type) and header_dict.get(id_type):
            if set(head_ids_list).difference(set(irods_dict[id_type])):
                problems.append(error_types.HeaderVsIrodsMetadataAttributeError(fpath=irods_path, attribute=id_type,
                                                                      header_value=str(head_ids_list),
                                                                      irods_value=irods_dict[id_type],
                                                                      entity_type=entity_type))
    return problems



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
        irods_samples = metadata_utils.iRODSUtils.extract_samples_from_irods_metadata(irods_metadata)

        if samples_irods_vs_header:
            header_samples = metadata_utils.HeaderUtils.sort_entities_by_guessing_id_type(header_metadata.samples)
            try:
                check_irods_vs_header_metadata(irods_fpath, header_samples, irods_samples, 'sample')
            except error_types.HeaderVsIrodsMetadataAttributeError as e:
                issues.append(str(e))

        if samples_irods_vs_seqscape:
            problems = irods_checks.compare_entity_sets_in_seqsc(irods_samples, 'sample')
            issues.extend(problems)


    # LIBRARY TESTS:
    if libraries_irods_vs_header or libraries_irods_vs_seqscape:
        irods_libraries = metadata_utils.iRODSUtils.extract_libraries_from_irods_metadata(irods_metadata)

        if libraries_irods_vs_header:
            header_libraries = metadata_utils.HeaderUtils.sort_entities_by_guessing_id_type(header_metadata.libraries)

            try:
                check_irods_vs_header_metadata(irods_fpath, header_libraries, irods_libraries, 'library')
            except error_types.HeaderVsIrodsMetadataAttributeError as e:
                issues.append(str(e))

        if libraries_irods_vs_seqscape:
            problems = irods_checks.compare_entity_sets_in_seqsc(irods_libraries, 'library')
            issues.extend(problems)


    # STUDY TESTS:
    if study_irods_vs_seqscape:
        irods_studies = metadata_utils.iRODSUtils.extract_studies_from_irods_metadata(irods_metadata)

        # Compare IRODS vs. SEQSCAPE:
        problems = irods_checks.compare_entity_sets_in_seqsc(irods_studies, 'study')
        issues.extend(problems)


    # OTHER TESTS:
    if collateral_tests:
        collateral_issues = seq_tests.run_irods_seq_specific_tests(irods_fpath, irods_metadata, header_metadata, desired_ref)
        if collateral_issues:
            issues.extend(collateral_issues)
            #print "IRODS SEQUENCING SPECIFIC TESTS - ISSUES: " + str(collateral_issues)
    

    if not issues:
        print "OK"
    else:
        print issues





def parse_args():
    parser = argparse.ArgumentParser()

    # INPUT: What files?
    #parser.add_argument()
    parser.add_argument('--study', required=False, help='Study name')
    parser.add_argument('--fpath_irods', required=False, dest='files', help='List of file paths in iRODS', action='append')
    parser.add_argument('--fofn', required=False,
                        help='The path to a fofn containing file paths from iRODS '
                             'for the files one wants to run tests on')
    parser.add_argument('--sample', required=False, dest='samples', help='Test all the data for this sample', action='append')

    # Filters files by type
    parser.add_argument('--file_type', choices=['bam', 'cram'], required=False, dest='file_types', action='append',
                        help='Options are: bam | cram, you can choose more than 1 param.')


    # SUBPARSERS - per TEST TYPE:
    test_sample_parser = argparse.ArgumentParser(parents=[parser])


    # OUTPUT: how to output the results?



#  parent_parser = argparse.ArgumentParser(add_help=False)
# >>> parent_parser.add_argument('--parent', type=int)
#
# >>> foo_parser = argparse.ArgumentParser(parents=[parent_parser])
# >>> foo_parser.add_argument('foo')
# >>> foo_parser.parse_args(['--parent', '2', 'XXX'])
# Namespace(foo='XXX', parent=2)


def parse_args2():
    parser = argparse.ArgumentParser()
    # Getting the input (filepaths, etc..)
    parser.add_argument('--study', required=False, help='Study name')
    parser.add_argument('--file_type', required=False, default=BOTH_FILE_TYPES, help='Options are: bam | cram | both. If you choose any, then it checks both - whatever it finds.')
    parser.add_argument('--fpaths_irods', required=False, help='List of file paths in iRODS')
    parser.add_argument('--fofn', required=False,
                        help='The path to a fofn containing file paths from iRODS '
                             'for the files one wants to run tests on')

    # Getting the list of tests to be done:
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
    parser.add_argument('--collateral_tests', required=False, default=True,
                        help='This is a test suite consisting of checks specific for sequencing data released by NPG, '
                             'such as md5, lane id, run id')
    parser.add_argument('--check_irods_meta_against_config', required=False,
                        help='This option takes also the path to a config file, to check the irods metadata of each file'
                             ' against the structure given as config file. The conf file should contain: '
                             '{field_name: expected_frequency,..} ')

    # Outputting the report:
    # TODO


    args = parser.parse_args()

    return args


# def check_args(args):
#     if not args.fpaths_irods and not args.study:
#         #parser.print_help()
#         #print "No study provided, no BAM path given => NOTHING TO DO! EXITTING"
#         #exit(0)
#         raise ValueError("No study provided, no BAM path given => NOTHING TO DO! EXITTING")
#     if not args.samples_irods_vs_header and not args.samples_irods_vs_seqscape \
#             and not args.libraries_irods_vs_header \
#             and not args.libraries_irods_vs_seqscape \
#             and not args.study_irods_vs_seqscape\
#             and not args.desired_ref\
#             and not args.collateral_tests\
#             and not args.check_irods_meta_against_config:
#         raise ValueError("You haven't selected neither samples to be checked, nor libraries, nor study. " \
#               "Nothing to be done!")
#         # parser.print_help()
#         # exit(0)


def read_fofn_into_list(fofn_path):
    fofn_fd = open(fofn_path)
    files_list = [f.strip() for f in fofn_fd]
    fofn_fd.close()
    return files_list


def write_list_to_file(input_list, output_file):
    out_fd = open(output_file, 'w')
    for entry in input_list:
        out_fd.write(entry+'\n')
    out_fd.close()


# def collect_fpaths_for_study(study, file_type=BOTH_FILE_TYPES):
#     fpaths_irods = []
#     if file_type == CRAM_FILE_TYPE:
#         fpaths_irods = metadata_utils.iRODSUtils.retrieve_list_of_crams_by_study_from_irods(study)
#         #print "NUMBER of CRAMs found: " + str(len(fpaths_irods))
#         #write_list_to_file(fpaths_irods, 'hiv-crams.out')
#     elif file_type == BAM_FILE_TYPE:
#         fpaths_irods = metadata_utils.iRODSUtils.retrieve_list_of_bams_by_study_from_irods(study)
#         #print "NUMBER of BAMs found: " + str(len(fpaths_irods))
#         #write_list_to_file(fpaths_irods, 'hiv-bams.out')
#     elif file_type == BOTH_FILE_TYPES:
#         bams_fpaths_irods = metadata_utils.iRODSUtils.retrieve_list_of_bams_by_study_from_irods(study)
#         crams_fpaths_irods = metadata_utils.iRODSUtils.retrieve_list_of_crams_by_study_from_irods(study)
#         fpaths_irods = bams_fpaths_irods + crams_fpaths_irods
#         print "NUMBER of BAMs found: " + str(len(bams_fpaths_irods))
#         print "NUMBER of CRAMs found: " + str(len(crams_fpaths_irods))
#         print "BAMS: " + str(bams_fpaths_irods)
#         print "CRAMs: " + str(crams_fpaths_irods)
#     return fpaths_irods

def collect_fpaths_by_study_name(study_name):
    return metadata_utils.iRODSUtils.retrieve_list_of_files_by_metadata('study', study_name)

def collect_fpaths_by_study_accession_nr(study_acc_nr):
    return metadata_utils.iRODSUtils.retrieve_list_of_files_by_metadata('study_accession_number', study_acc_nr)

def collect_fpaths_by_study_internal_id(study_id):
    return metadata_utils.iRODSUtils.retrieve_list_of_files_by_metadata('study_id', study_id)

def check_same_files_by_diff_study_ids(name, internal_id, acc_nr):
    files_by_name = set(collect_fpaths_by_study_name(str(name)))
    files_by_acc_nr = set(collect_fpaths_by_study_accession_nr(str(acc_nr)))
    files_by_id = set(collect_fpaths_by_study_internal_id(str(internal_id)))

    problems = []
    if files_by_name != files_by_acc_nr:
        diffs = files_by_name.difference(files_by_acc_nr)
        if diffs:
            problems.append(error_types.DifferentFilesRetrievedByDiffStudyIdsOfSameStudy(diffs, 'name', 'accession_number'))

        diffs = files_by_acc_nr.difference(files_by_name)
        if diffs:
            problems.append(error_types.DifferentFilesRetrievedByDiffStudyIdsOfSameStudy(diffs, 'accession_number', 'name'))

    if files_by_name != files_by_id:
        diffs = files_by_name.difference(files_by_id)
        if diffs:
            problems.append(error_types.DifferentFilesRetrievedByDiffStudyIdsOfSameStudy(diffs, 'name', 'internal_id'))

        diffs = files_by_id.difference(files_by_name)
        if diffs:
            problems.append(error_types.DifferentFilesRetrievedByDiffStudyIdsOfSameStudy(diffs, 'internal_id', 'name'))

    if files_by_acc_nr != files_by_id:
        diffs = files_by_id.difference(files_by_acc_nr)
        if diffs:
            problems.append(error_types.DifferentFilesRetrievedByDiffStudyIdsOfSameStudy(diffs, 'internal_id', 'accession_number'))

        diffs = files_by_acc_nr.difference(files_by_id)
        if diffs:
            problems.append(error_types.DifferentFilesRetrievedByDiffStudyIdsOfSameStudy(diffs, 'accession_number', 'internal_id'))
    return problems


def collect_fpaths_from_args(study=None, file_type=BOTH_FILE_TYPES, files_list=None, fofn_path=None):
    if study:
        fpaths_irods = collect_fpaths_by_study_name(study, file_type)
    elif fofn_path:
        fpaths_irods = read_fofn_into_list(fofn_path)
    elif files_list:
        fpaths_irods = files_list
    return fpaths_irods

def collect_fpaths_for_samples(samples):
    pass

def filter_by_file_type(fpaths, file_type):
    return [f for f in fpaths if f.endswith(file_type)]

def filter_by_avu(fpath, avu_attribute, avu_value):
    pass# manual_qc,...

def main():
    args = arg_parser.parse_args()

    # COLLECT FILE PATHS:
    fpaths_per_type = {} # type : [ fpath ]
    if args.study:
    #     if BAM_FILE_TYPE in args.file_types:
    #         fpaths_per_type[BAM_FILE_TYPE] = metadata_utils.iRODSUtils.retrieve_list_of_bams_by_study_from_irods(args.study)
    #     if CRAM_FILE_TYPE in args.file_types:
    #         fpaths_per_type[CRAM_FILE_TYPE] = metadata_utils.iRODSUtils.retrieve_list_of_crams_by_study_from_irods(args.study)
    # fpaths = fpaths_per_type.get(BAM_FILE_TYPE) + fpaths_per_type.get(CRAM_FILE_TYPE)

        #fpaths = metadata_utils.retrieve_list_of_files_by_study(args.study)
        fpaths = collect_fpaths_by_study_name(args.study)



    if args.fofn:
        files_from_fofn = read_fofn_into_list(args.fofn)
        fpaths = files_from_fofn

    if args.files:
        fpaths = args.files

    # per samples:
    if args.fosn:
        samples = read_fofn_into_list(args.fosn)
        # query irods for samples, get a list of files

    if args.samples:
        samples = args.samples
        # query irods per sample for files
        pass

    # Check for conflicts in the params?
    # TODO

    ##################### FILTER FILES ################################
    ## Filter by file type ###
    filtered_fpaths = []
    for file_type in args.file_types:
        filtered_fpaths.extend(filter_by_file_type(fpaths, file_type))


    print "ARGS = " + str(args)

    ########################## TESTS #####################
    # PREPARING FOR THE TESTS
    general_problems = []
    if args.test_same_files_by_diff_study_ids or args.all_tests:
        if args.study_internal_id and args.study_acc_nr and args.study:
            issues = check_same_files_by_diff_study_ids(args.study, args.study_internal_id, args.study_acc_nr)
            general_problems.extend(issues)
    print "Ran check on the list of files retrieved by each study identifier -- result is: " + str(general_problems)

    for f in filtered_fpaths:
        problems = []
        if args.config_file:
            pass


        # Deciding what tests to run
        header_tests = False
        irods_tests = False
        if args.all_tests:
            header_tests = True
            irods_tests = True
        else:
            if args.test_sample:
                if 'all' in args.test_sample or 'irods_vs_header' in args.test_sample:
                    header_tests = True
            if args.test_library:
                if 'irods_vs_header' in args.test_library or 'all' in args.test_library:
                    header_tests = True
            if any([args.test_sample, args.test_library, args.test_study, args.test_reference, args.test_md5, args.test_filename, args.all_tests, args.config_file]):
                irods_tests = True


        # Retrieve the resources as needed in preparation for the tests:
        h_meta = None
        if header_tests:
            try:
                header = metadata_utils.HeaderUtils.get_parsed_header_from_irods_file(f)
            except IOError as e:
                problems.append(str(e))
                continue
            else:
                h_meta = header_meta_module.HeaderSAMFileMetadata.from_header_to_metadata(header, f)


        if irods_tests:
            irods_avus = metadata_utils.iRODSUtils.retrieve_irods_avus(f)
            avu_issues = irods_meta_module.IrodsSeqFileMetadata.run_avu_count_checks(f, irods_avus)
            problems.extend(avu_issues)

            i_meta = irods_meta_module.IrodsSeqFileMetadata.from_avus_to_irods_metadata(irods_avus, f)
            sanity_issues = i_meta.run_field_sanity_checks()
            problems.extend(sanity_issues)

            ## Filter by manual_qc:
            if not args.filter_npg_qc is None:
                if args.filter_npg_qc != i_meta.npg_qc:
                    continue


            ####### RUN THE TESTS: #########
            # MD5 tests:
            if args.test_md5 or args.all_tests:
                try:
                    i_meta.test_md5_calculated_vs_metadata()
                except (error_types.WrongMD5Error, error_types.TestImpossibleToRunError) as e:
                    problems.append(str(e))

            # TODO - not working properly
            if args.test_reference or args.all_tests:
                try:
                    i_meta.test_reference(args.desired_reference)
                except (error_types.WrongReferenceError, error_types.TestImpossibleToRunError) as e:
                    problems.append(str(e))

            if args.test_filename or args.all_tests:
                try:
                    i_meta.test_lane_from_fname_vs_metadata()
                except (error_types.IrodsMetadataAttributeVsFileNameError, error_types.TestImpossibleToRunError) as e:
                    problems.append(str(e))

                try:
                    i_meta.test_run_id_from_fname_vs_metadata()
                except (error_types.IrodsMetadataAttributeVsFileNameError, error_types.TestImpossibleToRunError) as e:
                    problems.append(str(e))

                # TODO : test also the tag

            if args.test_sample or args.all_tests:
                if 'all' in args.test_sample or args.all_tests:
                    issues = check_irods_vs_header_metadata(f, h_meta.samples, i_meta.samples, 'sample')
                    problems.extend(issues)

                    issues = seq_consistency_checks.compare_entity_sets_in_seqsc(i_meta.samples, 'sample')    #def compare_entity_sets_in_seqsc(entities_dict, entity_type):
                    problems.extend(issues)

                    issues = seq_consistency_checks.check_sample_is_in_desired_study(i_meta.samples['internal_id'], i_meta.studies['name'])
                    problems.extend(issues)
                else:
                    if 'irods_vs_header' in args.test_sample:
                        issues = check_irods_vs_header_metadata(f, h_meta.samples, i_meta.samples, 'sample')
                        problems.extend(issues)

                    if 'irods_vs_seqsc' in args.test_sample:
                        issues = seq_consistency_checks.compare_entity_sets_in_seqsc(i_meta.samples, 'sample')    #def compare_entity_sets_in_seqsc(entities_dict, entity_type):
                        problems.extend(issues)

                        issues = seq_consistency_checks.check_sample_is_in_desired_study(i_meta.samples['internal_id'], i_meta.studies['name'])
                        problems.extend(issues)

            if args.test_library or args.all_tests:
                if args.all_tests or 'all' in args.test_library:
                    issues = check_irods_vs_header_metadata(f, h_meta.libraries, i_meta.libraries, 'library')
                    problems.extend(issues)

                    issues = seq_consistency_checks.compare_entity_sets_in_seqsc(i_meta.libraries, 'library')
                    problems.extend(issues)
                else:
                    if 'irods_vs_header' in args.test_library:
                        issues = check_irods_vs_header_metadata(f, h_meta.libraries, i_meta.libraries, 'library')
                        problems.extend(issues)

                    if 'irods_vs_seqsc' in args.test_library:
                        issues = seq_consistency_checks.compare_entity_sets_in_seqsc(i_meta.libraries, 'library')
                        problems.extend(issues)


            if args.test_study or args.all_tests:
                issues = seq_consistency_checks.compare_entity_sets_in_seqsc(i_meta.studies, 'study')
                problems.extend(issues)




            if args.all_tests or args.test_complete_meta:
                # TODO: Add a warning that by default there is a default config file used
                if not args.config_file:
                    config_file = config.IRODS_ATTRIBUTE_FREQUENCY_CONFIG_FILE
                else:
                    config_file = args.config_file
                try:
                    diffs = complete_irods_metadata_checks.check_avus_freq_vs_config_freq(irods_avus, config_file)
                except IOError:
                    problems.append(error_types.TestImpossibleToRunError(f, "Test iRODS metadata is complete",
                                                                         "Config file missing: "+str(config_file)))
                else:
                    diffs_as_exc = complete_irods_metadata_checks.from_tuples_to_exceptions(diffs)
                    for d in diffs_as_exc:
                        d.fpath = f
                    problems.extend(diffs_as_exc)

        print "FILE: " + str(f) + " -- PROBLEMS found: " + str(problems)



    # OUTPUTS

    ## FILTER OUTPUT depending on what params were given (what was asked as output)

    ## PUT THE OUTPUT IN REQUESTED FORMAT



def start_tests(study=None, file_type='both', fpaths=None, fofn_path=None, samples_irods_vs_header=True, samples_irods_vs_seqscape=True,
                libraries_irods_vs_header=True, libraries_irods_vs_seqscape=True, study_irods_vs_seqscape=True,
                collateral_tests=True, desired_ref=None, irods_meta_conf=None):

    fpaths_irods = collect_fpaths_from_args(study, file_type, fpaths, fofn_path)
    print "I have collected "+ str(len(fpaths_irods)) + " paths.....starting to analyze......."

    for fpath in fpaths_irods:
        if not fpath:
            continue
        #print "FPATH analyzed: " + str(fpath)

        if samples_irods_vs_header or libraries_irods_vs_header:
            irods_metadata = metadata_utils.iRODSUtils.retrieve_irods_avus(fpath)
            header_metadata = metadata_utils.HeaderUtils.get_parsed_header_from_irods_file(fpath)
            if irods_meta_conf:

                pass
            run_metadata_tests(fpath, irods_metadata, header_metadata,
                   samples_irods_vs_header, samples_irods_vs_seqscape,
                   libraries_irods_vs_header, libraries_irods_vs_seqscape,
                   study_irods_vs_seqscape, collateral_tests, desired_ref)
        if irods_meta_conf:
            diffs = complete_irods_metadata_checks.compare_avus_vs_config_frequencies(fpath, irods_meta_conf)
            print "IRODS METADATA CHECKS: "+ str(diffs)
    #print "FILES PER TYPE: CRAMs = " + str(nr_crams) + " and BAMs = " + str(nr_bams)

# TODO: write in README - actually all these tests apply only to irods seq data...
def main1():
    args = parse_args()
    start_tests(args.study, args.file_type, args.fpaths_irods, args.fofn, args.samples_irods_vs_header, args.samples_irods_vs_seqscape,
                args.libraries_irods_vs_header, args.libraries_irods_vs_seqscape, args.study_irods_vs_seqscape,
                args.collateral_tests, args.desired_ref, args.check_irods_meta_against_config)


if __name__ == '__main__':
    main()


