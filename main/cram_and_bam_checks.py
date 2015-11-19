#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK

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

#from main import arg_parser
#from meta_check.main import arg_parser

from main import arg_parser

from main import metadata_utils
#from main import irods_seq_data_tests as seq_tests
from main import irods_metadata_consistency_checks as seq_consistency_checks
from main import error_types
from main import complete_irods_metadata_checks
#from main.. import config
import config
from main import constants
from collections import defaultdict
from irods_baton import baton_wrapper as baton
import sys
import os
from com import utils

from metadata_types.seqscape_metadata import SeqscapeMetadata
from metadata_checks.seqsc_metadata_checks import SeqscapeRawMetadataChecks
from metadata_provider.seqscape_meta_provider import SeqscapeRawMetadataProvider


#BOTH_FILE_TYPES = 'both'
from metadata_types import irods_metadata as irods_meta_module


def check_irods_vs_header_metadata(irods_path, header_dict, irods_dict, entity_type):
    """
        where: (e.g.)
         irods_dict = dict('name': [sample_name], accession_number: [samples_acc_nr], internal_id: [internal_id])
         header_dict = dict('name': [sample_name], accession_number: [samples_acc_nr], internal_id: [internal_id])
    """
    problems = []
    for id_type, head_ids_list in header_dict.items():
        if irods_dict.get(id_type) and header_dict.get(id_type):
            if set(head_ids_list).difference(set(irods_dict[id_type])):
                problems.append(error_types.HeaderVsIrodsMetadataAttributeError(fpath=irods_path, attribute=id_type,
                                                                      header_value=str(head_ids_list),
                                                                      irods_value=irods_dict[id_type],
                                                                      entity_type=entity_type))
    return problems



def read_file_into_list(fofn_path):
    fofn_fd = open(fofn_path)
    files_list = [f.strip() for f in fofn_fd]
    fofn_fd.close()
    return files_list


def write_list_to_file(input_list, output_file, header=None):
    out_fd = open(output_file, 'a')
    if header:
        out_fd.write(header+'\n')
    for entry in input_list:
        out_fd.write(entry+'\n')
    out_fd.write('\n')
    out_fd.close()

def write_tuples_to_file(tuples, output_file, header_tuple=None):
    out_fd = open(output_file, 'a')
    for elem in header_tuple:
        out_fd.write(str(elem)+"\t")
    out_fd.write("\n")
    for tup in tuples:
        for elem in tup:
            out_fd.write(str(elem)+"\t")
        out_fd.write("\n")
    out_fd.close()



def collect_fpaths_by_study_name(study_name):
    avus_dict = {'study': study_name}
    return metadata_utils.iRODSiCmdsUtils.retrieve_list_of_files_by_avus(avus_dict)

def collect_fpaths_by_study_name_and_filter(study_name, filter_dict):
    avus_dict = {'study': study_name}
    avus_dict.update(filter_dict)
    return metadata_utils.iRODSiCmdsUtils.retrieve_list_of_files_by_avus(avus_dict)

def collect_fpaths_by_study_accession_nr_and_filter(study_acc_nr, filter_dict):
    avus_dict = {'study_accession_number': study_acc_nr}
    avus_dict.update(filter_dict)
    return metadata_utils.iRODSiCmdsUtils.retrieve_list_of_files_by_avus(avus_dict)

def collect_fpaths_by_study_internal_id_and_filter(study_id, filter_dict):
    avus_dict = {'study_id': study_id}
    avus_dict.update(filter_dict)
    return metadata_utils.iRODSiCmdsUtils.retrieve_list_of_files_by_avus(avus_dict)

# def collect_fpaths_by_study_identif_and_filter(id_type, id_value, filter_dict):
#     return metadata_utils.iRODSUtils.retrieve_list_of_files_by_avus({id_type: id_value}.update(filter_dict))

