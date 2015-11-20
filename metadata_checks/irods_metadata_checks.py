"""
Copyright (C) 2015  Genome Research Ltd.

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

This file has been created on Nov 18, 2015.
"""

from main import metadata_utils
from main import error_types
from com import utils as common_utils
from com.operators import Operators
from irods import constants as irods_consts
from metadata_types.attribute_count import AttributeCount, AttributeCountComparison
from metadata_types.irods_metadata import IrodsFileMetadata, IrodsRawFileMetadata, IrodsACL, IrodsFileReplicasChecksum

import re
from typing import List


# TODO: replace iRODSCMDUTILS with some other way of extracting values - probably in a AVU class or smth, depending on the implementation in Baton wrapper


# class IRODSACL:
#     def __init__(self, access_group: str, zone: str, permission: str):
#         self.access_group = access_group
#         self.zone = zone
#         self.permission = permission

class IrodsACLsChecks:

    def check_non_public_acls(self, acls: List[IrodsACL]):
        for acl in acls:
            if acl.access_group == 'public':
        #        raise PublicData!!!!
                pass

    def check_has_specific_group_permission(self, acls: List[IrodsACL], permission: str):
        """
        Check in the ACLs for permission for a specific access_group.
        :param acls:
        :return:
        """
        pass

#TODO: make Enums with permissions and irods seq zones
# class IRODSRawFileMetadata:
#     def __init__(self, fname, dir_path, avus_list, md5_at_upload=None):
#         self.avus = avus_list
#         self.fname = fname
#         self.dir_path = dir_path
#         self.md5_at_upload = md5_at_upload

# AVUCOunt
#         self.attribute = attribute
#         self.count = count
#         self.operator = operator
#

class IRODSRawFileMetadataChecks:

    def _is_true_comparison(self, left_operand: int, right_operand: int, operator: str):
        if operator == Operators.EQUAL:
            return left_operand == right_operand
        elif operator == Operators.GREATER_THAN:
            return left_operand > right_operand
        elif operator == Operators.LESS_THAN:
            return left_operand < right_operand


    def check_attribute_count(self, raw_metadata: IrodsRawFileMetadata, avu_counts: List[AttributeCount]):
        differences = []
        for avu_count in avu_counts:
            count = raw_metadata.get_values_for_attribute(avu_counts.attribute)
            threshold = avu_count.count
            if not self._is_true_comparison(count, threshold, avu_count.operator):
                comparison = AttributeCountComparison(attribute=avu_count.attribute, threshold=threshold,
                                      actual_count=count, operator=avu_count.operator)
                differences.append(comparison)
        # TODO: return or raise an error?!
        return differences


