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
from metadata_types.irods_metadata import IrodsFileMetadata, IrodsRawFileMetadata, IrodsACL, IrodsFileReplica

import re
from typing import List


# TODO: replace iRODSCMDUTILS with some other way of extracting values - probably in a AVU class or smth, depending on the implementation in Baton wrapper


# class IRODSACL:
#     def __init__(self, access_group: str, zone: str, permission: str):
#         self.access_group = access_group
#         self.zone = zone
#         self.permission = permission

class IrodsACLChecks:

    @classmethod
    def check_non_public_acls(cls, acls: List[IrodsACL]):
        """
        Checks that the iRODS object doesn't have associated an ACL giving public access to users to it.
        :param acls:
        :return:
        """
        for acl in acls:
            if acl.provides_public_access():
                raise error_types.WrongACLWarning( message="ACL for public access found " + str(acl))


    @classmethod
    def check_has_read_permission_ss_group(cls, acls: List[IrodsACL]):
        """
        Checks if any of the ACLs is for an ss group.
        :param acls:
        :param permission:
        :return:
        """
        found_ss_gr_acl = False
        for acl in acls:
            if acl.provides_access_for_ss_group():
                found_ss_gr_acl = True
                if not acl.provides_read_permission():
                    raise error_types.WrongACLWarning(message="ACL provides user/group: "+ str(acl.access_group) +
                                                                  " permission="+str(acl.permission))
                break
        if not found_ss_gr_acl:
            raise error_types.MissingACLWarning("There is no ACL for an ss_* group, probably nobody "
                                                "outside of NPG can access this file")


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

# class IrodsFileReplicaChecksum:
#     def __init__(self, checksum: str, replica_nr: int):
#         self.checksum = checksum
#         self.replica_nr = replica_nr

class IrodsFileReplicaChecks:

    @classmethod
    def check_all_replicas_have_same_checksum(cls, replicas: List[IrodsFileReplica]):
        if not replicas:
            return
        first_replica = replicas[0]
        for replica in replicas:
            if not replica.checksum == first_replica.checksum:
                raise error_types.DifferentFileReplicasWarning(message="Replicas different ",
                                                               replicas=[str(first_replica), str(replica)])

class IRODSRawFileMetadataChecks:

    @classmethod
    def _is_true_comparison(cls, left_operand: int, right_operand: int, operator: str):
        if operator == Operators.EQUAL:
            return left_operand == right_operand
        elif operator == Operators.GREATER_THAN:
            return left_operand > right_operand
        elif operator == Operators.LESS_THAN:
            return left_operand < right_operand

    @classmethod
    def check_attribute_count(cls, raw_metadata: IrodsRawFileMetadata, avu_counts: List[AttributeCount]):
        differences = []
        for avu_count in avu_counts:
            count = raw_metadata.get_values_for_attribute(avu_counts.attribute)
            threshold = avu_count.count
            if not cls._is_true_comparison(count, threshold, avu_count.operator):
                comparison = AttributeCountComparison(attribute=avu_count.attribute, threshold=threshold,
                                      actual_count=count, operator=avu_count.operator)
                differences.append(comparison)
        # TODO: return or raise an error?!
        return differences


# class IrodsFileMetadata(object):
#     def __init__(self, fpath: str=None, fname :str=None, samples=None, libraries=None, studies=None,
#                  checksum_in_meta:str=None, checksum_at_upload:str=None, references:List[str]=None,
#                  run_ids:List[str]=None, lane_ids:List[str]=None, npg_qc:str=None, target:str=None):
#         self.fname = fname
#         self.fpath = fpath
#         self.samples = samples
#         self.libraries = libraries
#         self.studies = studies
#         self.checksum_in_meta = checksum_in_meta
#         self.checksum_at_upload = checksum_at_upload
#         self._references = references
#         self.run_ids = run_ids
#         self.lane_ids = lane_ids
#         self._npg_qc_values = [npg_qc]
#         self._target_values = [target]


