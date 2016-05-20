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



class TestRawFileMetadataFromBaton(unittest.TestCase):

    def test_from_baton_wrapper_fname_and_path_1(self):
        data_obj = baton_models.DataObject(path='/seq/123/123.bam.bai')
        raw_meta = IrodsRawFileMetadata.from_baton_wrapper(data_obj)
        self.assertEqual(raw_meta.fname, '123.bam.bai')
        self.assertEqual(raw_meta.dir_path, '/seq/123')

    def test_from_baton_wrapper_fname_and_path_2(self):
        data_obj = baton_models.DataObject(path='/humgen/projects/helic/123.bam')
        raw_meta = IrodsRawFileMetadata.from_baton_wrapper(data_obj)
        self.assertEqual(raw_meta.fname, '123.bam')
        self.assertEqual(raw_meta.dir_path, '/humgen/projects/helic')

    def test_from_baton_wrapper_file_replicas(self):
        replicas = [
            baton_models.DataObjectReplica(number=1, checksum="123abc"),
            baton_models.DataObjectReplica(number=2, checksum="abc"),]
        data_obj = baton_models.DataObject(path='/humgen/projects/helic/123.bam', replicas=replicas)
        raw_meta = IrodsRawFileMetadata.from_baton_wrapper(data_obj)
        self.assertEqual(len(raw_meta.file_replicas), 2)

    def test_from_baton_wrapper_acls(self):
        acl = [baton_models.AccessControl(user_or_group='hgi', level=baton_models.AccessControl.Level.WRITE)]
        data_obj = baton_models.DataObject(path='/somepath/file.txt', access_controls=acl)
        raw_meta = IrodsRawFileMetadata.from_baton_wrapper(data_obj)
        self.assertEqual(len(raw_meta.acls), 1)
        self.assertEqual(raw_meta.acls[0].access_group, 'hgi')
        self.assertEqual(raw_meta.acls[0].permission, IrodsPermission.WRITE)



    def test_from_baton_wrapper_full_obj(self):
        acl = [baton_models.AccessControl(user_or_group='irina', level=baton_models.AccessControl.Level.OWN)]
        replicas = [
            baton_models.DataObjectReplica(number=1, checksum="123abc", host='hgi-dev', resource_name='irods-s1', up_to_date=True),
            baton_models.DataObjectReplica(number=2, checksum="abc", host='hgi-dev-wow', resource_name='irods-s2', up_to_date=True),]
        metadata = baton_coll.IrodsMetadata({'study': set(['BLUEPRINT'])})
        data_obj = baton_models.DataObject(path='/somepath/file.txt', access_controls=acl, metadata=metadata, replicas=replicas)
        raw_meta = IrodsRawFileMetadata.from_baton_wrapper(data_obj)
        self.assertEqual(raw_meta.fname, 'file.txt')
        self.assertEqual(raw_meta.dir_path, '/somepath')
        self.assertEqual(len(raw_meta.file_replicas), 2)
        self.assertEqual(len(raw_meta.acls), 1)
        #self.assertEqual(raw_meta.acls[0].zone, 'humgen')
        self.assertEqual(raw_meta.acls[0].access_group, 'irina')



    def test_from_baton_wrapper_all_ok(self):
        acl = [baton_models.AccessControl(user_or_group='irina', level=baton_models.AccessControl.Level.OWN)]
        print("ACL: %s" % acl)
        replicas = [
            baton_models.DataObjectReplica(number=1, checksum="123abc", host='hgi-dev', resource_name='irods-s1', up_to_date=True)]
        data_obj = baton_models.DataObject(path='/somepath/file.txt', access_controls=acl, replicas=replicas)
        raw_meta = IrodsRawFileMetadata.from_baton_wrapper(data_obj)
        self.assertEqual(raw_meta.fname, 'file.txt')
        self.assertEqual(raw_meta.dir_path, '/somepath')
        self.assertEqual(len(raw_meta.file_replicas), 1)
        self.assertEqual(len(raw_meta.acls), 1)
        #self.assertEqual(raw_meta.acls[0].zone, 'humgen')
        self.assertEqual(raw_meta.acls[0].access_group, 'irina')


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

        print(raw_meta.get_values_for_attribute('study'))
        self.assertEqual(raw_meta.get_values_for_attribute('study'), set(['BLUEPRINT']))



