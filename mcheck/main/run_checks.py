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
import json
from collections import defaultdict
from sys import stdin, exit
import logging

from mcheck.com import utils
from mcheck.main import arg_parser
from mcheck.main.input_parser import convert_json_to_baton_objs #parse_data_objects,
from mcheck.results.results_processing import CheckResultsProcessing
from mcheck.checks.mchecks_by_comparison import FileMetadataComparison
from mcheck.checks.mchecks_by_type import MetadataSelfChecks
from mcheck.metadata.irods_metadata.file_metadata import IrodsSeqFileMetadata
from mcheck.results.checks_results import RESULT, CheckResultJSONEncoder

# my_logger = logging.getLogger('MyLogger')
# my_logger.setLevel(logging.DEBUG)


def print_output_as_tsv(check_results_by_path):
    if check_results_by_path:
        print("Fpath\tExecuted\tResult\tErrors\t")
        for fpath, issues in check_results_by_path.items():
            for issue in issues:
                errors = issue.error_message if (issue.error_message or issue.error_message is None) else None
                print(str(fpath) + '\t' + str(issue.check_name) + '\t' + str(issue.executed) + '\t' + str(issue.result) + '\t' + str(errors))


def convert_args_to_search_criteria(filter_by_npg_qc=None, filter_by_target=None, filter_by_file_types=None,
                                match_study_name=None, match_study_acc_nr=None, match_study_id=None):
    search_criteria = []
    if filter_by_npg_qc:
        search_criteria.append(('manual_qc',str(filter_by_npg_qc)))
    else:
        print(
            "WARNING! You haven't filtered on manual_qc field. You will get the report from checking all the data, "
            "no matter if qc pass of fail.")
    if filter_by_target:
        search_criteria.append(('target', str(filter_by_target)))
    else:
        print(
            "WARNING! You haven't filtered by target field. You will get back the report from checking all the data, "
            "no matter if it is the target or not, hence possibly also PhiX")
    if filter_by_file_types:
        search_criteria.append(('type', str(filter_by_file_types)))
    else:
        print("WARNING! You haven't filtered on file type.")

    # Parse input parameters and obtain files+metadata:
    if match_study_name:
        search_criteria.append(('study', str(match_study_name)))
    elif match_study_acc_nr:
        search_criteria.append(('study_accession_number', str(match_study_acc_nr)))
    elif match_study_id:
        search_criteria.append(('study_id', str(match_study_id)))
    return search_criteria


def check_metadata_fetched_by_metadata(filter_npg_qc=None, filter_target=None, file_types=None, study_name=None,
                                     study_acc_nr=None, study_internal_id=None, irods_zone=None, reference=None):
    issues_dict = defaultdict(list)
    search_criteria = convert_args_to_search_criteria(filter_npg_qc, filter_target,
                                                      file_types, study_name,
                                                      study_acc_nr, study_internal_id)
    irods_metadata_dict = MetadataSelfChecks.fetch_and_preprocess_irods_metadata_by_metadata(search_criteria, irods_zone, issues_dict, reference)
    if not irods_metadata_dict:
        print("No irods metadata found. No checks performed.")
        sys.exit(1)
    header_metadata_dict, seqscape_metadata_dict = _search_irods_metadata_in_other_sources_and_check(irods_metadata_dict, issues_dict)
    FileMetadataComparison.check_metadata_across_different_sources(irods_metadata_dict, header_metadata_dict, seqscape_metadata_dict, issues_dict)
    return issues_dict


def check_metadata_fetched_by_path(irods_fpaths, reference=None):
    issues_dict = defaultdict(list)
    irods_metadata_dict = MetadataSelfChecks.fetch_and_preprocess_irods_metadata_by_path(irods_fpaths, issues_dict, reference)
    if not irods_metadata_dict:
        print("No irods metadata found. No checks performed.")
        sys.exit(1)
    header_metadata_dict, seqscape_metadata_dict = _search_irods_metadata_in_other_sources_and_check(irods_metadata_dict, issues_dict)
    FileMetadataComparison.check_metadata_across_different_sources(irods_metadata_dict, header_metadata_dict, seqscape_metadata_dict, issues_dict)
    return issues_dict


def check_metadata_given_as_json_stream(reference=None):
    issues_dict = defaultdict(list)
    json_input_data = stdin.read()
    baton_data_objects_list = convert_json_to_baton_objs(json_input_data)
    irods_metadata_dict = {}
    for data_obj in baton_data_objects_list:
        meta = IrodsSeqFileMetadata.from_baton_wrapper(data_obj)
        issues_dict[meta.fpath].extend(meta.check_metadata(reference))
        irods_metadata_dict[meta.fpath] = meta
    if not irods_metadata_dict:
        print("No irods metadata found. No checks performed.")
        sys.exit(1)
    header_metadata_dict, seqscape_metadata_dict = _search_irods_metadata_in_other_sources_and_check(irods_metadata_dict, issues_dict)
    FileMetadataComparison.check_metadata_across_different_sources(irods_metadata_dict, header_metadata_dict, seqscape_metadata_dict, issues_dict)
    return issues_dict


def _search_irods_metadata_in_other_sources_and_check(irods_metadata_dict, issues_dict):
    header_metadata_dict = MetadataSelfChecks.fetch_and_preprocess_header_metadata(irods_metadata_dict.keys(), issues_dict)
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
        check_results_by_fpath = check_metadata_fetched_by_metadata(filter_npg_qc, filter_target, file_types,
                                                               study_name, study_acc_nr, study_internal_id, irods_zone, reference)
    elif args.metadata_fetching_strategy == 'fetch_by_path':
        check_results_by_fpath = check_metadata_fetched_by_path(irods_fpaths, reference)
    elif args.metadata_fetching_strategy == 'given_by_user':
        check_results_by_fpath = check_metadata_given_as_json_stream(reference)
    else:
        raise ValueError("Fetching strategy not supported")

    if args.json_output:
        check_results_json = json.dumps(check_results_by_fpath, cls=CheckResultJSONEncoder)
        print(check_results_json)
    else:
        print_output_as_tsv(check_results_by_fpath)

    for fpath, check_res in check_results_by_fpath.items():
        for result in check_res:
            if result.result == RESULT.FAILURE:
                exit(1)

if __name__ == '__main__':
    main()

