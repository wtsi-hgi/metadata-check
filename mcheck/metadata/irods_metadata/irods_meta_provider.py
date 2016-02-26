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
from mcheck.irods_baton import baton_wrapper as baton


class iRODSMetadataProvider:

    def get_files_and_metadata_by_metadata(search_criteria):
        metaquery_results = baton.BatonAPI.query_by_metadata_and_get_results_as_json(search_criteria) # avu_tuple_list
        fpaths_checksum_and_avus = metadata_utils.iRODSBatonUtils.from_metaquery_results_to_fpaths_and_avus(metaquery_results)  # this is a dict of key = fpath, value = dict({'avus':[], 'checksum':str})
        print("NR OF FPATHS FOUND: " + str(len(fpaths_checksum_and_avus)))
        return fpaths_checksum_and_avus


    def get_files_and_metadata_by_fpath(fpaths):
        fpaths_checksum_and_avus = baton.BatonAPI.get_all_files_metadata(fpaths)
        fpaths_checksum_and_avus = [_f for _f in fpaths_checksum_and_avus.split('\n') if _f]
        #fpaths_checksum_and_avus = metadata_utils.iRODSBatonUtils.from_metaquery_results_to_fpaths_and_avus(fpaths_checksum_and_avus)  # this is a dict of key = fpath, value = dict({'avus':[], 'checksum':str})
        fpaths_checksum_and_avus = metadata_utils.iRODSBatonUtils.from_multi_metaquery_results_to_fpaths_and_avus(fpaths_checksum_and_avus)
        return fpaths_checksum_and_avus

    @classmethod
    def retrieve_metadata_by_file_path(cls, fpath):
        pass

    @classmethod
    def retrieve_metadata_by_metadata(cls, metadata):
        pass