class TestIrodsRawFileMetadata(unittest.TestCase):

    def test_group_avus_per_attribute_1(self):
        avus_list = [MetaAVU(attribute='sample', value='ABCSample'), MetaAVU(attribute='sample', value='DEFGSample')]
        expected_result = {'sample': set(['ABCSample', 'DEFGSample'])}
        actual_result = IrodsRawFileMetadata._group_avus_per_attribute(avus_list)
        self.assertDictEqual(expected_result, actual_result)

    def test_group_avus_per_attribute_2(self):
        avus_list = [MetaAVU(attribute='sample', value='ABCSample'), MetaAVU(attribute='library', value='lib')]
        expected_result = {'sample': set(['ABCSample']), 'library': set(['lib'])}
        actual_result = IrodsRawFileMetadata._group_avus_per_attribute(avus_list)
        self.assertDictEqual(expected_result, actual_result)

    def test_group_avus_per_attribute_3(self):
        avus_list = [MetaAVU(attribute='sample', value='ABCSample'), MetaAVU(attribute='library', value='lib'),
                     MetaAVU(attribute='sample', value='XYZSample')]
        expected_result = {'sample': set(['ABCSample', 'XYZSample']), 'library': set(['lib'])}
        actual_result = IrodsRawFileMetadata._group_avus_per_attribute(avus_list)
        self.assertDictEqual(expected_result, actual_result)


    def test_set_attributes_from_avus_1(self):
        raw_meta = IrodsRawFileMetadata(fname='123.bam', dir_path='/seq/123')
        raw_meta.set_attributes_from_avus([MetaAVU(attribute='sample', value='ABCSample'),
                                           MetaAVU(attribute='library', value='lib')])
        expected_result = {'sample': set(['ABCSample']), 'library': set(['lib'])}
        self.assertDictEqual(raw_meta._attributes, expected_result)


    def test_get_values_for_attribute_1(self):
        raw_meta = IrodsRawFileMetadata(fname='123.bam', dir_path='/seq/123')
        raw_meta.set_attributes_from_avus([MetaAVU(attribute='sample', value='ABCSample'),
                                           MetaAVU(attribute='library', value='lib')])
        expected_result = set(['ABCSample'])
        actual_result = raw_meta.get_values_for_attribute('sample')
        self.assertSetEqual(actual_result, expected_result)

    def test_get_values_for_attribute_2(self):
        raw_meta = IrodsRawFileMetadata(fname='123.bam', dir_path='/seq/123')
        raw_meta.set_attributes_from_avus([MetaAVU(attribute='sample', value='ABCSample'),
                                           MetaAVU(attribute='sample', value='123')])
        expected_result = set(['ABCSample', '123'])
        actual_result = raw_meta.get_values_for_attribute('sample')
        self.assertSetEqual(actual_result, expected_result)

    def test_get_values_for_attribute_3(self):
        raw_meta = IrodsRawFileMetadata(fname='123.bam', dir_path='/seq/123')
        raw_meta.set_attributes_from_avus([MetaAVU(attribute='sample', value='ABCSample'),
                                           MetaAVU(attribute='library', value='lib')])
        expected_result = set()
        actual_result = raw_meta.get_values_for_attribute('study')
        self.assertSetEqual(actual_result, expected_result)


    def test_get_values_count_for_attribute_1(self):
        raw_meta = IrodsRawFileMetadata(fname='123.bam', dir_path='/seq/123')
        raw_meta.set_attributes_from_avus([MetaAVU(attribute='sample', value='ABCSample')])
        expected_result = 1
        actual_result = raw_meta.get_values_count_for_attribute('sample')
        self.assertEqual(expected_result, actual_result)

    def test_get_values_count_for_attribute_2(self):
        raw_meta = IrodsRawFileMetadata(fname='123.bam', dir_path='/seq/123')
        expected_result = 0
        actual_result = raw_meta.get_values_count_for_attribute('sample')
        self.assertEqual(expected_result, actual_result)


    def test_check_all_replicas_have_same_checksum_1(self):
        replica1 = IrodsFileReplica(checksum='abc', replica_nr=1)
        replica2 = IrodsFileReplica(checksum='abc', replica_nr=2)
        raw_metadata = IrodsRawFileMetadata(fname='123.bam', dir_path='/seq/123', file_replicas=[replica1, replica2])
        result = raw_metadata.check_all_replicas_have_same_checksum()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].result, RESULT.SUCCESS)


    def test_check_all_replicas_have_same_checksum_2(self):
        replica1 = IrodsFileReplica(checksum='abc', replica_nr=1)
        replica2 = IrodsFileReplica(checksum='abcabc', replica_nr=2)
        raw_metadata = IrodsRawFileMetadata(fname='123.bam', dir_path='/seq/123', file_replicas=[replica1, replica2])
        actual_result = raw_metadata.check_all_replicas_have_same_checksum()
        self.assertEqual(len(actual_result), 1)
        self.assertEqual(actual_result[0].result, RESULT.FAILURE)

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
        raw_metadata = IrodsRawFileMetadata(fname='myfile', dir_path='/home')
        raw_metadata.set_attributes_from_dict({'sample': set(['1', '2', '3'])})
        result = raw_metadata.check_attribute_count([AttributeCount(attribute='sample', count=3, operator='=')])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].result, RESULT.SUCCESS)

    def test_check_attribute_count_greater_ok(self):
        raw_metadata = IrodsRawFileMetadata(fname='myfile', dir_path='/home')
        raw_metadata.set_attributes_from_dict({'sample': set(['1', '2', '3'])})
        result = raw_metadata.check_attribute_count([AttributeCount(attribute='sample', count=2, operator='>')])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].result, RESULT.SUCCESS)


    def test_check_attribute_count_less_wrong(self):
        raw_metadata = IrodsRawFileMetadata(fname='myfile', dir_path='/home')
        raw_metadata.set_attributes_from_dict({'sample': set(['1', '2', '3'])})
        result = raw_metadata.check_attribute_count([AttributeCount(attribute='sample', count=2, operator='<')])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].result, RESULT.FAILURE)

    def test_check_attribute_count_when_not_found(self):
        raw_metadata = IrodsRawFileMetadata(fname='myfile', dir_path='/home')
        raw_metadata.set_attributes_from_dict({'sample': set(['1', '2', '3'])})
        result = raw_metadata.check_attribute_count([AttributeCount(attribute='study', count=2, operator='>')])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].result, RESULT.FAILURE)


    def test_check_non_public_acls_when_there_are(self):
        acl = IrodsACL(access_group='public#seq', zone='seq', permission='own')
        raw_metadata = IrodsRawFileMetadata(fname='myfile', dir_path='/home', acls=[acl])
        result = raw_metadata.check_non_public_acls()
        self.assertEqual(len(result), 1)

    def test_check_non_public_acls_when_not(self):
        acl1 = IrodsACL(access_group='ss_123#seq', zone='seq', permission='own')
        acl2 = IrodsACL(access_group='npg#seq', zone='seq', permission='own')
        raw_metadata = IrodsRawFileMetadata(fname='myfile', dir_path='/home', acls=[acl1, acl2])
        result = raw_metadata.check_non_public_acls()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].result, RESULT.SUCCESS)


    def test_check_has_read_permission_ss_group_when_ok(self):
        acl1 = IrodsACL(access_group='ss_123#seq', zone='seq', permission='read')
        acl2 = IrodsACL(access_group='npg#seq', zone='seq', permission='own')
        raw_metadata = IrodsRawFileMetadata(fname='myfile', dir_path='/home', acls=[acl1, acl2])
        result = raw_metadata.check_has_read_permission_ss_group()
        self.assertEqual(len(result), 2)
        for check_res in result:
            self.assertEqual(check_res.result, RESULT.SUCCESS)

    def test_check_has_read_permission_ss_group_when_own_instead_of_read(self):
        acl1 = IrodsACL(access_group='ss_123#seq', zone='seq', permission='own')
        acl2 = IrodsACL(access_group='npg#seq', zone='seq', permission='own')
        raw_metadata = IrodsRawFileMetadata(fname='myfile', dir_path='/home', acls=[acl1, acl2])
        result = raw_metadata.check_has_read_permission_ss_group()
        self.assertEqual(len(result), 2)
        for check_res in result:
            if check_res.check_name == CHECK_NAMES.check_ss_irods_group_read_permission:
                self.assertEqual(check_res.result, RESULT.FAILURE)
            else:
                self.assertEqual(check_res.result, RESULT.SUCCESS)

    def test_check_has_read_permission_ss_group_no_ss_grp(self):
        acl1 = IrodsACL(access_group='public#seq', zone='seq', permission='read')
        acl2 = IrodsACL(access_group='npg#seq', zone='seq', permission='own')
        raw_metadata = IrodsRawFileMetadata(fname='myfile', dir_path='/home', acls=[acl1, acl2])
        result = raw_metadata.check_has_read_permission_ss_group()
        self.assertEqual(len(result), 2)
        for check_res in result:
            if check_res.check_name == CHECK_NAMES.check_there_is_ss_irods_group:
                self.assertEqual(check_res.result, RESULT.FAILURE)
            else:
                self.assertEqual(check_res.result, RESULT.SUCCESS)


    def test_check_more_than_one_replicas_when_1(self):
        replicas = [baton_models.DataObjectReplica(number=2, checksum="abc")]
        raw_metadata = IrodsRawFileMetadata(fname='123.bam', dir_path='/seq', file_replicas=replicas)
        result = raw_metadata.check_more_than_one_replicas()
        self.assertEqual(len(result), 1)

    def test_check_more_than_one_replicas_when_no_replica(self):
        replicas = []
        raw_metadata = IrodsRawFileMetadata(fname='123.bam', dir_path='/seq', file_replicas=replicas)
        result = raw_metadata.check_more_than_one_replicas()
        self.assertEqual(len(result), 1)

    def test_check_more_than_one_replicas_when_ok(self):
        replicas = [
            baton_models.DataObjectReplica(number=1, checksum="123abc"),
            baton_models.DataObjectReplica(number=2, checksum="abc"),]
        raw_metadata = IrodsRawFileMetadata(fname='123.bam', dir_path='/seq', file_replicas=replicas)
        result = raw_metadata.check_more_than_one_replicas()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].result, RESULT.SUCCESS)



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


    def test_is_checksum_valid_1(self):
        checksum = 'abcdref123asssssdaf'
        result = IrodsSeqFileMetadata._check_checksum(checksum)
        self.assertEqual(len(result), 0)

    def test_is_checksum_valid_2(self):
        checksum = 'abcdref123asssssdafAAA'
        result = IrodsSeqFileMetadata._check_checksum(checksum)
        self.assertEqual(len(result), 0)

    def test_is_checksum_valid_3(self):
        checksum = ''
        result = IrodsSeqFileMetadata._check_checksum(checksum)
        self.assertEqual(len(result), 1)

    def test_is_checksum_valid_when_valid(self):
        checksum = '123'
        result = IrodsSeqFileMetadata._check_checksum(checksum)
        self.assertEqual(len(result), 0)

    def test_is_checksum_valid_when_invalid_because_capitals(self):
        checksum = 'AAA'
        result = IrodsSeqFileMetadata._check_checksum(checksum)
        self.assertEqual(len(result), 0)

    def test_is_checksum_valid_6(self):
        checksum = 123
        self.assertRaises(TypeError, IrodsSeqFileMetadata._check_checksum, checksum)


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
        self.assertRaises(TypeError, IrodsSeqFileMetadata._is_npg_qc_valid, npq_qc)


    def test_check_checksum_calculated_vs_metadata_1(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.bam', fname='1234_5#6.bam',
                                              checksum_in_meta='123abc', checksum_at_upload='123abc')
        result = irods_metadata.validate_checksums()
        self.assertEqual(len(result), 0)

    def test_check_checksum_calculated_vs_metadata_2(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.bam', fname='1234_5#6.bam',
                                              checksum_in_meta='123abc123', checksum_at_upload='123abc')
        result = irods_metadata.validate_checksums()
        self.assertEqual(len(result), 1)
