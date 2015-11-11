"""
Copyright (C) 2014  Genome Research Ltd.

Author: Irina Colgiu <ic4@sanger.ac.uk>

This program is part of metadata-check.

metadata-check is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.


This is the API exposed for the whole package, this should encompass all the functionality that a user wants
from an iRODS API wrapper.

This file has been created on Oct 24, 2014
"""

from irods import icommands_wrapper as irods_api
from irods import exceptions as irods_exc
from irods import data_types as irods_types


class iRODSAPI:


    @classmethod
    def _map_irods_exc_on_backend_exc(cls, irods_exc):
        return irods_exc


    @classmethod
    def list_dir(cls, path):
        try:
            return irods_api.iRODSListOperations.list_files_in_coll(path)
        except irods_exc.iLSException as e:
            exc = cls._map_irods_exc_on_backend_exc(e)
            raise exc
            

    @classmethod
    def checksum_file(cls, path):
        ''' This method checksums a file and returns the checksum.
            Parameters
            ----------
            path : str
                The path to the file to be checksum-ed
            Returns
            -------
            ChecksumResult
                The checksum result containing the checksum
            Raises
            ------
            BackendException
        '''
        try:
            return irods_api.iRODSChecksumOperations.run_file_checksum_across_all_replicas(path)
        except irods_exc.iChksumException as e:
            exc = cls._map_irods_exc_on_backend_exc(e)
            raise exc
        
    @classmethod
    def get_file_checksum(cls, path):
        """ This method checksums a file and returns the checksum.
            Parameters
            ----------
            path : str
                The path to the file to be checksum-ed
            Returns
            -------
            ChecksumResult
                The checksum result containing the checksum
            Raises
            ------
            BackendException
        """
        try:
            return irods_api.iRODSChecksumOperations.run_file_checksum(path)
        except irods_exc.iChksumException as e:
            exc = cls._map_irods_exc_on_backend_exc(e)
            raise exc
    

    @classmethod
    def retrieve_metadata_for_file(cls, path):
        return irods_api.iRODSMetaListOperations.get_metadata(path)


    @classmethod
    def search_files_by_metadata(cls, avu_dict):
        return irods_api.iRODSMetaQueryOperations.query_by_metadata(avu_dict)


    @classmethod
    def modify_metadata_avu(cls, path, old_avu, new_avu):
        """ This method modifies one AVU, but removing the old one and adding the new one.
            Parameters
            ----------
            path : str
                The path to the file in iRODS
            old_avu : data_types.MetaAVU
                The old avu, to be removed
            new_avu : data_types.MetaAVU
                The new avu to be added
            Returns
            -------
            bool
        """
        irods_api.iRODSMetaRMOperations.remove_avu(path, old_avu)
        irods_api.iRODSMetaAddOperations.add_avu(path, new_avu)
        return True

    @classmethod
    def add_metadata_avu(cls, path, avu):
        return irods_api.iRODSMetaAddOperations.add_avu(path, avu)

    @classmethod
    def remove_metadata_avu(cls, path, avu):
        return irods_api.iRODSMetaRMOperations.remove_avu(path, avu)