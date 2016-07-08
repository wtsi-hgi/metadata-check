"""
Copyright (C) 2015  Genome Research Ltd.

Author: Irina Colgiu <ic4@sanger.ac.uk>

This program is part of metadata-check

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

This file has been created on Jun 26, 2015.
"""

import unittest

from mcheck.metadata.irods_metadata.constants import IrodsPermission
from mcheck.metadata.irods_metadata.avu import MetaAVU
from mcheck.metadata.irods_metadata.file_metadata import IrodsSeqFileMetadata, IrodsRawFileMetadata
from mcheck.metadata.irods_metadata.file_replica import IrodsFileReplica
from mcheck.results.constants import RESULT
from mcheck.check_names import CHECK_NAMES
from mcheck.metadata.irods_metadata.acl import IrodsACL
from baton import models as baton_models
from baton import collections as baton_coll
from mcheck.metadata.common.attribute_count import AttributeCount
from mcheck.check_names import CHECK_NAMES



class TestRawFileMetadataFromBaton(unittest.TestCase):

    def test_from_baton_wrapper_fpath_1(self):
        data_obj = baton_models.DataObject(path='/seq/123/123.bam.bai')
        raw_meta = IrodsRawFileMetadata.from_baton_wrapper(data_obj)
        self.assertEqual(raw_meta.fpath, '/seq/123/123.bam.bai')

    def test_from_baton_wrapper_fpath_2(self):
        data_obj = baton_models.DataObject(path='/humgen/projects/helic/123.bam')
        raw_meta = IrodsRawFileMetadata.from_baton_wrapper(data_obj)
        self.assertEqual(raw_meta.fpath, '/humgen/projects/helic/123.bam')

    def test_from_baton_wrapper_file_replicas(self):
        replicas = [
            baton_models.DataObjectReplica(number=1, checksum="123abc"),
            baton_models.DataObjectReplica(number=2, checksum="abc"),]
        data_obj = baton_models.DataObject(path='/humgen/projects/helic/123.bam', replicas=replicas)
        raw_meta = IrodsRawFileMetadata.from_baton_wrapper(data_obj)
        self.assertEqual(len(raw_meta.file_replicas), 2)

    def test_from_baton_wrapper_acls(self):
        user = "hgi#Sanger1"
        acl = [baton_models.AccessControl(user, level=baton_models.AccessControl.Level.WRITE)]
        data_obj = baton_models.DataObject(path='/somepath/file.txt', access_controls=acl)
        raw_meta = IrodsRawFileMetadata.from_baton_wrapper(data_obj)
        self.assertEqual(len(raw_meta.acls), 1)
        self.assertEqual(raw_meta.acls[0].access_group, 'hgi')
        self.assertEqual(raw_meta.acls[0].permission, IrodsPermission.WRITE)
        self.assertEqual(raw_meta.acls[0].zone, 'Sanger1')


    def test_from_baton_wrapper_full_obj(self):
        user = "hgi#humgen"
        acl = [baton_models.AccessControl(user, level=baton_models.AccessControl.Level.OWN)]
        replicas = [
            baton_models.DataObjectReplica(number=1, checksum="123abc", host='hgi-dev', resource_name='irods-s1', up_to_date=True),
            baton_models.DataObjectReplica(number=2, checksum="abc", host='hgi-dev-wow', resource_name='irods-s2', up_to_date=True),]
        metadata = baton_coll.IrodsMetadata({'study': set(['BLUEPRINT'])})
        data_obj = baton_models.DataObject(path='/somepath/file.txt', access_controls=acl, metadata=metadata, replicas=replicas)
        raw_meta = IrodsRawFileMetadata.from_baton_wrapper(data_obj)
        self.assertEqual(raw_meta.fpath, '/somepath/file.txt')
        self.assertEqual(len(raw_meta.file_replicas), 2)
        self.assertEqual(len(raw_meta.acls), 1)
        self.assertEqual(raw_meta.acls[0].zone, 'humgen')
        self.assertEqual(raw_meta.acls[0].access_group, 'hgi')


    def test_from_baton_wrapper_all_ok(self):
        user = "serapis#humgen"
        acl = [baton_models.AccessControl(user, level=baton_models.AccessControl.Level.OWN)]
        replicas = [
            baton_models.DataObjectReplica(number=1, checksum="123abc", host='hgi-dev', resource_name='irods-s1', up_to_date=True)]
        data_obj = baton_models.DataObject(path='/somepath/file.txt', access_controls=acl, replicas=replicas)
        raw_meta = IrodsRawFileMetadata.from_baton_wrapper(data_obj)
        self.assertEqual(raw_meta.fpath, '/somepath/file.txt')
        self.assertEqual(len(raw_meta.file_replicas), 1)
        self.assertEqual(len(raw_meta.acls), 1)
        self.assertEqual(raw_meta.acls[0].zone, 'humgen')
        self.assertEqual(raw_meta.acls[0].access_group, 'serapis')


    def test_from_baton_wrapper_missing_bits(self):
        replicas = [
            baton_models.DataObjectReplica(number=1, checksum="123abc", host='hgi-dev', resource_name='irods-s1', up_to_date=True)]
        metadata = baton_coll.IrodsMetadata({'study': set(['BLUEPRINT'])})
        data_obj = baton_models.DataObject(path='/somepath/file.txt', metadata=metadata, replicas=replicas)
        raw_meta = IrodsRawFileMetadata.from_baton_wrapper(data_obj)
        self.assertEqual(len(raw_meta.file_replicas), 1)
        self.assertEqual(len(raw_meta.acls), 0)

    def test_from_baton_wrapper_metadata(self):
        metadata = baton_coll.IrodsMetadata({'study': set(['BLUEPRINT']), 'sample': set(['123sam'])})
        data_obj = baton_models.DataObject(path='/somepath/file.txt', metadata=metadata)
        raw_meta = IrodsRawFileMetadata.from_baton_wrapper(data_obj)

        self.assertEqual(raw_meta.get_values_for_attribute('study'), set(['BLUEPRINT']))



