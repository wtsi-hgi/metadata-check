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

This file has been created on Apr 12, 2016.
"""

import unittest
from mcheck.metadata.file_header_metadata.header_meta_provider import SAMFileHeaderMetadataProvider
from mcheck.metadata.file_header_metadata.header_metadata import SAMFileHeaderMetadata

@unittest.skip
class TestSAMFileHeaderMetadataProvider(unittest.TestCase):

    def test_fetch(self):
        fpath = 'test_data/A.bam'
        result = SAMFileHeaderMetadataProvider.fetch_metadata(fpath)
        expected = SAMFileHeaderMetadata(fpath='test_data/A.bam', fname='A.bam', samples={'name': set(['A_J']), 'internal_id': set(), 'accession_number': set()},
                                         platforms={'SLX'}, libraries={'name': set(['A_J_SLX_500_HC_2', 'A_J_SLX_200_NOPCR_3',
                                                                                 'A_J_SLX_200_NOPCR_2', 'A_J_SLX_200_NOPCR_2',
                                                                                 'A_J_SLX_200_NOPCR_3', 'A_J_SLX_300_DSS_1',
                                                                                 'A_J_SLX_300_DSS_2', 'A_J_SLX_300_DSS_3',
                                                                                 'A_J_SLX_500_DSS_1', 'A_J_SLX_500_DSS_2',
                                                                                 'A_J_SLX_500_DSS_3']), 'internal_id': set(), 'accession_number': set()})
        self.assertEqual(result, expected)