def check_same_files_by_diff_study_ids(name, internal_id, acc_nr, filters_dict):  # filters can be: None => get any value for this tag, 1, or 0
    files_by_name = set(collect_fpaths_by_study_name_and_filter(str(name), filters_dict))
    files_by_acc_nr = set(collect_fpaths_by_study_accession_nr_and_filter(str(acc_nr), filters_dict))
    files_by_id = set(collect_fpaths_by_study_internal_id_and_filter(str(internal_id), filters_dict))

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


def collect_fpaths_from_args(study=None, file_type=constants.CRAM_FILE_TYPE, files_list=None, fofn_path=None):
    if study:
        fpaths_irods = collect_fpaths_by_study_name(study, file_type)
    elif fofn_path:
        fpaths_irods = read_file_into_list(fofn_path)
    elif files_list:
        fpaths_irods = files_list
    return fpaths_irods

def collect_fpaths_for_samples(samples):
    pass

def filter_by_file_type(fpaths, file_type):
    return [f for f in fpaths if f.endswith(file_type)]

def infer_file_type(fpath):
    if fpath.endswith(constants.BAM_FILE_TYPE):
        return constants.BAM_FILE_TYPE
    elif fpath.endswith(constants.CRAM_FILE_TYPE):
        return constants.CRAM_FILE_TYPE
    else:
        raise NotImplementedError("Infer file type was not implemented for " + str(fpath))



def filter_by_avu(fpath, avu_attribute, avu_value):
    pass# manual_qc,...

def decide_which_tests(all_tests=None, test_sample=None, test_library=None, test_study=None, desired_reference=None, test_md5=None, test_filename=None, test_complete_meta=None):
    run_header_tests = False
    run_irods_tests = False
    if all_tests:
        run_header_tests = True
        run_irods_tests = True
    else:
        if test_sample:
            if 'all' in test_sample or 'irods_vs_header' in test_sample:
                run_header_tests = True
        if test_library:
            if 'irods_vs_header' in test_library or 'all' in test_library:
                run_header_tests = True
        if any([test_sample, test_library, test_study, desired_reference, test_md5, test_filename, all_tests, test_complete_meta]):
            run_irods_tests = True
    return {'header_tests' : run_header_tests, 'irods_tests' : run_irods_tests}



def extract_filters_from_args(args):
    filters = {}
    if args.filter_npg_qc:
        filters['manual_qc'] = args.filter_npg_qc
    if args.filter_target:
        filters['target'] = args.filter_target
    if len(args.file_types) == 1:
        filters['type'] = args.file_types[0]
    return filters

def extract_meta_search_criteria(args):
    search_criteria = []
    if args.study_name:
        search_criteria.append(('study', args.study_name))
    elif args.study_acc_nr:
        search_criteria.append(('study_accession_number', args.study_acc_nr))
    elif args.study_internal_id:
        search_criteria.append(('study_id', args.study_internal_id))

    if args.filter_npg_qc:
        search_criteria.append(('manual_qc', args.filter_npg_qc))
    if args.filter_target:
        search_criteria.append(('target', args.filter_target))
    if len(args.file_types) == 1:
        search_criteria.append(('type', args.file_types[0]))
    print("SEARCH CRITERIA : " + str(search_criteria))
    return search_criteria








def is_input_given_by_path(args):
    if args.fpaths_irods or args.fofn:
        return True
    return False


def is_input_given_by_meta(args):
    if args.study_internal_id or args.study_acc_nr or args.study_name or args.sample_names:
        return True
    return False