class TestIrodsRawFileMetadata(unittest.TestCase):

    # def test_group_avus_per_attribute_1(self):
    #     avus_list = [MetaAVU(attribute='sample', value='ABCSample'), MetaAVU(attribute='sample', value='DEFGSample')]
    #     expected_result = {'sample': set(['ABCSample', 'DEFGSample'])}
    #     actual_result = IrodsRawFileMetadata._group_avus_per_attribute(avus_list)
    #     self.assertDictEqual(expected_result, actual_result)
    #
    # def test_group_avus_per_attribute_2(self):
    #     avus_list = [MetaAVU(attribute='sample', value='ABCSample'), MetaAVU(attribute='library', value='lib')]
    #     expected_result = {'sample': set(['ABCSample']), 'library': set(['lib'])}
    #     actual_result = IrodsRawFileMetadata._group_avus_per_attribute(avus_list)
    #     self.assertDictEqual(expected_result, actual_result)
    #
    # def test_group_avus_per_attribute_3(self):
    #     avus_list = [MetaAVU(attribute='sample', value='ABCSample'), MetaAVU(attribute='library', value='lib'),
    #                  MetaAVU(attribute='sample', value='XYZSample')]
    #     expected_result = {'sample': set(['ABCSample', 'XYZSample']), 'library': set(['lib'])}
    #     actual_result = IrodsRawFileMetadata._group_avus_per_attribute(avus_list)
    #     self.assertDictEqual(expected_result, actual_result)


    def test_set_attributes_from_avus_1(self):
        raw_meta = IrodsRawFileMetadata(fpath='/seq/123/123.bam')
        raw_meta.init_avus_from_avu_tuples([MetaAVU(attribute='sample', value='ABCSample'),
                                           MetaAVU(attribute='library', value='lib')])
        expected_result = {'sample': set(['ABCSample']), 'library': set(['lib'])}
        self.assertDictEqual(raw_meta.avus, expected_result)


    def test_get_values_for_attribute_1(self):
        raw_meta = IrodsRawFileMetadata(fpath='/seq/123/123.bam')
        raw_meta.init_avus_from_avu_tuples([MetaAVU(attribute='sample', value='ABCSample'),
                                           MetaAVU(attribute='library', value='lib')])
        expected_result = set(['ABCSample'])
        actual_result = raw_meta.get_values_for_attribute('sample')
        self.assertSetEqual(actual_result, expected_result)

    def test_get_values_for_attribute_2(self):
        raw_meta = IrodsRawFileMetadata(fpath='/seq/123/123.bam')
        raw_meta.init_avus_from_avu_tuples([MetaAVU(attribute='sample', value='ABCSample'),
                                           MetaAVU(attribute='sample', value='123')])
        expected_result = set(['ABCSample', '123'])
        actual_result = raw_meta.get_values_for_attribute('sample')
        self.assertSetEqual(actual_result, expected_result)

    def test_get_values_for_attribute_3(self):
        raw_meta = IrodsRawFileMetadata(fpath='/seq/123/123.bam')
        raw_meta.init_avus_from_avu_tuples([MetaAVU(attribute='sample', value='ABCSample'),
                                           MetaAVU(attribute='library', value='lib')])
        expected_result = set()
        actual_result = raw_meta.get_values_for_attribute('study')
        self.assertSetEqual(actual_result, expected_result)


    def test_get_values_count_for_attribute_1(self):
        raw_meta = IrodsRawFileMetadata(fpath='/seq/123/123.bam')
        raw_meta.init_avus_from_avu_tuples([MetaAVU(attribute='sample', value='ABCSample')])
        expected_result = 1
        actual_result = raw_meta.get_values_count_for_attribute('sample')
        self.assertEqual(expected_result, actual_result)

    def test_get_values_count_for_attribute_2(self):
        raw_meta = IrodsRawFileMetadata(fpath='/seq/123/123.bam')
        expected_result = 0
        actual_result = raw_meta.get_values_count_for_attribute('sample')
        self.assertEqual(expected_result, actual_result)


    def test_check_all_replicas_have_same_checksum_1(self):
        replica1 = IrodsFileReplica(checksum='abc', replica_nr=1)
        replica2 = IrodsFileReplica(checksum='abc', replica_nr=2)
        replicas=[replica1, replica2]
        result = IrodsRawFileMetadata.ReplicasChecks.check_all_replicas_have_same_checksum(replicas)
        #self.assertEqual(len(result), 1)
        self.assertEqual(result.result, RESULT.SUCCESS)


    def test_check_all_replicas_have_same_checksum_2(self):
        replica1 = IrodsFileReplica(checksum='abc', replica_nr=1)
        replica2 = IrodsFileReplica(checksum='abcabc', replica_nr=2)
        replicas=[replica1, replica2]
        actual_result = IrodsRawFileMetadata.ReplicasChecks.check_all_replicas_have_same_checksum(replicas)
        #self.assertEqual(len(actual_result), 1)
        self.assertEqual(actual_result.result, RESULT.FAILURE)

    def test_is_true_comparison_when_equal(self):
        result = IrodsRawFileMetadata._is_true_comparison(1, 1, '=')
        self.assertTrue(result)

    def test_is_true_comparison_when_less(self):
        result = IrodsRawFileMetadata._is_true_comparison(1, 2, '<')
        self.assertTrue(result)

    def test_is_true_comparison_when_not_equal(self):
        result = IrodsRawFileMetadata._is_true_comparison(1, 3, '=')
        self.assertFalse(result)

    def test_is_true_comparison_raises_exc_when_operator_unknown(self):
        self.assertRaises(ValueError, IrodsRawFileMetadata._is_true_comparison, 1, 3, '#')

    def test_check_attribute_count_equal_ok(self):
        raw_metadata = IrodsRawFileMetadata(fpath='/home/myfile')
        raw_metadata.avus = {'sample': set(['1', '2', '3'])}
        result = raw_metadata.check_attribute_count([AttributeCount(attribute='sample', count=3, operator='=')])
        #self.assertEqual(len(result), 1)
        self.assertEqual(result.result, RESULT.SUCCESS)

    def test_check_attribute_count_greater_ok(self):
        raw_metadata = IrodsRawFileMetadata(fpath='/home/myfile')
        raw_metadata.avus = {'sample': set(['1', '2', '3'])}
        result = raw_metadata.check_attribute_count([AttributeCount(attribute='sample', count=2, operator='>')])
        #self.assertEqual(len(result), 1)
        self.assertEqual(result.result, RESULT.SUCCESS)


    def test_check_attribute_count_less_wrong(self):
        raw_metadata = IrodsRawFileMetadata(fpath='/home/myfile')
        raw_metadata.avus = {'sample': set(['1', '2', '3'])}
        result = raw_metadata.check_attribute_count([AttributeCount(attribute='sample', count=2, operator='<')])
        #self.assertEqual(len(result), 1)
        self.assertEqual(result.result, RESULT.FAILURE)

    def test_check_attribute_count_when_not_found(self):
        raw_metadata = IrodsRawFileMetadata(fpath='/home/myfile')
        raw_metadata.avus = {'sample': set(['1', '2', '3'])}
        result = raw_metadata.check_attribute_count([AttributeCount(attribute='study', count=2, operator='>')])
        #self.assertEqual(len(result), 1)
        self.assertEqual(result.result, RESULT.FAILURE)


    def test_check_non_public_acls_when_there_are(self):
        acl = IrodsACL(access_group='public#seq', zone='seq', permission='own')
        acls=[acl]
        #raw_metadata = IrodsRawFileMetadata(fname='myfile', dir_path='/home', acls=[acl])
        result = IrodsRawFileMetadata.ACLsChecks.check_non_public_acls(acls)
        self.assertEqual(result.result, RESULT.FAILURE)

    def test_check_non_public_acls_when_not(self):
        acl1 = IrodsACL(access_group='ss_123#seq', zone='seq', permission='own')
        acl2 = IrodsACL(access_group='npg#seq', zone='seq', permission='own')
        acls = [acl1, acl2]
        result = IrodsRawFileMetadata.ACLsChecks.check_non_public_acls(acls)
        self.assertEqual(result.result, RESULT.SUCCESS)


    def test_check_has_read_permission_ss_group_when_ok(self):
        acl1 = IrodsACL(access_group='ss_123#seq', zone='seq', permission='read')
        acl2 = IrodsACL(access_group='npg#seq', zone='seq', permission='own')
        acls=[acl1, acl2]
        result = IrodsRawFileMetadata.ACLsChecks.check_read_permission_exists_for_ss_group(acls)
        self.assertEqual(len(result), 2)
        for check_res in result:
            self.assertEqual(check_res.result, RESULT.SUCCESS)

    def test_check_has_read_permission_ss_group_when_own_instead_of_read(self):
        acl1 = IrodsACL(access_group='ss_123#seq', zone='seq', permission='own')
        acl2 = IrodsACL(access_group='npg#seq', zone='seq', permission='own')
        acls=[acl1, acl2]
        result = IrodsRawFileMetadata.ACLsChecks.check_read_permission_exists_for_ss_group(acls)
        self.assertEqual(len(result), 2)
        for check_res in result:
            if check_res.check_name == CHECK_NAMES.check_ss_irods_group_read_permission:
                self.assertEqual(check_res.result, RESULT.FAILURE)
            else:
                self.assertEqual(check_res.result, RESULT.SUCCESS)

    def test_check_has_read_permission_ss_group_no_ss_grp(self):
        acl1 = IrodsACL(access_group='public#seq', zone='seq', permission='read')
        acl2 = IrodsACL(access_group='npg#seq', zone='seq', permission='own')
        raw_metadata = IrodsRawFileMetadata(fpath='/home/myfile', acls=[acl1, acl2])
        result = raw_metadata.ACLsChecks.check_read_permission_exists_for_ss_group(raw_metadata.acls)
        self.assertEqual(len(result), 2)
        for check_res in result:
            if check_res.check_name in [CHECK_NAMES.check_ss_irods_group_read_permission, CHECK_NAMES.check_there_is_ss_irods_group]:
                self.assertEqual(check_res.result, RESULT.FAILURE)
            else:
                self.assertEqual(check_res.result, RESULT.SUCCESS)


    def test_check_more_than_one_replicas_when_1(self):
        replicas = [baton_models.DataObjectReplica(number=2, checksum="abc")]
        result = IrodsRawFileMetadata.ReplicasChecks.check_more_than_one_replicas(replicas)
        self.assertEqual(result.result, RESULT.FAILURE)

    def test_check_more_than_one_replicas_when_no_replica(self):
        replicas = []
        result = IrodsRawFileMetadata.ReplicasChecks.check_more_than_one_replicas(replicas)
        self.assertEqual(result.result, RESULT.FAILURE)

    def test_check_more_than_one_replicas_when_ok(self):
        replicas = [
            baton_models.DataObjectReplica(number=1, checksum="123abc"),
            baton_models.DataObjectReplica(number=2, checksum="abc"),]
        result = IrodsRawFileMetadata.ReplicasChecks.check_more_than_one_replicas(replicas)
        self.assertEqual(result.result, RESULT.SUCCESS)


