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

import sys
from collections import defaultdict
from sys import stdin, exit

from mcheck.results.checks_results import RESULT
from mcheck.metadata.irods_metadata.irods_meta_provider import iRODSMetadataProvider
from mcheck.main import arg_parser
from mcheck.main.input_parser import convert_json_to_baton_objs
from mcheck.checks.mchecks_by_comparison import FileMetadataComparison
from mcheck.checks.mchecks_by_type import MetadataSelfChecks
from mcheck.metadata.irods_metadata.file_metadata import IrodsSeqFileMetadata
from mcheck.main.output_formatter import format_output_as_json, format_output_as_tsv

# import logging
# my_logger = logging.getLogger('MyLogger')
# my_logger.setLevel(logging.DEBUG)



def check_metadata_fetched_by_metadata(filter_npg_qc=None, filter_target=None, file_types=None, study_name=None,
                                       study_acc_nr=None, study_internal_id=None, irods_zone=None, reference=None):
    """
    This function fetches the iRODS metadata by querying iRODS by other metadata. It takes as parameters a set of optional
    querying fields and returns a dict where key = file path checked, value = a list of CheckResult objects corresponding
    to the checks performed.
    :param filter_npg_qc: the field in iRODS that applies a filter on QC pass/fail on the data it fetches
    :param filter_target: the field in iRODS that applies a filter on target field in iRODS
    :param file_types: the field in iRODS that applies a filter on the type of files
    :param study_name: the study name that we want to fetch data for
    :param study_acc_nr: the study accession number that we want to fetch data for
    :param study_internal_id: the study internal id that we want to fetch data for
    :param irods_zone: the zone where the query should be run
    :param reference: the genome reference => one wants to check if the data has this reference as metadata
    :return: dict of key = string file path, value = list[CheckResult]
    """
    check_results_by_path = defaultdict(list)
    search_criteria = iRODSMetadataProvider.convert_to_irods_fields(filter_npg_qc, filter_target,
                                                                    file_types, study_name,
                                                                    study_acc_nr, study_internal_id)
    irods_metadata_dict = MetadataSelfChecks.fetch_and_preprocess_irods_metadata_by_metadata(search_criteria,
                                                                                             irods_zone,
                                                                                             check_results_by_path,
                                                                                             reference)
    if not irods_metadata_dict:
        print("No irods metadata found. No checks performed.")
        sys.exit(1)
    header_metadata_dict, seqscape_metadata_dict = _fetch_irods_metadata_from_other_sources_and_check(
        irods_metadata_dict, check_results_by_path)
    FileMetadataComparison.check_metadata_across_different_sources(irods_metadata_dict, header_metadata_dict,
                                                                   seqscape_metadata_dict, check_results_by_path)
    return check_results_by_path


def check_metadata_fetched_by_path(irods_fpaths, reference=None):
    """
    This function fetches the iRODS metadata by file path. It takes as parameter a list of file paths and queries
    iRODS for metadata for each of the paths taken as parameter. It returns a dict where
    key = file path checked, value = a list of CheckResult objects corresponding to the checks performed.
    :param irods_fpaths: list of strings corresponding to iRODS file paths
    :param reference: string that contains the name of the genome reference =>
            one wants to check if the data has this reference as metadata
    :return: dict of key = string file path, value = list[CheckResult]
    """
    check_results_by_path = defaultdict(list)
    irods_metadata_dict = MetadataSelfChecks.fetch_and_preprocess_irods_metadata_by_path(irods_fpaths,
                                                                                         check_results_by_path,
                                                                                         reference)
    if not irods_metadata_dict:
        print("No irods metadata found. No checks performed.")
        sys.exit(1)
    header_metadata_dict, seqscape_metadata_dict = _fetch_irods_metadata_from_other_sources_and_check(
        irods_metadata_dict, check_results_by_path)
    FileMetadataComparison.check_metadata_across_different_sources(irods_metadata_dict, header_metadata_dict,
                                                                   seqscape_metadata_dict, check_results_by_path)
    return check_results_by_path