def save_metadata(irods_meta, header_dict, output_dict):
    # populate the samples and libraries for outputting them (in case someone asked for them)
    output_dict['irods_samples_by_names'].extend(irods_meta.samples.get('name'))
    output_dict['irods_samples_by_egaids'].extend(irods_meta.samples.get('accession_number'))

    output_dict['irods_libraries_by_names'].extend(irods_meta.libraries.get('name'))
    output_dict['irods_libraries_by_ids'].extend(irods_meta.libraries.get('internal_id'))

    output_dict['irods_studies_by_names'].extend(irods_meta.studies.get('name'))
    output_dict['irods_studies_by_egaids'].extend(irods_meta.studies.get('accession_number'))

    output_dict['header_samples'].extend(header_dict.samples['accession_number'])
    output_dict['header_samples'].extend(header_dict.samples['name'])
    output_dict['header_samples'].extend(header_dict.samples['internal_id'])

    output_dict['header_libraries'].extend(header_dict.libraries['name'])
    output_dict['header_libraries'].extend(header_dict.libraries['internal_id'])


def must_output_entities(args):
    if args.meta_dir:
        return True
    return False

# unused
def print_errors(errors_list, issues_per_file):
    #warnings = defaultdict(list) # type : files
    warnings = []
    errors = {}
    warning_types = [error_types.TestImpossibleToRunError]   # TODO: organize the errors in warnings and errors (here I assumed the TestIm err has the attribute test_name)
    for fpath, problems in list(issues_per_file.items()):
        file_pbs = []
        for pb in problems:
            if type(pb) in warning_types:
                #warnings[pb.test_name].append(fpath)
                warnings.append(pb)
            elif problems:
                file_pbs.append(pb)
        if file_pbs:
            errors[fpath] = file_pbs
            #print "File: " + str(fpath) + " has problems: " + str(file_pbs)

    if errors:
        print("ERRORS: ")
        for fpath, err in list(errors.items()):
            print("File: " + str(err))
    if warnings:
        print("WARNINGS:")
        for warn in warnings:
            print(str(warn))

        # for warn, files in warnings.items():
        #     print str(warn) + " - files affected: " + str(files)


class TestResult(object):
    def __init__(self, test_name, result, reason=None):
        self.test_name = test_name
        self.result = result
        self.reason = reason

    def __str__(self):
        if self.reason:
            return "Test " + str(self.test_name) + " result = " + str(self.result) + " reson = " + str(self.reason)
        return "Test " + str(self.test_name) + " result = " + str(self.result) + " reson = "

    def __repr__(self):
        return self.__str__()

def main():
    args = arg_parser.parse_args()

    header_meta_needed = is_header_metadata_needed(args)
    irods_meta_needed = is_irods_metadata_needed(args)  # Is there any scenario in which we don't need the irods meta?

    general_errors = []

    if irods_meta_needed:
        filters = extract_filters_from_args(args)

        # QUERY BY AVUS and get AVUS for all the data objects found:
        #search_criteria = put_together_search_criteria(some_args)
        if is_input_given_by_path(args):
            if args.fpaths_irods:
                fpaths_checksum_and_avus = get_files_and_metadata_by_fpath(args.fpaths_irods)
            elif args.fofn:
                fpaths_irods = read_file_into_list(args.fofn)
                fpaths_checksum_and_avus = get_files_and_metadata_by_fpath(fpaths_irods)
        elif is_input_given_by_meta(args):
            search_criteria = extract_meta_search_criteria(args)
            if args.study_name or args.study_acc_nr or args.study_internal_id:
                try:
                    fpaths_checksum_and_avus = get_files_and_metadata_by_metadata(search_criteria)
                except IOError as e:
                    print("iRODS error when retrieving metadata: " + str(e))
                    sys.exit(0)
                else:
                    issues = check_same_files_by_diff_study_ids(args.study_name, args.study_internal_id, args.study_acc_nr, filters)
                    general_errors.extend(issues)
                    print("Ran check on the list of files retrieved by each study identifier -- result is: " + str(issues))

            elif args.sample_names or args.fosn:
                raise NotImplementedError


         ########################## TESTS #####################
        # PREPARING FOR THE TESTS