class TestIrodsSeqFileMetadata(unittest.TestCase):
    def test_extract_reference_name_from_ref_path1(self):
        ref_path = '/lustre/scratch109/srpipe/references/Homo_sapiens/1000Genomes_hs37d5/all/bwa/hs37d5.fa'
        result = IrodsSeqFileMetadata.extract_reference_name_from_ref_path(ref_path)
        self.assertEqual(result, 'hs37d5')

    def test_extract_reference_name_from_ref_path2(self):
        ref_path = '/lustre/scratch110/srpipe/references/Homo_sapiens/1000Genomes/all/bwa/human_g1k_v37.fasta'
        result = IrodsSeqFileMetadata.extract_reference_name_from_ref_path(ref_path)
        self.assertEqual(result, 'human_g1k_v37')

    def test_extract_reference_name_from_ref_path3(self):
        ref_path = '/lustre/scratch109/srpipe/references/Homo_sapiens/GRCh38_15/all/bwa0_6/Homo_sapiens.GRCh38_15.fa'
        result = IrodsSeqFileMetadata.extract_reference_name_from_ref_path(ref_path)
        self.assertEqual(result, 'Homo_sapiens.GRCh38_15')

    def test_extract_reference_name_from_ref_path4(self):
        ref_path = '/lustre/scratch110/srpipe/references/Homo_sapiens/GRCh37_53/all/bwa/Homo_sapiens.GRCh37.dna.all.fa'
        result = IrodsSeqFileMetadata.extract_reference_name_from_ref_path(ref_path)
        self.assertEqual(result, 'Homo_sapiens.GRCh37.dna.all')

    def test_extract_reference_name_from_ref_path5(self):
        ref_path = '/lustre/scratch110/srpipe/references/Homo_sapiens/GRCh37_53/all/bwa/Homo_sapiens.bam'
        self.assertRaises(ValueError, IrodsSeqFileMetadata.extract_reference_name_from_ref_path, ref_path)


    def test_is_npg_qc_valid_1(self):
        npq_qc = 1
        result = IrodsSeqFileMetadata._is_npg_qc_valid(npq_qc)
        self.assertTrue(result)

    def test_is_npg_qc_valid_2(self):
        npq_qc = 4
        result = IrodsSeqFileMetadata._is_npg_qc_valid(npq_qc)
        self.assertFalse(result)

    def test_is_npg_qc_valid_3(self):
        npq_qc = "1"
        result = IrodsSeqFileMetadata._is_npg_qc_valid(npq_qc)
        self.assertTrue(result)

    def test_is_npg_qc_valid_4(self):
        npq_qc = "0"
        result = IrodsSeqFileMetadata._is_npg_qc_valid(npq_qc)
        self.assertTrue(result)

    def test_is_npg_qc_valid_5(self):
        npq_qc = 123
        result = IrodsSeqFileMetadata._is_npg_qc_valid(npq_qc)
        self.assertFalse(result)

    def test_is_npg_qc_valid_6(self):
        npq_qc = "mamba"
        result = IrodsSeqFileMetadata._is_npg_qc_valid(npq_qc)
        self.assertFalse(result)

    def test_is_npg_qc_valid_7(self):
        npq_qc = True
        self.assertFalse(IrodsSeqFileMetadata._is_npg_qc_valid(npq_qc))


    def test_validate_fields_1(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.bam',
                                              checksum_in_meta='aaAAA')
        result = irods_metadata.validate_fields()
        self.assertEqual(len(result), 5)
        for check_res in result:
            if check_res.check_name == CHECK_NAMES.check_checksum_in_metadata_present:
                self.assertEqual(check_res.result, RESULT.SUCCESS)
            elif check_res.check_name == CHECK_NAMES.check_by_comparison_checksum_in_meta_with_checksum_at_upload:
                self.assertEqual(check_res.result, None)

    def test_validate_fields_2(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.bam')
        result = irods_metadata.validate_fields()
        self.assertEqual(len(result), 5)
        for check_res in result:
            if check_res.check_name == CHECK_NAMES.check_by_comparison_checksum_in_meta_with_checksum_at_upload:
                self.assertEqual(check_res.result, None)
            else:
                self.assertEqual(check_res.result, RESULT.FAILURE)

    def test_validate_fields_when_wrong_npg_qc(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.bam', npg_qc='aaAAA',
                                              checksum_at_upload='123abc', checksum_in_meta='123abc')
        result = irods_metadata.validate_fields()
        self.assertEqual(len(result), 5)
        for check_res in result:
            if check_res.check_name in [CHECK_NAMES.check_target_field, CHECK_NAMES.check_npg_qc_field]:
                self.assertEqual(check_res.result, RESULT.FAILURE)
            else:
                self.assertEqual(check_res.result, RESULT.SUCCESS)


    def test_is_target_valid_when_valid_1(self):
        result = IrodsSeqFileMetadata._is_target_valid('1')
        self.assertTrue(result)

    def test_is_target_valid_when_valid_library(self):
        result = IrodsSeqFileMetadata._is_target_valid('library')
        self.assertTrue(result)

    def test_is_target_valid_when_invalid(self):
        result = IrodsSeqFileMetadata._is_target_valid('somethingelse')
        self.assertFalse(result)

    def test_is_target_valid_when_empty(self):
        result = IrodsSeqFileMetadata._is_target_valid('')
        self.assertFalse(result)


    def test_check_reference_when_ok(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.cram',
                                              references=['/lustre/hs37d5.fa'])
        result = irods_metadata.check_reference('hs37d5')
        self.assertEqual(result.result, RESULT.SUCCESS)

    def test_check_reference_2(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.cram',
                                              references=['/lustre/hs37d5.fa'])
        result = irods_metadata.check_reference('')
        self.assertEqual(result.result, None)
        self.assertEqual(result.executed, False)

    def test_check_reference_3(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.cram')
        result = irods_metadata.check_reference('')
        self.assertEqual(result.result, None)
        self.assertEqual(result.executed, False)

    def test_from_raw_metadata_only_replicas(self):
        replicas = [
            baton_models.DataObjectReplica(number=1, checksum="123abc"),
            baton_models.DataObjectReplica(number=2, checksum="abc"),]
        raw_metadata = IrodsRawFileMetadata(fpath='/seq/123.bam', file_replicas=replicas)
        seq_metadata = IrodsSeqFileMetadata.from_raw_metadata(raw_metadata)
        expected = {'name': set(), 'accession_number': set(), 'internal_id': set()}
        self.assertEqual(seq_metadata.samples, expected)
        self.assertEqual(seq_metadata.libraries, expected)
        self.assertEqual(seq_metadata.checksum_in_meta, set())
        #TODO: test further the fields of seq_metadata

    def test_check_more_than_one_replicas_when_ok(self):
        replicas = [
            baton_models.DataObjectReplica(number=1, checksum="123abc"),
            baton_models.DataObjectReplica(number=2, checksum="abc")]
        raw_metadata = IrodsRawFileMetadata(fpath='/seq/123/123.cram', file_replicas=replicas)
        result = raw_metadata.ReplicasChecks.check_more_than_one_replicas(raw_metadata.file_replicas)
        self.assertEqual(result.result, RESULT.SUCCESS)
        #self.assertEqual(result[0].result, RESULT.SUCCESS)

    def test_check_more_than_one_replicas_when_1_replica(self):
        replicas = [
            baton_models.DataObjectReplica(number=1, checksum="123abc")]
        raw_metadata = IrodsRawFileMetadata(fpath='/seq/123/123.cram', file_replicas=replicas)
        result = raw_metadata.ReplicasChecks.check_more_than_one_replicas(raw_metadata.file_replicas)
        #self.assertEqual(len(result), 1)
        self.assertEqual(result.result, RESULT.FAILURE)

    def test_check_more_than_one_replicas_when_no_replica(self):
        replicas = []
        raw_metadata = IrodsRawFileMetadata(fpath='/seq/123/123.cram', file_replicas=replicas)
        result = raw_metadata.ReplicasChecks.check_more_than_one_replicas(raw_metadata.file_replicas)
        #self.assertEqual(len(result), 1)
        self.assertEqual(result.result, RESULT.FAILURE)

    def test_check_checksum_at_upload_present_when_present(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.bam', checksum_at_upload='aaa')
        result = irods_metadata.check_checksum_at_upload_present()
        self.assertEqual(result.result, RESULT.SUCCESS)

    def test_check_checksum_at_upload_present_when_absent(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.bam')
        result = irods_metadata.check_checksum_at_upload_present()
        self.assertEqual(result.result, RESULT.FAILURE)

    def test_check_checksum_in_meta_present(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.bam', checksum_in_meta='aaa')
        result = irods_metadata.check_checksum_in_meta_present()
        self.assertEqual(result.result, RESULT.SUCCESS)

    def test_check_checksum_in_meta_present_when_absent(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.bam')
        result = irods_metadata.check_checksum_in_meta_present()
        self.assertEqual(result.result, RESULT.FAILURE)

    def test_check_attribute_frequencies_when_missing_acc_nr(self):
        avus = {'study_id': {'3257'}, 'sample_id': {'1248216'}, 'target': {'1'},
                'study_accession_number': {'EGAS00001000929'}, 'library_id': {'14820960'}, 'study': {'GDAP_XTEN'},
                'sample': {'APP5201296'}, 'md5': {'123abc'}, 'manual_qc': {'1'}, 'sample_common_name': {'Homo sapiens'},
                'reference': {'hla/all/bwa0_6/Homo_sapiens.GRCh38_full_analysis_set_plus_decoy_hla.fa'}, 'type': {'cram'}}
        check_result = IrodsSeqFileMetadata.CompleteMetadataChecks.check_attribute_frequencies(avus)
        self.assertEqual(check_result.result, RESULT.FAILURE)
        self.assertEqual(len(check_result.error_message), 1)

    def test_check_attribute_frequencies_when_ok(self):
        avus = {'study_id': {'3257'}, 'sample_id': {'1248216'}, 'sample_accession_number': {'EGA123'}, 'target': {'1'},
                'study_accession_number': {'EGAS00001000929'}, 'library_id': {'14820960'}, 'study': {'GDAP_XTEN'},
                'sample': {'APP5201296'}, 'md5': {'123abc'}, 'manual_qc': {'1'}, 'sample_common_name': {'Homo sapiens'},
                'reference': {'hla/all/bwa0_6/Homo_sapiens.GRCh38_full_analysis_set_plus_decoy_hla.fa'}, 'type': {'cram'}}
        check_result = IrodsSeqFileMetadata.CompleteMetadataChecks.check_attribute_frequencies(avus)
        self.assertEqual(check_result.result, RESULT.SUCCESS)

    def test_check_attribute_frequencies_when_missing3_fields(self):
        avus = {'study_id': {'3257'}, 'sample_id': {'1248216'},
                'study_accession_number': {'EGAS00001000929'}, 'library_id': {'14820960'}, 'study': {'GDAP_XTEN'},
                'sample': {'APP5201296'}, 'md5': {'123abc'}, 'manual_qc': {'1'},
                'reference': {'hla/all/bwa0_6/Homo_sapiens.GRCh38_full_analysis_set_plus_decoy_hla.fa'}, 'type': {'cram'}}
        check_result = IrodsSeqFileMetadata.CompleteMetadataChecks.check_attribute_frequencies(avus)
        self.assertEqual(check_result.result, RESULT.FAILURE)
        self.assertEqual(len(check_result.error_message), 3)


    def test_check_attribute_frequencies_when_ok_and_extra_meta(self):
        avus = {'study_id': {'3257'}, 'sample_id': {'1248216'}, 'sample_accession_number': {'EGA123'}, 'target': {'1'},
                'study_accession_number': {'EGAS00001000929'}, 'library_id': {'14820960'}, 'study': {'GDAP_XTEN'},
                'sample': {'APP5201296'}, 'md5': {'123abc'}, 'manual_qc': {'1'}, 'sample_common_name': {'Homo sapiens'},
                'reference': {'hla/all/bwa0_6/Homo_sapiens.GRCh38_full_analysis_set_plus_decoy_hla.fa'}, 'type': {'cram'},
                'some_tag': {'some_val'}}
        check_result = IrodsSeqFileMetadata.CompleteMetadataChecks.check_attribute_frequencies(avus)
        self.assertEqual(check_result.result, RESULT.SUCCESS)


if __name__ == "__main__":
    unittest.main()