#        self.assertEqual(result[0].result, RESULT.FAILURE)

    def test_check_checksum_calculated_vs_metadata_3(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.bam', fname='1234_5#6.bam',
                                              checksum_in_meta='123abc')
        result = irods_metadata.validate_checksums()
        self.assertEqual(len(result), 2)
        #self.assertEqual(result[0].executed, False)

    def test_check_checksum_calculated_vs_metadata_4(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.bam', fname='1234_5#6.bam',
                                              checksum_at_upload='123abc')
        result = irods_metadata.validate_checksums()
        self.assertEqual(len(result), 2)
        #self.assertEqual(result[0].executed, False)


    def test_validate_fields_1(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.bam', fname='1234_5#6.bam',
                                              checksum_in_meta='aaAAA')
        result = irods_metadata.validate_fields()
        self.assertEqual(len(result), 2)

    def test_validate_fields_2(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.bam', fname='1234_5#6.bam')
        result = irods_metadata.validate_fields()
        print("RESUlts: %s" % result)
        self.assertEqual(len(result), 3)

    def test_validate_fields_when_wrong_npg_qc(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.bam', fname='1234_5#6.bam', npg_qc='aaAAA',
                                              checksum_at_upload='123abc', checksum_in_meta='123abc')
        result = irods_metadata.validate_fields()
        self.assertEqual(len(result), 1)

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


    def test_check_reference_1(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.cram', fname='1234_5#6.cram',
                                              references=['/lustre/hs37d5.fa'])
        result = irods_metadata.check_reference('hs37d5')
        self.assertEqual(result, [])

    def test_check_reference_2(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.cram', fname='1234_5#6.cram',
                                              references=['/lustre/hs37d5.fa'])
        result = irods_metadata.check_reference('')
        self.assertEqual(len(result), 1)

    def test_check_reference_3(self):
        irods_metadata = IrodsSeqFileMetadata(fpath='/seq/1234/1234_5#6.cram', fname='1234_5#6.cram')
        result = irods_metadata.check_reference('')
        self.assertEqual(len(result), 2)

    def test_from_raw_metadata_only_replicas(self):
        replicas = [
            baton_models.DataObjectReplica(number=1, checksum="123abc"),
            baton_models.DataObjectReplica(number=2, checksum="abc"),]
        raw_metadata = IrodsRawFileMetadata(fname='123.bam', dir_path='/seq', file_replicas=replicas)
        seq_metadata = IrodsSeqFileMetadata.from_raw_metadata(raw_metadata)
        expected = {'name': set(), 'accession_number': set(), 'internal_id': set()}
        self.assertEqual(seq_metadata.samples, expected)
        self.assertEqual(seq_metadata.libraries, expected)
        self.assertEqual(seq_metadata.checksum_in_meta, set())
        check_results = seq_metadata.check_metadata()
        self.assertEqual(len(check_results), 3)

    def test_check_more_than_one_replicas_when_ok(self):
        replicas = [
            baton_models.DataObjectReplica(number=1, checksum="123abc"),
            baton_models.DataObjectReplica(number=2, checksum="abc")]
        raw_metadata = IrodsRawFileMetadata(fname='123.cram', dir_path='/seq/123', file_replicas=replicas)
        result = raw_metadata.check_more_than_one_replicas()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].result, RESULT.SUCCESS)

    def test_check_more_than_one_replicas_when_1_replica(self):
        replicas = [
            baton_models.DataObjectReplica(number=1, checksum="123abc")]
        raw_metadata = IrodsRawFileMetadata(fname='123.cram', dir_path='/seq/123', file_replicas=replicas)
        result = raw_metadata.check_more_than_one_replicas()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].result, RESULT.FAILURE)

    def test_check_more_than_one_replicas_when_no_replica(self):
        replicas = []
        raw_metadata = IrodsRawFileMetadata(fname='123.cram', dir_path='/seq/123', file_replicas=replicas)
        result = raw_metadata.check_more_than_one_replicas()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].result, RESULT.FAILURE)



if __name__ == "__main__":
    unittest.main()