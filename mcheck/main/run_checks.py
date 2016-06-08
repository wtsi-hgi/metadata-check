"""
Copyright (C) 2016  Genome Research Ltd.

Author: Irina Colgiu <ic4@sanger.ac.uk>

This program is part of meta-check

meta-check is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.
You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

This file has been created on May 05, 2016.
"""

import os
import sys
from collections import defaultdict
from typing import Dict, Set

from mcheck.main import arg_parser
from mcheck.metadata.irods_metadata.irods_meta_provider import iRODSMetadataProvider
from mcheck.metadata.seqscape_metadata.seqscape_meta_provider import SeqscapeRawMetadataProvider
from mcheck.metadata.file_header_metadata.header_meta_provider import SAMFileHeaderMetadataProvider
from mcheck.metadata.seqscape_metadata.seqscape_metadata import SeqscapeMetadata
from mcheck.metadata.irods_metadata.file_metadata import IrodsSeqFileMetadata
from mcheck.results.checks_results import CheckResult
from mcheck.results.constants import SEVERITY
from mcheck.check_names import CHECK_NAMES
from mcheck.results.checks_results import RESULT
from mcheck.results.results_processing import CheckResultsProcessing


def read_file_into_list(fofn_path):
    fofn_fd = open(fofn_path)
    files_list = [f.strip() for f in fofn_fd]
    fofn_fd.close()
    return files_list


def write_list_to_file(input_list, output_file, header=None):
    out_fd = open(output_file, 'a')
    if header:
        out_fd.write(header + '\n')
    for entry in input_list:
        out_fd.write(str(entry) + '\n')
    out_fd.write('\n')
    out_fd.close()


def write_tuples_to_file(tuples, output_file, header_tuple=None):
    out_fd = open(output_file, 'a')
    for elem in header_tuple:
        out_fd.write(str(elem) + "\t")
    out_fd.write("\n")
    for tup in tuples:
        for elem in tup:
            out_fd.write(str(elem) + "\t")
        out_fd.write("\n")
    out_fd.close()


def write_dict_to_file(input_dict, output_file):
    out_fd = open(output_file, 'a')
    for k, v in input_dict.items():
        out_fd.write(str(k))
        out_fd.write("\n")
        out_fd.write(str(v))
        out_fd.write("\n")
    out_fd.close()


class BulkMetadataRetrieval:
    @staticmethod
    def fetch_irods_metadata_by_metadata(search_criteria):
        """
        Queries iRODS for all the files that match the search criteria and fetch all the metadata for them.
        :param search_criteria: a dict with: key = search field name, value = search field value
        :return:
        """
        return iRODSMetadataProvider.retrieve_raw_files_metadata_by_metadata(search_criteria)


class FileMetadataRetrieval:
    @staticmethod
    def fetch_seqscape_metadata(samples, libraries, studies):
        return SeqscapeRawMetadataProvider.fetch_raw_metadata(samples, libraries, studies)

    @staticmethod
    def fetch_header_metadata(fpath):
        return SAMFileHeaderMetadataProvider.fetch_metadata(fpath, irods=True)

    @staticmethod
    def fetch_irods_metadata_by_path(fpath):
        return iRODSMetadataProvider.fetch_raw_file_metadata_by_path(fpath)


class MetadataSelfChecks:
    @staticmethod
    def check_and_convert_seqscape_metadata(raw_metadata):
        problems = raw_metadata.check_metadata()
        seqsc_metadata = SeqscapeMetadata.from_raw_metadata(raw_metadata)
        problems.extend(seqsc_metadata.check_metadata())
        return seqsc_metadata, problems

    @staticmethod
    def check_and_convert_header_metadata(header_metadata):
        problems = header_metadata.check_metadata()
        header_metadata.fix_metadata()
        return header_metadata, problems

    @staticmethod
    def check_and_convert_irods_metadata(raw_metadata, reference=None, attribute_counts=None):
        print("Type of raw metadata: %s" % str(type(raw_metadata)))
        problems = raw_metadata.check_metadata()
        file_metadata = IrodsSeqFileMetadata.from_raw_metadata(raw_metadata)
        problems.extend(file_metadata.check_metadata(reference))
        return file_metadata, problems


