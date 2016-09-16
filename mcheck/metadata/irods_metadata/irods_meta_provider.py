"""
Copyright (C) 2015  Genome Research Ltd.

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

This file has been created on Nov 16, 2015.
"""

from mcheck.metadata.irods_metadata.file_metadata import IrodsRawFileMetadata

import config
from baton.api import connect_to_irods_with_baton
from baton.models import SearchCriterion
from typing import List, Tuple


class iRODSMetadataProvider:

    @classmethod
    def convert_to_irods_fields(cls, filter_by_npg_qc=None, filter_by_target=None, filter_by_file_types=None,
                                match_study_name=None, match_study_acc_nr=None, match_study_id=None):
        search_criteria = []
        if filter_by_npg_qc:
            search_criteria.append(('manual_qc', str(filter_by_npg_qc)))
        if filter_by_target:
            search_criteria.append(('target', str(filter_by_target)))
        if filter_by_file_types:
            search_criteria.append(('type', str(filter_by_file_types)))
        if match_study_name:
            search_criteria.append(('study', str(match_study_name)))
        elif match_study_acc_nr:
            search_criteria.append(('study_accession_number', str(match_study_acc_nr)))
        elif match_study_id:
            search_criteria.append(('study_id', str(match_study_id)))
        return search_criteria


    @classmethod
    def fetch_raw_file_metadata_by_path(cls, fpath):
        try:
            connection = connect_to_irods_with_baton(config.BATON_BIN)#, skip_baton_binaries_validation=True)
            data_object = connection.data_object.get_by_path(fpath)
        except Exception as e:
            if str(e).find('KRB_ERROR_ACQUIRING_CREDS') != -1:
                raise OSError("ERROR: you need to log into iRODS and aquire the KERBEROS credentials.") from None
            else:
                raise e from None
        else:
            if data_object:
                raw_metadata = IrodsRawFileMetadata.from_baton_wrapper(data_object)
                return raw_metadata
            return None


    @classmethod
    def retrieve_raw_files_metadata_by_metadata(cls, search_criteria_list: List[Tuple], zone=None):
        search_criteria_objs = []
        for k, v in search_criteria_list:
            search_criterion = SearchCriterion(k, v)
            search_criteria_objs.append(search_criterion)

        # Getting metadata from iRODS:
        try:
            connection = connect_to_irods_with_baton(config.BATON_BIN)  # skip_baton_binaries_validation=True) # type: Connection
            list_of_data_objs_and_metadata = connection.data_object.get_by_metadata(search_criteria_objs, zone=zone)
        except RuntimeError as e:
            if str(e).find('KRB_ERROR_ACQUIRING_CREDS') != -1:
                raise OSError("ERROR: you need to log into iRODS and aquire the KERBEROS credentials.") from None
            else:
                raise e from None
        raw_meta_objects = [IrodsRawFileMetadata.from_baton_wrapper(data_obj) for data_obj in list_of_data_objs_and_metadata]
        return raw_meta_objects

