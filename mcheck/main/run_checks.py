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
from mcheck.check_names import CHECK_NAMES

my_logger = logging.getLogger('MyLogger')
my_logger.setLevel(logging.DEBUG)

def process_output(issues_by_path, output_dir):
    stats = CheckResultsProcessing.failed_check_results_stats(issues_by_path)
    print("STATS---------------: %s " % stats)
    print("---------- END of STATS -----------------")
    for fpath, issues in issues_by_path.items():
        sorted_by_executed = CheckResultsProcessing.group_by_executed(issues)
        sorted_by_result = CheckResultsProcessing.group_by_result(sorted_by_executed[True])
        sorted_by_severity = CheckResultsProcessing.group_by_severity(sorted_by_result[RESULT.FAILURE])
        for severity, failure_issues in sorted_by_severity.items():
            utils.write_list_to_file(failure_issues, os.path.join(output_dir, severity+'.txt'), fpath)
        utils.write_list_to_file(issues, os.path.join(output_dir, 'all_issues.txt'), fpath)
    print("FAILED---------")
    utils.write_dict_to_file(stats, os.path.join(output_dir, 'stats.txt'))
    for failure in sorted_by_result[RESULT.FAILURE]:
        print(failure)



def process_output_and_print(issues_by_path, output_dir):
    for fpath, file_issues in issues_by_path.items():
        print("FPATH: %s and type of issues container: %s" % (fpath, str(type(file_issues))))
        for issue in file_issues:
            print("Issue - type: %s and value: %s" % (str(type(issue)), issue))


        sorted_by_exec = CheckResultsProcessing.group_by_executed(file_issues)
        # print("Sorted by exec = True:")
        # for check in  sorted_by_exec[True]:
        #     print(check)
        print("Sorted by exec = False:")
        for check in sorted_by_exec[False]:
            print(check)
        sorted_by_severity = CheckResultsProcessing.group_by_severity(sorted_by_exec[True])
        print("SORTED BY SEVERITY::::::::::")
        for severity, fpaths_issues in sorted_by_severity.items():
            print("SEVERITY: %s" % severity)
            utils.write_list_to_file(fpaths_issues, os.path.join(output_dir, severity + '.txt'), fpath)
            for issue in fpaths_issues:
                if issue.result == RESULT.FAILURE:
                    print("issue: %s" % (issue))

        print("FAILED-------------")
        sorted_by_result = CheckResultsProcessing.group_by_result(file_issues)
        for issue in sorted_by_result[RESULT.FAILURE]:
            print(issue)


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
        #for ftype in filter_by_file_types:
        search_criteria.append(('type', str(filter_by_file_types)))
    else:
        print("WARNING! You haven't filtered on file type.")

    # Parse input parameters and obtain files+metadata:
    if match_study_name:
        search_criteria.append(('study', str(match_study_name)))
    elif match_study_acc_nr:
        search_criteria.append(('study_accession_number', str(match_study_acc_nr)))
    elif match_study_id:
        search_criteria.append(('study_internal_id', str(match_study_id)))
    return search_criteria

def fetch_irods_metadata_by_metadata(issues_dict, filter_npg_qc=None, filter_target=None, file_types=None, study_name=None,
                                     study_acc_nr=None, study_internal_id=None, irods_zone=None, reference=None):
    search_criteria = convert_args_to_search_criteria(filter_npg_qc, filter_target,
                                                      file_types, study_name,
                                                      study_acc_nr, study_internal_id)
    irods_metadata_dict = MetadataSelfChecks.fetch_and_preprocess_irods_metadata_by_metadata(search_criteria, irods_zone, issues_dict, reference)
    return irods_metadata_dict


def fetch_irods_metadata_by_path(issues_dict, irods_fpaths, reference):
    return MetadataSelfChecks.fetch_and_preprocess_irods_metadata_by_path(irods_fpaths, issues_dict, reference)


def fetch_irods_metadata_from_json(issues_dict, json_data_objects, reference=None):
    baton_data_objects_list = convert_json_to_baton_objs(json_data_objects)
    irods_metadata_dict = {}
    for data_obj in baton_data_objects_list:
        meta = IrodsSeqFileMetadata.from_baton_wrapper(data_obj)
        issues_dict[meta.fpath].extend(meta.check_metadata(reference))
        irods_metadata_dict[meta.fpath] = meta
    return irods_metadata_dict