class FileMetadataComparison:
    @staticmethod
    def are_entities_equal(entity_set1: Dict[str, Set], entity_set2: Dict[str, Set]):
        """
        Compares the entities in 2 different dicts that look like: {'accession_number': {'EGAN00001099700'}, 'name': {'SC_SEPI5488478'}, 'internal_id': {'1582333'}}
        :param entity_set1: dict of key = id_type, value = id_value
        :param entity_set2: dict of key = id_type, value = id_value
        :return:
        """
        for id_type, values in entity_set1.items():
            if values and entity_set2.get(id_type):
                if values != entity_set2.get(id_type):
                    return False
        return True

    @staticmethod
    def find_differences(metadata1, metadata2, entity_types_list):
        for entity_type in entity_types_list:
            metadata_entities1 = getattr(metadata1, entity_type)  # header
            metadata_entities2 = getattr(metadata2, entity_type)  # seqsc
            differences = {}
            for id_type, values in metadata_entities1.items():
                if values and metadata_entities2.get(id_type):
                    if values != metadata_entities2.get(id_type):
                        differences[id_type] = set(values).difference(set(metadata_entities2.get(id_type)))
            return differences


# def query_for_metadata(filters, study_metadata):
def fetch_all_matching_metadata(irods_zone, filter_by_npg_qc=None, filter_by_target=None, filter_by_file_types=None,
                                match_study_name=None, match_study_acc_nr=None, match_study_id=None):
    search_criteria = {}
    if filter_by_npg_qc:
        search_criteria['manual_qc'] = filter_by_npg_qc
    else:
        print(
            "WARNING! You haven't filtered on manual_qc field. You will get the report from checking all the data, no matter if qc pass of fail.")
    if filter_by_target:
        search_criteria['target'] = filter_by_target
    else:
        print(
            "WARNING! You haven't filtered by target field. You will get back the report from checking all the data, no matter if it is the target or not, hence possibly also PhiX")
    if filter_by_file_types:
        for ftype in filter_by_file_types:
            search_criteria['type'] = ftype
    else:
        print("WARNING! You haven't filtered on file type.")

    # Parse input parameters and obtain files+metadata:
    if match_study_name:
        search_criteria['study'] = match_study_name
    elif match_study_acc_nr:
        search_criteria['study_accession_number'] = match_study_acc_nr
    elif match_study_id:
        search_criteria['study_internal_id'] = match_study_id

    try:
        all_files_metadata_objs_list = iRODSMetadataProvider.retrieve_raw_files_metadata_by_metadata(search_criteria,
                                                                                                     irods_zone)
        return all_files_metadata_objs_list
    except Exception as e:
        print(e)
        sys.exit(1)


def run_metacheck_by_metadata():
    pass


def run_metachecks_by_path():
    pass


def fetch_and_preprocess_irods_metadata_by_metadata(issues_dict, irods_zone, reference=None, filter_by_npg_qc=None,
                                                    filter_by_target=None,
                                                    filter_by_file_types=None, match_study_name=None,
                                                    match_study_acc_nr=None, match_study_id=None):
    """
    This function takes some filtering/matching criteria for selecting data from iRODS based on metadata.
    The client also passes an issues_dict to this function as parameter, which the current function just needs to
    update with the issues found on the files found in iRODS to match the criteria.
    :param issues_dict: an existing dictionary of issues, to which this function needs to add the issues found
    :param irods_zone: the irods zone where to search for the data matching the criteria given
    :param reference:
    :param filter_by_npg_qc:
    :param filter_by_target:
    :param filter_by_file_types:
    :param match_study_name:
    :param match_study_acc_nr:
    :param match_study_id:
    :return:
    """
    irods_metadata_by_path = {}
    all_files_metadata_objs_list = fetch_all_matching_metadata(irods_zone, filter_by_npg_qc,
                                                               filter_by_target, filter_by_file_types,
                                                               match_study_name, match_study_acc_nr,
                                                               match_study_id)

    for raw_metadata in all_files_metadata_objs_list:
        fpath = os.path.join(raw_metadata.dir_path, raw_metadata.fname)
        file_metadata, problems = MetadataSelfChecks.check_and_convert_irods_metadata(raw_metadata, reference)
        irods_metadata_by_path[fpath] = file_metadata
        issues_dict[fpath].extend(problems)
    return irods_metadata_by_path


