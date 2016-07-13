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

This file has been created on Jun 13, 2016.
"""
import unittest
from collections import defaultdict

from mcheck.main import run_checks

class ArgsConvertTests(unittest.TestCase):

    def test_convert_args_to_search_criteria_1(self):
        result = set(run_checks.convert_args_to_search_criteria(filter_by_npg_qc='1', filter_by_target='1', filter_by_file_types='cram'))
        expected = set([('manual_qc', '1'), ('target', '1'), ('type', 'cram')])
        self.assertSetEqual(result, expected)


    def test_convert_args_to_search_criteria_when_no_search_criteria(self):
        result = set(run_checks.convert_args_to_search_criteria())
        expected = set()
        self.assertSetEqual(result, expected)


    def test_convert_args_to_search_criteria_2(self):
        result = run_checks.convert_args_to_search_criteria(match_study_acc_nr='EGA1')
        expected = [('study_accession_number', 'EGA1')]
        self.assertSetEqual(set(result), set(expected))


    def test_convert_args_to_search_criteria_3(self):
        result = set(run_checks.convert_args_to_search_criteria(filter_by_file_types='bam'))
        expected = set([('type', 'bam')])
        self.assertSetEqual(result, expected)


class FetchIrodsMetadataTests(unittest.TestCase):

    def test_fetch_irods_metadata_by_path(self):
        issues_dict = defaultdict(list)
        json_str = '{"timestamps": [{"created": "2013-06-27T12:37:36", "replicates": 0}, {"modified": "2013-06-27T12:37:36", "replicates": 0}, {"created": "2013-06-27T12:38:48", "replicates": 1}, {"modified": "2013-06-27T12:38:48", "replicates": 1}], "collection": "/seq/10080", "access": [{"level": "read", "zone": "Sanger1", "owner": "trace"}, {"level": "read", "zone": "seq", "owner": "dnap_ro"}, {"level": "read", "zone": "seq", "owner": "ss_2034"}, {"level": "own", "zone": "Sanger1", "owner": "srpipe"}, {"level": "own", "zone": "seq", "owner": "rodsBoot"}, {"level": "own", "zone": "seq", "owner": "irods-g1"}, {"level": "read", "zone": "Sanger1", "owner": "psdpipe"}], "data_object": "10080_8#64.bam", "avus": [{"attribute": "id_run", "value": "10080"}, {"attribute": "sample_supplier_name", "value": "F31_FET"}, {"attribute": "type", "value": "bam"}, {"attribute": "lane", "value": "8"}, {"attribute": "study", "value": "SEQCAP_Abnormal_foetal_development_exome_trios"}, {"attribute": "is_paired_read", "value": "1"}, {"attribute": "md5", "value": "dd6163040f095c571f714169e079f50d"}, {"attribute": "tag", "value": "TCTCTTCA"}, {"attribute": "study_accession_number", "value": "EGAS00001000167"}, {"attribute": "library", "value": "7353571"}, {"attribute": "total_reads", "value": "44470502"}, {"attribute": "study_title", "value": "Abnormal foetal development exome trios"}, {"attribute": "sample_common_name", "value": "Homo Sapien"}, {"attribute": "manual_qc", "value": "1"}, {"attribute": "sample_accession_number", "value": "EGAN00001098854"}, {"attribute": "reference", "value": "/lustre/scratch109/srpipe/references/Homo_sapiens/1000Genomes_hs37d5/all/bwa/hs37d5.fa"}, {"attribute": "sample", "value": "SC_AFD5518355"}, {"attribute": "tag_index", "value": "64"}, {"attribute": "target", "value": "1"}, {"attribute": "sample_id", "value": "1613348"}, {"attribute": "library_id", "value": "7353571"}, {"attribute": "alignment", "value": "1"}, {"attribute": "study_id", "value": "2034"}], "checksum": "dd6163040f095c571f714169e079f50d", "replicates": [{"number": 0, "location": "irods-seq-sr04", "resource": "irods-seq-sr04-ddn-gc10-30-31-32", "checksum": "dd6163040f095c571f714169e079f50d", "valid": true}, {"number": 1, "location": "irods-seq-i10", "resource": "irods-seq-i10-bc", "checksum": "dd6163040f095c571f714169e079f50d", "valid": true}]}'
        irods_metadata_dict = run_checks.fetch_irods_metadata_from_json(issues_dict, json_str, 'hs37d5')
        for fpath, irods_metadata in irods_metadata_dict.items():
            self.assertEqual(len(irods_metadata.file_replicas), 2)
            self.assertEqual(len(irods_metadata.acls), 7)
            self.assertEqual(len(irods_metadata.avus), 23)