#        wanted_entities_as_output = must_output_entities(args)
        #all_entities_as_output = defaultdict(list)
        issues_per_file = {}
        metadata_per_file = {}
        tests_per_file = {}
        for fpath, meta_dict in list(fpaths_checksum_and_avus.items()):
            tests_results = []
            problems = []
            avu_issues = irods_meta_module.IRODSFileMetadata.run_avu_count_checks(fpath, meta_dict['avus'])
            problems.extend(avu_issues)

            i_meta = irods_meta_module.IRODSFileMetadata.from_avus_to_irods_metadata(meta_dict['avus'], fpath)
            i_meta.ichksum_md5 = meta_dict['checksum']

            # Check for sanity before starting the tests:
            sanity_issues = i_meta.run_field_sanity_checks_and_filter()
            problems.extend(sanity_issues)


            # FETCH Seqscape raw metadata:
            raw_ss_meta = SeqscapeRawMetadataProvider.retrieve_raw_metadata(i_meta.samples, i_meta.libraries, i_meta.studies)

            # RUN CHECKS:
            SeqscapeRawMetadataChecks.check_raw_metadata(raw_ss_meta)

            # Convert raw metadata to usable metadata:
            ss_meta = SeqscapeMetadata.from_raw_metadata(raw_ss_meta)


            print("SS metadata: ", ss_meta)
            print("RAW METADATAAAAAAAAAAAAAA", raw_ss_meta)


            if header_meta_needed:
                try:
                    header = metadata_utils.HeaderUtils.get_parsed_header_from_irods_file(fpath)
                except IOError as e:
                    problems.append(e)
                else:
                    h_meta = header_meta_module.HeaderSAMFileMetadata.from_header_to_metadata(header, fpath)

            print("i meta: " + str(i_meta))
            print("H meta: " + str(h_meta))
           # save_metadata(i_meta, h_meta, all_entities_as_output)

            seqsc_meta = {}
            if args.test_md5 or args.all_tests:
                test_name = 'check_md5_in_irods_meta_vs_ichcksum'
                try:
                    i_meta.test_md5_calculated_vs_metadata()
                except error_types.WrongMD5Error as e:
                    problems.append(e)
                    tests_results.append(TestResult(test_name=test_name, result='FAIL', reason=str(e)))
                except error_types.TestImpossibleToRunError as e:
                    tests_results.append(TestResult(test_name=test_name, result='SKIP', reason=str(e)))
                else:
                    tests_results.append(TestResult(test_name=test_name, result='PASS'))

            if args.desired_reference or args.all_tests:
                test_name = 'check_reference_in_irods_vs_param'
                try:
                    i_meta.test_reference(args.desired_reference)
                except error_types.WrongReferenceError as e:
                    problems.append(e)
                    tests_results.append(TestResult(test_name=test_name, result='FAIL', reason=str(e)))
                except error_types.TestImpossibleToRunError as e:
                    tests_results.append(TestResult(test_name=test_name, result='SKIP', reason=str(e)))
                else:
                    tests_results.append(TestResult(test_name=test_name, result='PASS'))


            if args.test_filename or args.all_tests:
                test_name = 'check_lane_in_filename_vs_irods'
                try:
                    i_meta.test_lane_from_fname_vs_metadata()
                except error_types.IrodsMetadataAttributeVsFileNameError as e:
                    problems.append(e)
                    tests_results.append(TestResult(test_name=test_name, result='FAIL', reason=str(e)))
                except error_types.TestImpossibleToRunError as e:
                    tests_results.append(TestResult(test_name=test_name, result='SKIP', reason=str(e)))
                else:
                    tests_results.append(TestResult(test_name=test_name, result='PASS'))


                # test run_id
                test_name = 'check_run_id_in_filename_vs_irods'
                try:
                    i_meta.test_run_id_from_fname_vs_metadata()
                except error_types.IrodsMetadataAttributeVsFileNameError as e:
                    problems.append(e)
                    tests_results.append(TestResult(test_name=test_name, result='FAIL', reason=str(e)))
                except error_types.TestImpossibleToRunError as e:
                    tests_results.append(TestResult(test_name=test_name, result='SKIP', reason=str(e)))
                else:
                    tests_results.append(TestResult(test_name=test_name, result='PASS'))

            if args.test_sample or args.all_tests:
                if 'irods_vs_header' in args.test_sample or 'all' in args.test_sample or args.all_tests:
                    test_name = 'check_sample_meta_irods_vs_header'
                    if not i_meta.samples:
                        tests_results.append(TestResult(test_name=test_name, result='SKIP', reason='No irods sample metadata'))
                    elif not h_meta.samples:
                        tests_results.append(TestResult(test_name=test_name, result='SKIP', reason='No header sample metadata'))
                    else:
                        issues = check_irods_vs_header_metadata(fpath, h_meta.samples, i_meta.samples, 'sample')
                        problems.extend(issues)
                        if issues:
                            tests_results.append(TestResult(test_name=test_name, result='FAIL', reason=str(issues)))
                        else:
                            tests_results.append(TestResult(test_name=test_name, result='PASS'))

                if 'irods_vs_seqsc' in args.test_sample or 'all' in args.test_sample or args.all_tests:
                    test_name = 'check_sample_meta_irods_vs_seqsc'
                    if not i_meta.samples:
                        tests_results.append(TestResult(test_name=test_name, result='SKIP', reason='No irods sample metadata'))
                    issues, ss_samples = seq_consistency_checks.fetch_and_compare_entity_sets_in_seqsc(i_meta.samples, 'sample')
                    problems.extend(issues)
                    ss_samples = seq_consistency_checks.from_seqsc_entity_list_to_list_of_ids(ss_samples)
                    seqsc_meta['samples'] = ss_samples

                    issues = seq_consistency_checks.check_sample_is_in_desired_study(i_meta.samples['internal_id'], i_meta.studies['name'])
                    problems.append(issues)

            if args.test_library or args.all_tests:
                if 'irods_vs_header' in args.test_library or args.all_tests or 'all' in args.test_library:
                    issues = check_irods_vs_header_metadata(fpath, h_meta.libraries, i_meta.libraries, 'library')
                    problems.extend(issues)

                if 'irods_vs_seqsc' in args.test_library or args.all_tests or 'all' in args.test_library:
                    issues, ss_libs = seq_consistency_checks.fetch_and_compare_entity_sets_in_seqsc(i_meta.libraries, 'library')
                    problems.extend(issues)
                    ss_libs = seq_consistency_checks.from_seqsc_entity_list_to_list_of_ids(ss_libs)
                    seqsc_meta['libraries'] = ss_libs


            if args.test_study or args.all_tests:
                issues, ss_studies = seq_consistency_checks.fetch_and_compare_entity_sets_in_seqsc(i_meta.studies, 'study')
                problems.extend(issues)
                ss_studies = seq_consistency_checks.from_seqsc_entity_list_to_list_of_ids(ss_studies)
                seqsc_meta['studies'] = ss_studies


            if args.all_tests or args.test_complete_meta:
                # TODO: Add a warning that by default there is a default config file used
                if not args.config_file:
                    config_file = config.IRODS_ATTRIBUTE_FREQUENCY_CONFIG_FILE
                else:
                    config_file = args.config_file
                try:
                    diffs = complete_irods_metadata_checks.check_avus_freq_vs_config_freq(meta_dict['avus'], config_file)
                except IOError:
                    problems.append(error_types.TestImpossibleToRunError(fpath, "Test iRODS metadata is complete",
                                                                         "Config file missing: "+str(config_file)))
                else:
                    diffs_as_exc = complete_irods_metadata_checks.from_tuples_to_exceptions(diffs)
                    for d in diffs_as_exc:
                        d.fpath = fpath
                    problems.extend(diffs_as_exc)

            if problems:
                issues_per_file[fpath] = problems
            metadata_per_file[fpath] = {'i_meta' : i_meta, 'h_meta': h_meta, 'seqsc_meta': seqsc_meta}
        print("Metadata per file: " + str(metadata_per_file))

            #all_problems.extend(problems)




        ########## PROVIDE THE OUTPUT BACK TO THE USER ##########################

        # (out_file, issues, metadata):
        # if args.out_file:
        #     write_output_report_to_file(args.out_file, general_errors, all_entities_as_output)


        # if args.meta_dir:
        #     mkdir_if_doesnt_exist(args.meta_dir)
        #     output_entities_to_dir(all_entities_as_output, args.meta_dir)

        #### OUTPUTTING the files by type ############
        counter_by_ftype = count_files_per_format(list(fpaths_checksum_and_avus.keys()))

        files_sorted_by_type = group_fpaths_by_fname(list(fpaths_checksum_and_avus.keys()))

        # printing out the count of files per format:
        for format, n in list(counter_by_ftype.items()):
            print("format = " + str(format) + " nr files = " + str(n))

        # TEST IF all the files appear in all formats requested:
        if args.fnames_by_ftype:
            # Going through the sorted files by type and put them in tuples
            ftypes_tuples = group_fpaths_by_format_in_tuples(args.file_types, files_sorted_by_type)
            write_tuples_to_file(ftypes_tuples, args.out_file, args.file_types)

            # Analyze the sorted dict to test that it all looks fine:
            missing_formats_errors = check_for_missing_file_formats(files_sorted_by_type, args.file_types)
            if missing_formats_errors:
                general_errors.extend(missing_formats_errors)