def fetch_and_preprocess_irods_metadata_by_path(irods_fpaths, issues_dict, reference):
    """
    This function fetches the irods metadata by file path and preprocesses it.
    It also adds the issues found to the issues_dict given as parameter.
    :param irods_fpaths:
    :param issues_dict:
    :param reference:
    :return:
    """
    irods_metadata_dict = defaultdict(list)
    for fpath in irods_fpaths:
        try:
            raw_metadata = iRODSMetadataProvider.fetch_raw_file_metadata_by_path(fpath)
        except Exception as e:
            print(e)
            sys.exit(1)
        else:
            file_metadata, problems = MetadataSelfChecks.check_and_convert_irods_metadata(raw_metadata, reference)
            irods_metadata_dict[fpath] = file_metadata
            issues_dict[fpath].extend(problems)
            return irods_metadata_dict


def fetch_and_preprocess_header_metadata(irods_fpaths, issues_dict):
    header_metadata_dict = {}
    for fpath in irods_fpaths:
        header_metadata = SAMFileHeaderMetadataProvider.fetch_metadata(fpath, irods=True)
        processed_header_metadata, problems = MetadataSelfChecks.check_and_convert_header_metadata(header_metadata)
        header_metadata_dict[fpath] = processed_header_metadata
        issues_dict[fpath].extend(problems)
    return header_metadata_dict


def fetch_and_preprocess_seqscape_metadata(irods_metadata_by_path_dict, issues_dict):
    seqsc_metadata_dict = {}
    for fpath, irods_metadata in irods_metadata_by_path_dict.items():
        raw_metadata = SeqscapeRawMetadataProvider.fetch_raw_metadata(irods_metadata.samples, irods_metadata.libraries,
                                                                      irods_metadata.studies)
        seqsc_metadata, problems = MetadataSelfChecks.check_and_convert_seqscape_metadata(raw_metadata)
        seqsc_metadata_dict[fpath] = seqsc_metadata
        issues_dict[fpath].extend(problems)
    return seqsc_metadata_dict


def check_metadata_across_different_sources(irods_metadata_dict, header_metadata_dict, seqsc_metadata_dict, issues_dict):
    """
    This function checks the metadata from 3 different sources in terms of samples, libraries and studies.
    As a result it updates the issues_dict by appending the CheckResults obtain after running the latest tests.
    :param irods_metadata_dict:
    :param header_metadata_dict:
    :param seqsc_metadata_dict:
    :param issues_dict:
    :return:
    """
    for fpath, irods_metadata in irods_metadata_dict.items():
        header_metadata = header_metadata_dict[fpath]
        seqscape_metadata = seqsc_metadata_dict[fpath]
        seqscape_diff_header = FileMetadataComparison.find_differences(seqscape_metadata, header_metadata,
                                                                       ['samples', 'libraries', 'studies'])
        header_diff_seqscape = FileMetadataComparison.find_differences(header_metadata, seqscape_metadata,
                                                                       ['samples', 'libraries', 'studies'])

        irods_diff_header = FileMetadataComparison.find_differences(irods_metadata, header_metadata,
                                                                    ['samples', 'libraries', 'studies'])
        header_diff_irods = FileMetadataComparison.find_differences(header_metadata, irods_metadata,
                                                                    ['samples', 'libraries', 'studies'])

        print("Irods metadata: %s" % irods_metadata)
        print("Seqscape metadata: %s" % seqscape_metadata)
        print("Header metadata: %s" % header_metadata)
        ss_vs_h_check_result = CheckResult(check_name=CHECK_NAMES.check_seqscape_ids_compared_to_header_ids)
        if seqscape_diff_header:
            error_msg = "Differences: %s" % seqscape_diff_header
            ss_vs_h_check_result.error_message = error_msg
            ss_vs_h_check_result.result = RESULT.FAILURE
        issues_dict[fpath].append(ss_vs_h_check_result)

        h_vs_ss_check_result = CheckResult(check_name=CHECK_NAMES.check_header_ids_compared_to_seqscape_ids)
        if header_diff_seqscape:
            error_msg = "Differences: %s" % header_diff_seqscape
            h_vs_ss_check_result.result = RESULT.FAILURE
            h_vs_ss_check_result.error_message = error_msg
        issues_dict[fpath].append(h_vs_ss_check_result)

        i_vs_h_check_result = CheckResult(check_name=CHECK_NAMES.check_irods_ids_compared_to_header_ids)
        if irods_diff_header:
            error_msg = "Differences: %s" % irods_diff_header
            i_vs_h_check_result.error_message = error_msg
            i_vs_h_check_result.result = RESULT.FAILURE
        issues_dict[fpath].append(i_vs_h_check_result)

        h_vs_i_check_result = CheckResult(check_name=CHECK_NAMES.check_header_ids_compared_to_irods_ids)
        if header_diff_irods:
            error_msg = "Differences between what is in the header and not in iRODS: %s" % header_diff_irods
            h_vs_i_check_result.error_message = error_msg
            h_vs_i_check_result.result = RESULT.FAILURE
        issues_dict[fpath].append(h_vs_i_check_result)