def check_metadata_given_as_json_stream(reference=None):
    """
    This function takes in the iRODS metadata as a stream of json data read from stdin and it uses for checking the files.
    :param reference: string that contains the name of the genome reference =>
                      one wants to check if the data has this reference as metadata
    :return: dict of key = string file path, value = list[CheckResult]
    """
    check_results_by_path = defaultdict(list)
    json_input_data = stdin.read()
    baton_data_objects_list = convert_json_to_baton_objs(json_input_data)
    irods_metadata_dict = {}
    for data_obj in baton_data_objects_list:
        meta = IrodsSeqFileMetadata.from_baton_wrapper(data_obj)
        check_results_by_path[meta.fpath].extend(meta.check_metadata(reference))
        irods_metadata_dict[meta.fpath] = meta
    if not irods_metadata_dict:
        print("No irods metadata found. No checks performed.")
        sys.exit(1)
    header_metadata_dict, seqscape_metadata_dict = _fetch_irods_metadata_from_other_sources_and_check(
        irods_metadata_dict, check_results_by_path)
    FileMetadataComparison.check_metadata_across_different_sources(irods_metadata_dict, header_metadata_dict,
                                                                   seqscape_metadata_dict, check_results_by_path)
    return check_results_by_path


def _fetch_irods_metadata_from_other_sources_and_check(irods_metadata_dict, issues_dict):
    header_metadata_dict = MetadataSelfChecks.fetch_and_preprocess_header_metadata(irods_metadata_dict.keys(),
                                                                                   issues_dict)
    seqsc_metadata_dict = MetadataSelfChecks.fetch_and_preprocess_seqscape_metadata(irods_metadata_dict, issues_dict)
    return header_metadata_dict, seqsc_metadata_dict


def main():
    args = arg_parser.parse_args()
    try:
        filter_npg_qc = args.filter_npg_qc
    except AttributeError:
        filter_npg_qc = None

    try:
        filter_target = args.filter_target
    except AttributeError:
        filter_target = None
    try:
        file_types = args.file_types
    except AttributeError:
        file_types = None

    try:
        study_name = args.study_name
    except AttributeError:
        study_name = None

    try:
        study_acc_nr = args.study_acc_nr
    except AttributeError:
        study_acc_nr = None

    try:
        study_internal_id = args.study_internal_id
    except AttributeError:
        study_internal_id = None

    try:
        irods_fpaths = args.irods_fpaths
    except AttributeError:
        irods_fpaths = None

    try:
        irods_zone = args.irods_zone
    except AttributeError:
        irods_zone = None

    try:
        reference = args.desired_reference
    except AttributeError:
        reference = None

    if args.metadata_fetching_strategy == 'fetch_by_metadata':
        if not file_types:
            print(
                "WARNING! You haven't filtered on file type. The result will contain both BAMs and CRAMs, possibly other types of file as well.")
        if not filter_target:
            print(
                "WARNING! You haven't filtered by target field. You will get back the report from checking all the data, "
                "no matter if it is the target or not, hence possibly also PhiX")
        if not filter_npg_qc:
            print(
                "WARNING! You haven't filtered on manual_qc field. You will get the report from checking all the data, "
                "no matter if qc pass of fail.")

    if args.metadata_fetching_strategy == 'fetch_by_metadata':
        check_results_by_fpath = check_metadata_fetched_by_metadata(filter_npg_qc, filter_target, file_types,
                                                                    study_name, study_acc_nr, study_internal_id,
                                                                    irods_zone, reference)
    elif args.metadata_fetching_strategy == 'fetch_by_path':
        check_results_by_fpath = check_metadata_fetched_by_path(irods_fpaths, reference)
    elif args.metadata_fetching_strategy == 'given_at_stdin':
        check_results_by_fpath = check_metadata_given_as_json_stream(reference)
    else:
        raise ValueError("Fetching strategy not supported")

    if args.json_output:
        check_results_as_json = format_output_as_json(check_results_by_fpath)
        print(check_results_as_json)
    else:
        result_as_tsv_string = format_output_as_tsv(check_results_by_fpath)
        print(result_as_tsv_string)

    for fpath, check_res in check_results_by_fpath.items():
        for result in check_res:
            if result.result == RESULT.FAILURE:
                exit(1)

if __name__ == '__main__':
    main()

