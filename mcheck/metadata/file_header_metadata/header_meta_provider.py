"""
Copyright (C) 2015, 2016  Genome Research Ltd.

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

import mcheck.com.utils as common_utils
from mcheck.metadata.common.identifiers import EntityIdentifier
from mcheck.metadata.file_header_metadata.header_metadata import SAMFileHeaderMetadata

from sam.header_extractor import IrodsSamFileHeaderExtractor, LustreSamFileHeaderExtractor
from sam.header_parser import SAMFileHeaderParser, SAMFileRGTagParser


class SAMFileHeaderMetadataProvider:

    @classmethod
    def fetch_metadata(cls, fpath, irods=False):
        if irods:
            header_as_text = IrodsSamFileHeaderExtractor.extract(fpath)
        else:
            header_as_text = LustreSamFileHeaderExtractor.extract(fpath)
        raw_header = SAMFileHeaderParser.parse(header_as_text)
        rg_tags_parsed = SAMFileRGTagParser.parse(raw_header.rg_tags)
        samples = EntityIdentifier.separate_identifiers_by_type(rg_tags_parsed.samples)
        libraries = EntityIdentifier.separate_identifiers_by_type(rg_tags_parsed.libraries)
        return SAMFileHeaderMetadata(fpath=fpath, samples=samples, libraries=libraries, platforms=rg_tags_parsed.platforms)