def write_report_to_file(report_file, issues_per_file):
    with open(report_file, 'w') as report_fd:
#        for fpath, set_of_tests in issues_per_file
        pass

def write_meta_to_file(meta_file, metadata_per_file):
    with open(meta_file, 'w') as meta_fd:
        pass


def mkdir_if_doesnt_exist(dir_path):
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path)


def check_for_missing_file_formats(files_sorted_by_type, formats):
    missing_ftypes_errors = []
    for fname, files in list(files_sorted_by_type.items()):
        existing_ftypes = set()
        wanted_formats = set(formats)
        for f in files:
            format = infer_file_type(f)
            existing_ftypes.add(format)

        # Check if the existing file types are the wanted ones...
        if wanted_formats != existing_ftypes:
            missing_ftypes = wanted_formats.difference(existing_ftypes)
            missing_ftypes_errors.append(error_types.MissingFileFormatsFromIRODSError(fname, missing_ftypes))
    return missing_ftypes_errors

# Count nr of files per type and build the sorted dict:
def count_files_per_format(fpaths):
    """
    This function counts the number of files in each format.
    :param fpaths: string - list of file paths
    :return: a defaultdict having as key = the file format (CRAM/BAM/..) and value = int (nr of files in CRAM format)
    """
    counter_by_ftype = defaultdict(int)
    for fpath in fpaths:
        ftype = infer_file_type(fpath)
        counter_by_ftype[ftype] += 1
    return counter_by_ftype

