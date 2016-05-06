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

This file has been created on Jan 12, 2016.
"""

import config
from typing import Set, Dict
from sequencescape import NamedModel, Sample, Study, Library

from mcheck.metadata.seqscape_metadata.seqscape_meta_provider import SeqscapeRawMetadataProvider
from mcheck.metadata.seqscape_metadata.seqscape_metadata import SeqscapeEntityQueryAndResults, SeqscapeRawMetadata, SeqscapeMetadata
from mcheck.metadata.file_header_metadata.header_meta_provider import SAMFileHeaderMetadataProvider
from mcheck.metadata.irods_metadata.irods_meta_provider import iRODSMetadataProvider
from mcheck.metadata.irods_metadata.irods_file_metadata import IrodsSeqFileMetadata


class IrodsMetadataVsHeaderMetadata:

    pass

    # def compare(self, irods_metadata, header_metadata):
    #     return self._compare_entities(irods_metadata.samples, header_metadata.samples)


class FileMetadataComparison:

    @staticmethod
    def compare_entities(entity_set1: Dict[str, str], entity_set2: Dict[str, str]):
        """
        Compares the entities in 2 different dicts that look like: {'accession_number': {'EGAN00001099700'}, 'name': {'SC_SEPI5488478'}, 'internal_id': {'1582333'}}
        :param entity_set1: dict of key = id_type, value = id_value
        :param entity_set2: dict of key = id_type, value = id_value
        :return:
        """
        for id_type, values in entity_set1.items():
            if values and entity_set2.get(id_type):
                if values != entity_set2.get(id_type):
                    return False
        return True

class BulkMetadataRetrieval:

    @staticmethod
    def fetch_irods_metadata_by_metadata(search_criteria):
        """
        Queries iRODS for all the files that match the search criteria and fetch all the metadata for them.
        :param search_criteria: a dict with: key = search field name, value = search field value
        :return:
        """
        return iRODSMetadataProvider.retrieve_fileinfo_and_metadata_by_metadata(search_criteria)


class FileMetadataRetrieval:

    @staticmethod
    def fetch_seqscape_metadata(samples, libraries, studies):
        raw_metadata = SeqscapeRawMetadataProvider.fetch_raw_metadata(samples, libraries, studies)
        problems = raw_metadata.check_metadata()
        seqsc_metadata = SeqscapeMetadata.from_raw_metadata(raw_metadata)
        return seqsc_metadata, problems

    @staticmethod
    def fetch_header_metadata(fpath):
        header_metadata = SAMFileHeaderMetadataProvider.fetch_metadata(fpath, irods=True)
        problems = header_metadata.check_metadata()
        header_metadata.fix_metadata()
        return header_metadata, problems

    @staticmethod
    def fetch_irods_metadata_by_path(fpath):
        raw_metadata = iRODSMetadataProvider.fetch_raw_metadata(fpath)
        problems = raw_metadata.check_metadata()
        seq_metadata = IrodsSeqFileMetadata.from_raw_metadata(raw_metadata)
        return seq_metadata, problems