class IRODSFileMetadataChecks:

    # @classmethod
    # def filter_out_non_entities(cls, fpath, entity_dict, entity_type):
    #     filtered_entities = {}
    #     problems = []
    #     for id_type, ids_list in list(entity_dict.items()):
    #         filtered_ids = cls.filter_out_non_ids(ids_list)
    #         non_ids = set(ids_list).difference(set(filtered_ids))
    #         problems.extend([error_types.WrongMetadataValue(fpath=fpath, attribute=str(entity_type)+'_'+str(id_type), value=id) for id in non_ids])
    #         filtered_entities[id_type] = filtered_ids
    #     return filtered_entities, problems


    @classmethod
    def run_field_sanity_checks_and_filter(file_metadata):
        problems = []
        if self.samples:
            #self.samples, pbs = self._filter_out_non_entities(self.samples)
            self.samples, pbs = metadata_utils.GeneralUtils.filter_out_non_entities(self.fpath, self.samples, 'sample')
            pbs = [error_types.WrongIRODSMetadataValue(err.fpath, err.attribute, err.value) for err in pbs]
            problems.extend(pbs)

        if self.libraries:
            self.libraries, pbs = metadata_utils.GeneralUtils.filter_out_non_entities(self.fpath, self.libraries, 'library')
            pbs = [error_types.WrongIRODSMetadataValue(err.fpath, err.attribute, err.value) for err in pbs]
            problems.extend(pbs)

        if self.studies:
            self.studies, pbs = metadata_utils.GeneralUtils.filter_out_non_entities(self.fpath, self.studies, 'study')
            pbs = [error_types.WrongIRODSMetadataValue(err.fpath, err.attribute, err.value) for err in pbs]
            problems.extend(pbs)

        if self.md5 and not self.is_md5(self.md5):
            problems.append(error_types.WrongMetadataValue(fpath=self.fpath, attribute='md5', value=self.md5))
        if self.ichksum_md5 and not self.is_md5(self.ichksum_md5):
            problems.append(error_types.WrongMetadataValue(fpath=self.fpath, attribute='ichcksum_md5', value=self.ichksum_md5))
        if self.run_id and not self.is_run_id(self.run_id):
            problems.append(error_types.WrongMetadataValue(fpath=self.fpath, attribute='run_id', value=self.run_id))
        if self.lane_id and not self.is_lane_id(self.lane_id):
            problems.append(error_types.WrongMetadataValue(fpath=self.fpath, attribute='lane_id', value=self.lane_id))
        if self.npg_qc and not self.is_npg_qc(self.npg_qc):
            problems.append(error_types.WrongMetadataValue(fpath=self.fpath, attribute='npg_qc', value=self.npg_qc))
        if self.target and not self.is_target(self.target):
            problems.append(error_types.WrongMetadataValue(fpath=self.fpath, attribute='target', value=self.target))
        return problems

    @classmethod
    def run_avu_count_checks(cls, fpath, avus):
        problems = []
        md5_list = metadata_utils.iRODSiCmdsUtils.extract_values_for_key_from_irods_metadata(avus, 'md5')
        if len(md5_list) != 1:
            problems.append(error_types.MetadataAttributeCountError(fpath, 'md5', '1', str(len(md5_list))))

        ref_list = metadata_utils.iRODSiCmdsUtils.extract_values_for_key_from_irods_metadata(avus, 'reference')
        if len(ref_list) != 1:
            problems.append(error_types.MetadataAttributeCountError(fpath, 'reference', '1', str(len(ref_list))))

        run_id_list = metadata_utils.iRODSiCmdsUtils.extract_values_for_key_from_irods_metadata(avus, 'id_run')
        if len(run_id_list) != 1:
            problems.append(error_types.MetadataAttributeCountError(fpath, 'id_run', '1', str(len(run_id_list))))

        lane_id_list = metadata_utils.iRODSiCmdsUtils.extract_values_for_key_from_irods_metadata(avus, 'lane')
        if len(lane_id_list) != 1:
            problems.append(error_types.MetadataAttributeCountError(fpath, 'lane', '1', str(len(lane_id_list))))

        npg_qc_list = metadata_utils.iRODSiCmdsUtils.extract_values_for_key_from_irods_metadata(avus, 'manual_qc')
        if len(npg_qc_list) != 1:
            problems.append(error_types.MetadataAttributeCountError(fpath, 'manual_qc', '1', str(len(npg_qc_list))))
        return problems



    @classmethod
    def is_md5(cls, md5):
        if not type(md5) is str:
            raise TypeError("WRONG TYPE: the MD5 must be a string, and is: " + str(type(md5)))
        r = re.compile(irods_consts.MD5_REGEX)
        return True if r.match(md5) else False

    @classmethod
    def is_run_id(cls, run_id):
        if not type(run_id) in [str, int]:
            raise TypeError("WRONG TYPE: the run_id must be a string or int and is: " + str(type(run_id)))
        r = re.compile(irods_consts.RUN_ID_REGEX)
        return True if r.match(str(run_id)) else False

    @classmethod
    def is_lane_id(cls, lane_id):
        if not type(lane_id) in [str, int]:
            raise TypeError("WRONG TYPE: the lane_id must be either string or int and is: " + str(type(lane_id)))
        r = re.compile(irods_consts.LANE_ID_REGEX)
        return True if r.match(str(lane_id)) else False

    @classmethod
    def is_npg_qc(cls, npg_qc):
        if not type(npg_qc) in [str, int]:
            raise TypeError("WRONG TYPE: the npg_qc must be either string or int and is: " + str(npg_qc))
        r = re.compile(irods_consts.NPG_QC_REGEX)
        return True if r.match(str(npg_qc)) else False


    @classmethod
    def is_target(cls, target):
        if not type(target) in [str, int]:
            raise TypeError("WRONG TYPE: the target must be either string or int and is: " + str(target))
        r = re.compile(irods_consts.TARGET_REGEX)
        return True if r.match(str(target)) else False


    @classmethod
    def check_is_irods_seq_fpath(cls, fpath):
        r = re.compile(irods_consts.IRODS_SEQ_LANELET_PATH_REGEX)
        if not r.match(fpath):
            raise ValueError("Not an iRODS seq path: " + str(fpath))


    @classmethod
    def check_is_lanelet_filename(cls, fname):
        """
        Checks if a filename looks like: 1234_5.* or 1234_5#6.*
        :param fname: file name
        :return: bool
        """
        r = re.compile(irods_consts.LANLET_NAME_REGEX)
        if not r.match(fname):
            raise ValueError("Not a lanelet filename: " + str(fname))


    @classmethod
    def check_is_irods_lanelet_fpath(cls, fpath):
        """
        Checks if a given file path is an irods seq path and that it is a lanelet. e.g. 1234_5.bam, 1234_5#6.cram
        :param fpath:
        :return:
        """
        cls.check_is_irods_seq_fpath(fpath)
        fname = common_utils.extract_fname_without_ext(fpath)
        cls.check_is_lanelet_filename(fname)




    def test_run_id_from_fname_vs_metadata(self):
        """
        This test assumes that all the files in iRODS have exactly 1 run (=LANELETS)
        """
        if not self.run_id:
            raise error_types.TestImpossibleToRunError(fpath=self.fpath,
                                                       reason='The run_id in iRODS metadata is either missing or more than 1.',
                                                       test_name='Check run_id from filename vs. iRODS metadata.')
        try:
            run_id_from_fname = self.get_run_from_irods_fname(self.fname)
        except ValueError as e:
            raise error_types.TestImpossibleToRunError(fpath=self.fpath, reason=str(e), test_name='Check run_id from filename vs. run_id from iRODS metadata') # 'Cant extract the run id from file name. Not a sequencing file?'
        else:
            if str(self.run_id) != str(run_id_from_fname):
                raise error_types.IrodsMetadataAttributeVsFileNameError(fpath=self.fpath, attribute='run_id', irods_value=self.run_id, filename_value=run_id_from_fname)


    # TODO: actually the user can't know exactly the name of the files - this needs refactoring, in order to associate the name of the ref file with the name of the ref
    def test_reference(self, desired_ref):
        if not self.reference:
            raise error_types.TestImpossibleToRunError(fpath=self.fpath, test_name='Check reference',reason='The reference from iRODS metadata is either missing or more than 1.')
        if not desired_ref:
            raise error_types.TestImpossibleToRunError(fpath=self.fpath, test_name='Check_reference', reason='Missing desired reference parameter.')
        #if self.reference != desired_ref:
        if self.reference.find(desired_ref) == -1:
            raise error_types.WrongReferenceError(fpath=self.fpath, desired_ref=desired_ref, header_ref='not implemented', irods_ref=self.reference)


    def test_md5_calculated_vs_metadata(self):
        if self.ichksum_md5 and self.md5:
            if self.ichksum_md5 != self.md5:
                raise error_types.WrongMD5Error(fpath=self.fpath, imeta_value=self.md5, ichksum_value=self.ichksum_md5)
        else:
            if not self.ichksum_md5:
                raise error_types.TestImpossibleToRunError(fpath=self.fpath, test_name='Test md5', reason='The md5 returned by ichksum is missing')
            if not self.md5:
                raise error_types.TestImpossibleToRunError(fpath=self.fpath, test_name='Test md5', reason='The md5 in iRODS metadata is either missing or more than 1.')


    def test_lane_from_fname_vs_metadata(self):
        if not self.lane_id:
            raise error_types.TestImpossibleToRunError(fpath=self.fpath,
                                                       reason='The lane id in the iRODS metadata is either missing or more than 1 ',
                                                       test_name='Check lane id from filename vs iRODS metadata')
        try:
            lane_from_fname = self.get_lane_from_irods_fname(self.fname)
        except ValueError as e:
            raise error_types.TestImpossibleToRunError(fpath=self.fpath,
                                                       reason=str(e),
                                                       test_name='Check lane id from filename vs iRODS metadata')
        else:
            if str(lane_from_fname) != str(self.lane_id):
                raise error_types.IrodsMetadataAttributeVsFileNameError(fpath=self.fpath, attribute='lane', irods_value=self.lane_id, filename_value=lane_from_fname)