def group_fpaths_by_fname(fpaths):
    """
    This function groups a list of file paths by filename. This is useful because a file can appear in different formats,
    (the same filename but a different extension).
    :param fpaths: list of strings corresponding to filepaths
    :return: a defaultdict containing as key = filename (without extension), value = {file_format : fpath}
    """
    files_sorted_by_type = defaultdict(dict)
    for fpath in fpaths:
        fname = utils.extract_fname_without_ext(fpath)
        ftype = infer_file_type(fpath)
        files_sorted_by_type[fname][ftype] = fpath
    return files_sorted_by_type

def group_fpaths_by_format_in_tuples(ftypes, files_sorted_by_type):
    ftypes_tuples = []
    for fname, ftypes_dict in list(files_sorted_by_type.items()):
        ftyptes_per_fname = []
        for ftype in ftypes:
            fpath_per_type = ftypes_dict.get(ftype) or 'missing'
            ftyptes_per_fname.append(fpath_per_type)
        ftypes_tuples.append(ftyptes_per_fname)
    return ftypes_tuples

def remove_non_ascii(input_str):
    return ''.join([i if (ord(i) < 128 and ord(i) >= 65) or i == '_' else '' for i in input_str])

def output_entities_to_dir( entities, out_dir, base_fname=''):
        # TODO: add try - except to test if the user has permission to write to this dir

        header_sample_ids_file = os.path.join(out_dir, base_fname + '.header.sample.ids')
        header_library_ids_file = os.path.join(out_dir, base_fname + '.header.library.ids')
        irods_sample_names_file = os.path.join(out_dir, base_fname + '.irods.sample.names')
        irods_sample_egaids_file = os.path.join(out_dir, base_fname + '.irods.sample.egaids')
        irods_library_names_file = os.path.join(out_dir, base_fname + '.irods.library.names')
        irods_library_ids_file = os.path.join(out_dir, base_fname + '.irods.library.ids')
        irods_study_names_file = os.path.join(out_dir, base_fname + '.irods.study.names')
        irods_study_egaids_file = os.path.join(out_dir, base_fname + '.irods.study.egaids')


        ############ OUTPUT HEADER METADATA ############
        # outputting HEADER samples:
        #if args.header_sample_ids_file:
        write_list_to_file(entities['header_samples'], header_sample_ids_file)

        # outputting HEADER libraries:
        #if args.header_library_ids_file:
        write_list_to_file(entities['header_libraries'], header_library_ids_file)

        ############ OUTPUT IRODS METADATA ###############
        # outputting IRODS samples by EGA ID:
        #if args.sample_ega_out_file:
        write_list_to_file(entities['irods_samples_by_egaids'], irods_sample_egaids_file)

        # outputting iRODS samples by name
        #if args.sample_names_out_file:
        write_list_to_file(entities['irods_samples_by_names'], irods_sample_names_file)

        # outputting iRODS libraries by id
        #if args.library_ids_out_file:
        write_list_to_file(entities['irods_libraries_by_ids'], irods_library_ids_file)

        #outputting iRODS libraries by name
        #if args.library_names_out_file:
        write_list_to_file(entities['irods_libraries_by_names'], irods_library_names_file)

        ##### STUDIES #####
        # outputting IRODS studies by ega id:
        #if args.study_egaids_out_file:
        write_list_to_file(entities['irods_studies_by_egaids'], irods_study_egaids_file)

        # outputting IRODS studies by name:
        #if args.study_names_out_file:
        write_list_to_file(entities['irods_studies_by_names'], irods_study_names_file)



