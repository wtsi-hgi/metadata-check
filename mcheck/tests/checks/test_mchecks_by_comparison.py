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
import unittest

from collections import defaultdict
from mcheck.metadata.irods_metadata.file_metadata import IrodsSeqFileMetadata
from mcheck.metadata.file_header_metadata.header_metadata import SAMFileHeaderMetadata
from mcheck.metadata.seqscape_metadata.seqscape_metadata import SeqscapeMetadata
from mcheck.checks.mchecks_by_comparison import FileMetadataComparison
from mcheck.results.checks_results import RESULT

class FileMetadataComparisonTest(unittest.TestCase):

    def test_find_differences_when_there_are_diffs_1(self):
        header_metadata = SAMFileHeaderMetadata('/seq/123.bam', '123/bam', samples={'name': set(['S1'])}, libraries={}, studies={})
        seqscape_metadata = SeqscapeMetadata(samples={'name': set(['S9'])}, libraries={}, studies={})
        result = FileMetadataComparison._find_differences(header_metadata, seqscape_metadata, ['samples'])
        self.assertEqual(result,{'samples': {'name': set(['S1'])}})

    def test_find_differences_when_there_are_diffs2(self):
        header_metadata = SAMFileHeaderMetadata('/seq/123.bam', '123/bam', samples={'name': set(['S9'])}, libraries={}, studies={})
        seqscape_metadata = SeqscapeMetadata(samples={'name': set(['S1'])}, libraries={}, studies={})
        result = FileMetadataComparison._find_differences(header_metadata, seqscape_metadata, ['samples'])
        self.assertEqual(result,{'samples': {'name': set(['S9'])}})


    def test_find_differences_when_there_are_diff_type_ids(self):
        header_metadata = SAMFileHeaderMetadata('/seq/123.bam', '123/bam', samples={'name': set(['S1']), 'accession_number': set(['Acc1'])}, libraries={}, studies={})
        seqscape_metadata = SeqscapeMetadata(samples={'name': set(['S1'])}, libraries={}, studies={})
        result = FileMetadataComparison._find_differences(header_metadata, seqscape_metadata, ['samples'])
        self.assertEqual(result, {})

    def test_find_differences_when_many_diffs(self):
        header_metadata = SAMFileHeaderMetadata('/seq/123.bam', '123/bam',
                                                samples={'name': set(['S9']), 'accession_number': set(['Acc9'])},
                                                libraries={'internal_id': set(['123'])}, studies={})
        seqscape_metadata = SeqscapeMetadata(samples={'name': set(['S1'])}, libraries={'internal_id': set(['444'])}, studies={})
        result = FileMetadataComparison._find_differences(header_metadata, seqscape_metadata, ['samples', 'libraries', 'studies'])
        self.assertEqual(result,{'samples': {'name': set(['S9'])}, 'libraries': {'internal_id': set(['123'])}})


    def test_find_differences_when_ok(self):
        irods_metadata = IrodsSeqFileMetadata('/seq/123.bam',
                                              samples={'name': set(['S1']), 'accession_number': set(), 'internal_id': set()},
                                              libraries={}, studies={})
        header_metadata = SAMFileHeaderMetadata('/seq/123.bam', '123/bam',
                                                samples={'name': set(['S1']), 'accession_number' : set(), 'internal_id': set()},
                                                libraries={}, studies={})
        result = FileMetadataComparison._find_differences(irods_metadata, header_metadata, ['samples'])
        self.assertDictEqual(result, {})


    def test_find_differences_when_entity_type_not_found_in_meta(self):
        irods_metadata = IrodsSeqFileMetadata('/seq/123.bam',
                                              samples={'name': set(['S1']), 'accession_number': set(), 'internal_id': set()},
                                              libraries={}, studies={})
        header_metadata = SAMFileHeaderMetadata('/seq/123.bam', '123/bam',
                                                samples={'name': set(['S1']), 'accession_number' : set(), 'internal_id': set()},
                                                libraries={}, studies={})
        self.assertRaises(AttributeError, FileMetadataComparison._find_differences, irods_metadata, header_metadata, ['nonexisting_entity'])
        # TODO: Comparison should throw an error as a CheckResult if AttributeError occurs (the attribute doesn't exist



    def test_mdata_from_diff_srcs_when_ok(self):
        irods_metadata = IrodsSeqFileMetadata('/seq/123.bam',
                                              samples={'name': set(['S1']), 'accession_number': set(), 'internal_id': set()},
                                              libraries={}, studies={})
        header_metadata = SAMFileHeaderMetadata('/seq/123.bam', '123/bam', samples={'name': set(['S1'])}, libraries={}, studies={})
        seqscape_metadata = SeqscapeMetadata(samples={'name': set(['S1'])}, libraries={}, studies={})
        issues_dict = defaultdict(list)
        FileMetadataComparison.check_metadata_across_different_sources({'/seq/213.bam': irods_metadata},
                                                                        {'/seq/213.bam': header_metadata},
                                                                        {'/seq/213.bam': seqscape_metadata},
                                                                        issues_dict)
        check_results = issues_dict['/seq/213.bam']
        self.assertEqual(4, len(check_results))

        results = {c.result for c in check_results}
        self.assertSetEqual(results, {RESULT.SUCCESS})


    def test_mdata_from_diff_srcs_when_different_id_types(self):
        irods_metadata = IrodsSeqFileMetadata('/seq/123.bam',
                                              samples={'name': set(['S1']), 'accession_number': set(['EGA1']), 'internal_id': set()},
                                              libraries={}, studies={})
        header_metadata = SAMFileHeaderMetadata('/seq/123.bam', '123/bam', samples={'name': set(['S1'])}, libraries={}, studies={})
        seqscape_metadata = SeqscapeMetadata(samples={'name': set(['S1'])}, libraries={}, studies={})
        issues_dict = defaultdict(list)
        FileMetadataComparison.check_metadata_across_different_sources({'/seq/213.bam': irods_metadata},
                                                                        {'/seq/213.bam': header_metadata},
                                                                        {'/seq/213.bam': seqscape_metadata},
                                                                        issues_dict)
        check_results = issues_dict['/seq/213.bam']
        self.assertEqual(4, len(check_results))

        results = {c.result for c in check_results}
        self.assertSetEqual(results, {RESULT.SUCCESS})


    def test_mdata_from_diff_srcs_when_diff_header(self):
        irods_metadata = IrodsSeqFileMetadata('/seq/123.bam',
                                              samples={'name': set(['S1']), 'accession_number': set(), 'internal_id': set()},
                                              libraries={}, studies={})
        header_metadata = SAMFileHeaderMetadata('/seq/123.bam', '123/bam', samples={'name': set(['S99999'])}, libraries={}, studies={})
        seqscape_metadata = SeqscapeMetadata(samples={'name': set(['S1'])}, libraries=set(), studies=set())
        issues_dict = defaultdict(list)
        FileMetadataComparison.check_metadata_across_different_sources({'/seq/213.bam': irods_metadata},
                                                                        {'/seq/213.bam': header_metadata},
                                                                        {'/seq/213.bam': seqscape_metadata},
                                                                        issues_dict)
        check_results = issues_dict['/seq/213.bam']
        self.assertEqual(4, len(check_results))

        print("RESULTS: %s" % check_results)
        results = {c.result for c in check_results}
        self.assertSetEqual(results, {RESULT.FAILURE})











