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

from mcheck.main import metadata_utils
#from mcheck.irods_baton import baton_wrapper as baton

from mcheck.metadata.irods_metadata.file_metadata import IrodsRawFileMetadata, IrodsSeqFileMetadata

import config
from baton.api import connect_to_irods_with_baton, Connection
from baton.models import IrodsEntity, DataObject, Collection, SpecificQuery, SearchCriterion, ComparisonOperator
from baton.collections import IrodsMetadata



class iRODSMetadataProvider:

    @classmethod
    def fetch_raw_file_metadata_by_path(cls, fpath):
        try:
            connection = connect_to_irods_with_baton(config.BATON_BIN)#, skip_baton_binaries_validation=True)
            baton_file_metadata_as_list = connection.data_object.get_by_path(fpath)
        except Exception as e:
            if str(e).find('KRB_ERROR_ACQUIRING_CREDS') != -1:
                raise OSError("ERROR: you need to log into iRODS and aquire the KERBEROS credentials.") from None
            else:
                raise e from None
        else:
            baton_file_metadata = baton_file_metadata_as_list if baton_file_metadata_as_list else None
            raw_metadata = IrodsRawFileMetadata.from_baton_wrapper(baton_file_metadata)
            return raw_metadata


    @classmethod
    def retrieve_raw_files_metadata_by_metadata(cls, search_criteria_dict, zone=None):
        search_crit_list = []
        for k, v in search_criteria_dict.items():
            search_criterion = SearchCriterion(k, v)
            search_crit_list.append(search_criterion)

        # Getting metadata from iRODS:
        try:
            connection = connect_to_irods_with_baton(config.BATON_BIN)#, skip_baton_binaries_validation=True) # type: Connection
            list_of_data_objs_and_metadata = connection.data_object.get_by_metadata(search_crit_list, zone=zone)
        except RuntimeError as e:
            if str(e).find('KRB_ERROR_ACQUIRING_CREDS') != -1:
                raise OSError("ERROR: you need to log into iRODS and aquire the KERBEROS credentials.") from None
            else:
                raise e from None
        raw_meta_objects = [IrodsRawFileMetadata.from_baton_wrapper(data_obj) for data_obj in list_of_data_objs_and_metadata]
        return raw_meta_objects


# import sys
# #by_path = iRODSMetadataProvider.fetch_raw_file_metadata_by_path('/Sanger1/home/ic4/some_json.txt')
# try:
#     by_path = iRODSMetadataProvider.fetch_raw_file_metadata_by_path('/Sanger1/home/ic4/tox.ini')
#     print("Metadata for file by path %s " % by_path)
# except Exception as e:
#     print(e)
#     sys.exit(1)

#objs = iRODSMetadataProvider.retrieve_raw_files_metadata_by_metadata({'study': 'SCG_sperm'}, zone='seq')
#objs = iRODSMetadataProvider.retrieve_raw_files_metadata_by_metadata({'file_type': 'tox'}, zone='Sanger1')
#print("Objects found by metadata: %s" % str(len(objs)))