def is_header_metadata_needed(args):
    # Deciding what tests to run
    header_meta_needed = False
    if args.all_tests:
        header_meta_needed = True
    else:
        if args.test_sample:
            if 'all' in args.test_sample or 'irods_vs_header' in args.test_sample:
                header_meta_needed = True
        if args.test_library:
            if 'irods_vs_header' in args.test_library or 'all' in args.test_library:
                header_meta_needed = True
        # check by wanted output:
        if args.meta_dir:
            header_meta_needed = True
    return header_meta_needed


def is_irods_metadata_needed(args):
    irods_meta_needed = False
    if args.all_tests:
        #irods_meta_needed = True
        return True
    else:
        if any([args.test_sample, args.test_library, args.test_study, args.desired_reference, args.test_md5, args.test_filename, args.all_tests, args.config_file]):
#            irods_meta_needed = True
            return True
        # check by wanted output:
        # if any([args.sample_ega_out_file, args.sample_names_out_file, #args.bad_sample_egaids_out_file,args.bad_sample_names_out_file, args.bad_library_names_out_file,args.bad_library_ids_out_file,
        #         args.library_names_out_file, args.library_ids_out_file,
        #         args.study_names_out_file,
        #         args.study_egaids_out_file, args.entities_out_dir, args.entities_out_file]):
        if args.meta_dir:
#            irods_meta_needed = True
            return True
    return irods_meta_needed


if __name__ == '__main__':
    main()


