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


from sys import exit
from mcheck.main.api import check_metadata_fetched_by_metadata, check_metadata_fetched_by_path, check_metadata_given_as_json_stream
from mcheck.check_names import CHECK_NAMES
from mcheck.results.checks_results import RESULT
from mcheck.main import arg_parser
from mcheck.main.output_formatter import format_output_as_json, format_output_as_tsv

# import logging
# my_logger = logging.getLogger('MyLogger')
# my_logger.setLevel(logging.DEBUG)


def decide_exit_status(check_results_by_path):
    exit_status = 0
    irrelevant = [CHECK_NAMES.check_for_samples_in_more_studies, CHECK_NAMES.check_more_than_one_replica]
    for fpath, check_results in check_results_by_path.items():
        for check_result in check_results:
            if check_result.result == RESULT.FAILURE and check_result.check_name not in irrelevant:
                exit_status = 1
    return exit_status


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

    exit(decide_exit_status(check_results_by_fpath))

if __name__ == '__main__':
    main()

