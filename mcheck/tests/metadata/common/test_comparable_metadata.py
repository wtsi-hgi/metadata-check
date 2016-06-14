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

This file has been created on Jun 14, 2016.
"""

import unittest

from mcheck.metadata.file_header_metadata.header_metadata import SAMFileHeaderMetadata
from mcheck.metadata.irods_metadata.file_metadata import IrodsSeqFileMetadata
from mcheck.metadata.seqscape_metadata.seqscape_metadata import SeqscapeMetadata

class ComparableMetadataTests(unittest.TestCase):


    def test_find_differences_when_there_are_diffs_h_vs_ss1(self):
        header_metadata = SAMFileHeaderMetadata('/seq/123.bam', '123/bam', samples={'name': set(['S1'])}, libraries={}, studies={})
        seqscape_metadata = SeqscapeMetadata(samples={'name': set(['S9'])}, libraries={}, studies={})
        result = header_metadata.difference(seqscape_metadata)
        self.assertEqual(result,{'samples': {'name': set(['S1'])}})


    def test_find_differences_when_there_are_diffs_h_vs_ss2(self):
        header_metadata = SAMFileHeaderMetadata('/seq/123.bam', '123/bam', samples={'name': set(['S9'])}, libraries={}, studies={})
        seqscape_metadata = SeqscapeMetadata(samples={'name': set(['S1'])}, libraries={}, studies={})
        result = header_metadata.difference(seqscape_metadata)
        self.assertEqual(result,{'samples': {'name': set(['S9'])}})


    def test_find_differences_when_there_are_diff_type_ids_h_vs_ss(self):
        header_metadata = SAMFileHeaderMetadata('/seq/123.bam', '123/bam', samples={'name': set(['S1']), 'accession_number': set(['Acc1'])}, libraries={}, studies={})
        seqscape_metadata = SeqscapeMetadata(samples={'name': set(['S1'])}, libraries={}, studies={})
        result = header_metadata.difference(seqscape_metadata)
        self.assertEqual(result, {})


    def test_find_differences_when_many_diffs_h_vs_ss(self):
        header_metadata = SAMFileHeaderMetadata('/seq/123.bam', '123/bam',
                                                samples={'name': set(['S9']), 'accession_number': set(['Acc9'])},
                                                libraries={'internal_id': set(['123'])}, studies={})
        seqscape_metadata = SeqscapeMetadata(samples={'name': set(['S1'])}, libraries={'internal_id': set(['444'])}, studies={})
        result = header_metadata.difference(seqscape_metadata)
        self.assertEqual(result,{'samples': {'name': set(['S9'])}, 'libraries': {'internal_id': set(['123'])}})


    def test_find_differences_when_no_diffs_h_vs_ss(self):
        header_metadata = SAMFileHeaderMetadata('/seq/123.bam', '123/bam',
                                                samples={'name': set(['S9']), 'accession_number': set(['Acc9'])},
                                                libraries={'internal_id': set(['123'])}, studies={})
        seqscape_metadata = SeqscapeMetadata(samples={'name': set(['S9']), 'accession_number': set(['Acc9'])},
                                             libraries={'internal_id': set(['123'])}, studies={})
        result = header_metadata.difference(seqscape_metadata)
        self.assertEqual(result,{})


    def test_find_differences_when_no_diffs_i_vs_h(self):
        irods_metadata = IrodsSeqFileMetadata('/seq/123.bam',
                                              samples={'name': set(['S1']), 'accession_number': set(), 'internal_id': set()},
                                              libraries={}, studies={})
        header_metadata = SAMFileHeaderMetadata('/seq/123.bam', '123/bam',
                                                samples={'name': set(['S1']), 'accession_number' : set(), 'internal_id': set()},
                                                libraries={}, studies={})
        result = irods_metadata.difference(header_metadata)
        self.assertDictEqual(result, {})


    def test_find_differences_when_diff_id_types_i_vs_h(self):
        irods_metadata = IrodsSeqFileMetadata('/seq/123.bam',
                                              samples={'name': set(['S1']), 'accession_number': set(['EGA1']), 'internal_id': set(['1'])},
                                              libraries={'name': set(['123']), 'internal_id': set(['123'])},
                                              studies={'name': set(["Crohns disease"]), 'accession_number': set(['EGAS4']), 'internal_id': set(['4'])})
        header_metadata = SAMFileHeaderMetadata('/seq/123.bam', '123/bam',
                                                samples={'name': set(['S1']), 'accession_number' : set(), 'internal_id': set()},
                                                libraries={'internal_id': set(['123'])}, studies={})
        result = irods_metadata.difference(header_metadata)
        self.assertDictEqual(result, {})


    def test_find_differences_when_diffs_i_vs_h(self):
        irods_metadata = IrodsSeqFileMetadata('/seq/123.bam',
                                              samples={'name': set(['S1']), 'accession_number': set(['EGA1']), 'internal_id': set(['1'])},
                                              libraries={'name': set(['123']), 'internal_id': set(['123'])},
                                              studies={'name': set(["Crohns disease"]), 'accession_number': set(['EGAS4']), 'internal_id': set(['4'])})
        header_metadata = SAMFileHeaderMetadata('/seq/123.bam', '123/bam',
                                                samples={'name': set(['S100']), 'accession_number' : set(), 'internal_id': set()},
                                                libraries={'internal_id': set(['123'])}, studies={})
        result = irods_metadata.difference(header_metadata)
        self.assertDictEqual(result, {'samples': {'name': set(['S1'])}})

    def test_find_differences_when_diffs_h_vs_i(self):
        irods_metadata = IrodsSeqFileMetadata('/seq/123.bam',
                                              samples={'name': set(['S1']), 'accession_number': set(['EGA1']), 'internal_id': set(['1'])},
                                              libraries={'name': set(['123']), 'internal_id': set(['123'])},
                                              studies={'name': set(["Crohns disease"]), 'accession_number': set(['EGAS4']), 'internal_id': set(['4'])})
        header_metadata = SAMFileHeaderMetadata('/seq/123.bam', '123/bam',
                                                samples={'name': set(['S100']), 'accession_number' : set(), 'internal_id': set()},
                                                libraries={'internal_id': set(['123'])}, studies={})
        result = header_metadata.difference(irods_metadata)
        self.assertDictEqual(result, {'samples': {'name': set(['S100'])}})


    def test_find_differences_when_not_the_right_type(self):
        irods_metadata = IrodsSeqFileMetadata('/seq/123.bam',
                                              samples={'name': set(['S1']), 'accession_number': set(), 'internal_id': set()},
                                              libraries={}, studies={})
        self.assertRaises(TypeError, irods_metadata.difference, [1,2,3])

