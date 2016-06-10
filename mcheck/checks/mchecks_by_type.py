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

This file has been created on Jun 10, 2016.
"""

import sys
import os
from collections import  defaultdict
from mcheck.metadata.irods_metadata.irods_meta_provider import iRODSMetadataProvider
from mcheck.metadata.seqscape_metadata.seqscape_meta_provider import SeqscapeRawMetadataProvider
from mcheck.metadata.file_header_metadata.header_meta_provider import SAMFileHeaderMetadataProvider
from mcheck.metadata.seqscape_metadata.seqscape_metadata import SeqscapeMetadata
from mcheck.metadata.irods_metadata.file_metadata import IrodsSeqFileMetadata


class MetadataSelfChecks:

    @staticmethod
    def fetch_and_preprocess_irods_metadata_by_metadata(search_criteria, irods_zone, issues_dict, reference):
        """
        This function takes some filtering/matching criteria for selecting data from iRODS based on metadata.
        The client also passes an issues_dict to this function as parameter, which the current function just needs to
        update with the issues found on the files found in iRODS to match the criteria.
        :param issues_dict: an existing dictionary of issues, to which this function needs to add the issues found
        :param irods_zone: the irods zone where to search for the data matching the criteria given
        :param search_criteria: a dict formed of key= attr name, val = attr value. The operator is by default =.
        :return: a dict of key: fpath, value: the iRODS metadata for that path
        """
        irods_metadata_by_path = {}
        try:
            all_files_metadata_objs_list = iRODSMetadataProvider.retrieve_raw_files_metadata_by_metadata(search_criteria,
                                                                                                         irods_zone)
        except Exception as e:
            print(e)
            sys.exit(1)
        else:
            for raw_metadata in all_files_metadata_objs_list:
                fpath = os.path.join(raw_metadata.dir_path, raw_metadata.fname)
                check_results = raw_metadata.check_metadata()
                file_metadata = IrodsSeqFileMetadata.from_raw_metadata(raw_metadata)
                check_results.extend(file_metadata.check_metadata(reference))
                irods_metadata_by_path[fpath] = file_metadata
                issues_dict[fpath].extend(check_results)
            return irods_metadata_by_path


    @staticmethod
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
                check_results = raw_metadata.check_metadata()
                file_metadata = IrodsSeqFileMetadata.from_raw_metadata(raw_metadata)
                check_results.extend(file_metadata.check_metadata(reference))
                irods_metadata_dict[fpath] = file_metadata
                issues_dict[fpath].extend(check_results)
                return irods_metadata_dict


    @staticmethod
    def fetch_and_preprocess_header_metadata(irods_fpaths, issues_dict):
        header_metadata_dict = {}
        for fpath in irods_fpaths:
            header_metadata = SAMFileHeaderMetadataProvider.fetch_metadata(fpath, irods=True)
            check_results = header_metadata.check_metadata()
            header_metadata.fix_metadata()
            header_metadata_dict[fpath] = header_metadata
            issues_dict[fpath].extend(check_results)
        return header_metadata_dict


    @staticmethod
    def fetch_and_preprocess_seqscape_metadata(irods_metadata_by_path_dict, issues_dict):
        seqsc_metadata_dict = {}
        for fpath, irods_metadata in irods_metadata_by_path_dict.items():
            raw_metadata = SeqscapeRawMetadataProvider.fetch_raw_metadata(irods_metadata.samples, irods_metadata.libraries,
                                                                          irods_metadata.studies)
            check_results = raw_metadata.check_metadata()
            seqsc_metadata = SeqscapeMetadata.from_raw_metadata(raw_metadata)
            issues_dict[fpath].extend(check_results)
            seqsc_metadata_dict[fpath] = seqsc_metadata
        return seqsc_metadata_dict
