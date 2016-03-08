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

from mcheck.metadata.seqscape_metadata.seqscape_meta_provider import SeqscapeRawMetadataProvider
from mcheck.metadata.seqscape_metadata.seqscape_metadata import SeqscapeEntityQueryAndResults, SeqscapeRawMetadata, SeqscapeMetadata

class IrodsMetadataVsHeaderMetadata:

    def compare(self, irods_metadata, header_metadata):
        pass



class Setup:

    def fetch_seqscape_metadata(self, samples, libraries, studies):
        raw_metadata = SeqscapeRawMetadataProvider.fetch_raw_metadata(samples, libraries, studies)
        problems = raw_metadata.check_raw_metadata()
        seqsc_metadata = SeqscapeMetadata.from_raw_metadata(raw_metadata)
        return seqsc_metadata, problems

    def fetch_header_metadata(self):
        pass

    def fetch_irods_metadata(self):
        pass