def check_metadata(metadata_fetching_strategy, reference=None, filter_npg_qc=None, filter_target=None, file_types=None,
                   study_name=None, study_acc_nr=None, study_internal_id=None, irods_fpaths=None, irods_zone=None):
    issues_dict = defaultdict(list)
    if metadata_fetching_strategy == 'fetch_by_metadata':
        irods_metadata_dict = fetch_irods_metadata_by_metadata(issues_dict, filter_npg_qc, filter_target, file_types,
                                                               study_name, study_acc_nr, study_internal_id, irods_zone, reference)
    elif metadata_fetching_strategy == 'fetch_by_path':
        irods_metadata_dict = fetch_irods_metadata_by_path(issues_dict, irods_fpaths, reference)
    elif metadata_fetching_strategy == 'given_by_user':
        input_data_objects = stdin.read()
        irods_metadata_dict = fetch_irods_metadata_from_json(issues_dict, input_data_objects, reference)
    else:
        raise ValueError("Fetching strategy not supported")

    # Getting HEADER metadata:
    header_metadata_dict = MetadataSelfChecks.fetch_and_preprocess_header_metadata(irods_metadata_dict.keys(), issues_dict)

    # Getting Seqscape metadata:
    seqsc_metadata_dict = MetadataSelfChecks.fetch_and_preprocess_seqscape_metadata(irods_metadata_dict, issues_dict)

    # Running checks to compare metadata obtained from different sources:
    FileMetadataComparison.check_metadata_across_different_sources(irods_metadata_dict, header_metadata_dict, seqsc_metadata_dict, issues_dict)

    return issues_dict

def main():
    args = arg_parser.parse_args()
    print("ARGS: %s" % args)
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
        fpaths_irods = args.fpaths_irods
    except AttributeError:
        fpaths_irods = None

    try:
        irods_zone = args.irods_zone
    except AttributeError:
        irods_zone = None

    try:
        reference = args.desired_reference
    except AttributeError:
        reference = None

    check_results_dict = check_metadata(args.metadata_fetching_strategy, reference, filter_npg_qc,
                                 filter_target, file_types, study_name, study_acc_nr,
                                 study_internal_id, fpaths_irods, irods_zone)


    # OUTPUTTING THE CHECK RESULTS
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    process_output(check_results_dict, args.output_dir)


    import json
    if args.json_output:
        check_results_json = json.dumps(check_results_dict, cls=CheckResultJSONEncoder)
        print(check_results_json)


    for fpath, check_res in check_results_dict.items():
        for result in check_res:
            if result.result == RESULT.FAILURE:
                exit(1)




if __name__ == '__main__':
    main()


# fpath = '/seq/illumina/library_merge/13841100.CCXX.paired310.4199421624/13841100.CCXX.paired310.4199421624.cram'
# python mcheck/main/run_checks.py fetch_by_metadata --output_dir /lustre/scratch113/teams/hgi/users/ic4/mercury/meta-checks/testing-outputs/test/ --study_name "SEQCAP_WGS_GDAP_AADM" --file_types cram --filter_npg_qc 1 --filter_target 1 --irods_zone seq
# (ENV) mercury@hgi-serapis-farm3-dev:/nfs/users/nfs_i/ic4/Projects/python3/meta-check$ bsub  -G hgi -q long -R"select[mem>4000] rusage[mem=4000]" -M4000 -o  /lustre/scratch113/teams/hgi/users/ic4/mercury/meta-checks/testing-outputs/interval-all.out "python mcheck/main/run_checks.py fetch_by_metadata --output_dir /lustre/scratch113/teams/hgi/users/ic4/mercury/meta-checks/testing-outputs/interval-all --study_name 'IHTP_WGS_INTERVAL Cohort (15x)' --file_types cram --filter_npg_qc 1 --irods_zone seq"
# Job <7876533> is submitted to queue <long>.
# (ENV) mercury@hgi-serapis-farm3-dev:/nfs/users/nfs_i/ic4/Projects/python3/meta-check$ bsub  -G hgi -q long -R"select[mem>4000] rusage[mem=4000]" -M4000 -o  /lustre/scratch113/teams/hgi/users/ic4/mercury/meta-checks/testing-outputs/helic-manolis.out "python mcheck/main/run_checks.py fetch_by_metadata --output_dir /lustre/scratch113/teams/hgi/users/ic4/mercury/meta-checks/testing-outputs/helic-manolis --study_name 'IHTP_MWGS_HELICMANOLIS' --file_types cram --filter_npg_qc 1 --filter_target library --irods_zone seq"
# Job <7876571> is submitted to queue <long>.
# (ENV) mercury@hgi-serapis-farm3-dev:/nfs/users/nfs_i/ic4/Projects/python3/meta-check$ bsub  -G hgi -q long -R"select[mem>4000] rusage[mem=4000]" -M4000 -o  /lustre/scratch113/teams/hgi/users/ic4/mercury/meta-checks/testing-outputs/helic-pomak.out "python mcheck/main/run_checks.py fetch_by_metadata --output_dir /lustre/scratch113/teams/hgi/users/ic4/mercury/meta-checks/testing-outputs/helic-pomak --study_name 'IHTP_MWGS_HELICPOMAK' --file_types cram --filter_npg_qc 1 --filter_target library --irods_zone seq"
# Job <7876591> is submitted to queue <long>.
# bsub  -G hgi -q long -R"select[mem>4000] rusage[mem=4000]" -M4000 -o  /lustre/scratch113/teams/hgi/users/ic4/mercury/meta-checks/testing-outputs/helic-manolis-nonlibrary.out "python mcheck/main/run_checks.py fetch_by_metadata --output_dir /lustre/scratch113/teams/hgi/users/ic4/mercury/meta-checks/testing-outputs/helic-manolis-nonlibrary --study_name 'IHTP_MWGS_HELICMANOLIS' --file_types cram --filter_npg_qc 1 --filter_target 1 --irods_zone seq"
#