def present_output(issues_by_path, output_dir):
    for fpath, file_issues in issues_by_path.items():
        sorted_by_exec = CheckResultsProcessing.group_by_executed(file_issues)
        print("Sorted by exec = True:")
        for check in  sorted_by_exec[True]:
            print(check)
        print("Sorted by exec = False:")
        for check in sorted_by_exec[False]:
            print(check)
        sorted_by_severity = CheckResultsProcessing.group_by_severity(sorted_by_exec[True])
        print("SORTED BY SEVERITY::::::::::")
        for severity, fpaths_issues in sorted_by_severity.items():
            print("SEVERITY: %s" % severity)
            write_list_to_file(fpaths_issues, os.path.join(output_dir, severity + '.txt'))
            for issue in fpaths_issues:
                print("issue: %s" % (issue))



def main():
    args = arg_parser.parse_args()
    print("ARGS: %s" % args)

    issues_dict = defaultdict(list)
    # Getting iRODS metadata for files and checking before bringing it a "normalized" form:
    # TODO: add the option of getting the metadata as a json from the command line...
    #irods_metadata_dict = {}    # key = filepath, value = metadata (avus + checksum and others)
    reference = args.desired_reference if args.desired_reference else None
    if args.metadata_fetching_strategy == 'fetch_by_metadata':
        irods_metadata_dict = fetch_and_preprocess_irods_metadata_by_metadata(issues_dict, args.irods_zone, reference,
                                                                              args.filter_npg_qc, args.filter_target,
                                                                              args.filter_types, args.study_name,
                                                                              args.study_acc_nr, args.study_internal_id)
    elif args.metadata_fetching_strategy == 'fetch_by_path':
        irods_metadata_dict = fetch_and_preprocess_irods_metadata_by_path(args.fpaths_irods, issues_dict, reference)

    # Getting HEADER metadata:
    header_metadata_dict = fetch_and_preprocess_header_metadata(irods_metadata_dict.keys(), issues_dict)

    # Getting Seqscape metadata:
    seqsc_metadata_dict = fetch_and_preprocess_seqscape_metadata(irods_metadata_dict, issues_dict)

    # Running checks to compare metadata obtained from different sources:
    check_metadata_across_different_sources(irods_metadata_dict, header_metadata_dict, seqsc_metadata_dict, issues_dict)

    # Outputting the CheckResults:
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    present_output(issues_dict, args.output_dir)


main()


# fpath = '/seq/illumina/library_merge/13841100.CCXX.paired310.4199421624/13841100.CCXX.paired310.4199421624.cram'