class IRODSFileMetadataChecks:

    @classmethod
    def run_field_sanity_checks(cls, file_metadata: IrodsFileMetadata):
        problems = []
        if not cls.is_checksum(file_metadata.checksum_in_meta):
            problems.append(error_types.WrongMetadataValue(attribute='Checksum_in_metadata', value=file_metadata.checksum_in_meta))

        if not cls.is_checksum(file_metadata.checksum_at_upload):
            problems.append(error_types.WrongMetadataValue(attribute='Checksum_at_upload', value=file_metadata.checksum_at_upload))

        for lane in file_metadata.lane_ids:
            if not cls.is_lane_id(lane):
                problems.append(error_types.WrongMetadataValue(attribute='lane'), value=lane)

        for run in file_metadata.run_ids:
            if not cls.is_run_id(run):
                problems.append(error_types.WrongMetadataValue(attribute='run_id'), value=run)

        if not cls.is_npg_qc(file_metadata.get_npg_qc()):
            problems.append(error_types.WrongMetadataValue(attribute='npg_qc'), value=file_metadata.get_npg_qc())

        if not cls.is_target(file_metadata.get_target()):
            problems.append(error_types.WrongMetadataValue(attribute='target', value=file_metadata.get_target()))

    @classmethod
    def check_file_metadata(cls, file_metadata: IrodsFileMetadata, desired_reference: str):
        problems = []
        try:
            cls.test_checksum_calculated_vs_metadata(file_metadata)
        except error_types.TestImpossibleToRunError:
            pass
            # TODO: think what to do in this case...
        except error_types.WrongChecksumError as e:
            problems.append(e)

        try:
            cls.test_lane_from_fname_vs_metadata(file_metadata)
        except error_types.TestImpossibleToRunError as e:
            # problems.append(e)
            pass
            # TODO: not sure
        except error_types.IrodsMetadataAttributeVsFileNameError as e:
            problems.append(e)

        try:
            cls.test_run_id_from_fname_vs_metadata(file_metadata)
        except error_types.TestImpossibleToRunError as e:
            #problems.append(e)
            #TODO: not sure where to save these...
            pass
        except error_types.IrodsMetadataAttributeVsFileNameError as e:
            problems.append(e)

        try:
            cls.test_reference(file_metadata, desired_reference)
        except error_types.WrongReferenceError as e:
            problems.append(e)
        except error_types.TestImpossibleToRunError as e:
            pass


    @classmethod
    def is_checksum(cls, checksum):
        if not type(checksum) is str:
            raise TypeError("WRONG TYPE: the checksum must be a string, and is: " + str(type(checksum)))
        r = re.compile(irods_consts.MD5_REGEX)
        return True if r.match(checksum) else False

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

    @classmethod
    def test_checksum_calculated_vs_metadata(cls, file_metadata):
        if file_metadata.checksum_in_meta and file_metadata.checksum_at_upload:
            if file_metadata.checksum_in_meta != file_metadata.checksum_at_upload:
                raise error_types.WrongChecksumError(fpath=file_metadata.fpath,
                                                     imeta_value=file_metadata.checksum_at_upload,
                                                     ichksum_value=file_metadata.checksum_in_meta)
        else:
            if not file_metadata.checksum_in_meta:
                raise error_types.TestImpossibleToRunError(fpath=file_metadata.fpath, test_name='Test md5',
                                                           reason='The md5 returned by ichksum is missing')
            if not file_metadata.checksum_at_upload:
                raise error_types.TestImpossibleToRunError(fpath=file_metadata.fpath, test_name='Test md5',
                                                           reason='The md5 in iRODS metadata is either missing or more than 1.')

    @classmethod
    def test_run_id_from_fname_vs_metadata(cls, file_metadata):
        """
        This test assumes that all the files in iRODS have exactly 1 run (=LANELETS)
        """
        if not file_metadata.run_id:
            raise error_types.TestImpossibleToRunError(fpath=file_metadata.fpath,
                                                       reason='The run_id in iRODS metadata is either missing or more than 1.',
                                                       test_name='Check run_id from filename vs. iRODS metadata.')
        try:
            run_id_from_fname = file_metadata.get_run_from_irods_fname(file_metadata.fname)
        except ValueError as e:
            raise error_types.TestImpossibleToRunError(fpath=file_metadata.fpath, reason=str(e),
                                                       test_name='Check run_id from filename vs. run_id from iRODS metadata') # 'Cant extract the run id from file name. Not a sequencing file?'
        else:
            if str(file_metadata.run_id) != str(run_id_from_fname):
                raise error_types.IrodsMetadataAttributeVsFileNameError(fpath=file_metadata.fpath, attribute='run_id',
                                                                        irods_value=file_metadata.run_id,
                                                                        filename_value=run_id_from_fname)


    # TODO: actually the user can't know exactly the name of the files - this needs refactoring, in order to associate the name of the ref file with the name of the ref
    @classmethod
    def test_reference(cls, file_metadata, desired_ref):
        if not file_metadata.reference:
            raise error_types.TestImpossibleToRunError(fpath=file_metadata.fpath, test_name='Check reference',reason='The reference from iRODS metadata is either missing or more than 1.')
        if not desired_ref:
            raise error_types.TestImpossibleToRunError(fpath=file_metadata.fpath, test_name='Check_reference', reason='Missing desired reference parameter.')
        #if self.reference != desired_ref:
        if file_metadata.reference.find(desired_ref) == -1:
            raise error_types.WrongReferenceError(fpath=file_metadata.fpath, desired_ref=desired_ref, header_ref='not implemented', irods_ref=self.reference)


    @classmethod
    def test_lane_from_fname_vs_metadata(cls, file_metadata):
        if not file_metadata.lane_id:
            raise error_types.TestImpossibleToRunError(fpath=file_metadata.fpath,
                                                       reason='The lane id in the iRODS metadata is either missing or more than 1 ',
                                                       test_name='Check lane id from filename vs iRODS metadata')
        try:
            lane_from_fname = file_metadata.get_lane_from_irods_fname(file_metadata.fname)
        except ValueError as e:
            raise error_types.TestImpossibleToRunError(fpath=file_metadata.fpath,
                                                       reason=str(e),
                                                       test_name='Check lane id from filename vs iRODS metadata')
        else:
            if str(lane_from_fname) != str(file_metadata.lane_id):
                raise error_types.IrodsMetadataAttributeVsFileNameError(fpath=file_metadata.fpath, attribute='lane',
                                                                        irods_value=file_metadata.lane_id,
                                                                        filename_value=lane_from_fname)




