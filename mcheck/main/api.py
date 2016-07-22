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

This file has been created on Jul 22, 2016.

API module
==========

This module exposes the functions that can be called for running the metacheck programatically.
Since metacheck is checking the files in IRODS, the checks are built around the way the metadata has been extracted
from iRODS and fed into this software, which is:
- metadata fetched by metacheck, given a file path
- metadata fetched by metacheck, given some metadata to query by iRODS
- metadata given as a stream of json data.
The result of all 3 check functions is the same: a dictionary of path - list of CheckResults.
"""

from mcheck.main.run_checks import check_metadata_given_as_json_stream, check_metadata_fetched_by_path, check_metadata_fetched_by_metadata

def check_metadata_given_as_json_stream(reference=None):
    """
    This function takes in the iRODS metadata as a stream of json data read from stdin and it uses for checking the files.
    :param reference: string that contains the name of the genome reference =>
                      one wants to check if the data has this reference as metadata
    :return: dict of key = string file path, value = list[CheckResult]
    """
    return check_metadata_given_as_json_stream(reference)


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
    return check_metadata_fetched_by_path(irods_fpaths, reference)


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
    return check_metadata_fetched_by_metadata(filter_npg_qc, filter_target, file_types, study_name, study_acc_nr,
                                              study_internal_id, irods_zone, reference)
