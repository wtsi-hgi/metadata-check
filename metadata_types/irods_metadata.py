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

This file has been created on Jun 23, 2015.
"""

import re
from collections import defaultdict
from typing import List, Dict

from com.operators import Operators
from main import error_types
from com import utils as common_utils
from irods import constants as irods_consts
from irods import data_types
from metadata_types.identifiers import EntityIdentifier

# PUBLIC:
# jq -n '{collection: "/seq/10001", data_object: "10001_1#30_phix.bai"}' | /software/gapi/pkg/baton/0.15.0/bin/baton-list
# --acl --checksum --replicate{"collection": "/seq/10001", "data_object": "10001_1#30_phix.bai",
# "replicate": [{"checksum": "2b84f847c8418e5d1ccb26e8e5633c53", "number": 0, "valid": true},
# {"checksum": "2b84f847c8418e5d1ccb26e8e5633c53", "number": 1, "valid": true}],
# "checksum": "2b84f847c8418e5d1ccb26e8e5633c53",
# "access": [{"owner": "trace", "zone": "Sanger1", "level": "read"},
# {"owner": "srpipe", "zone": "Sanger1", "level": "own"},
# {"owner": "rodsBoot", "zone": "seq", "level": "own"},
# {"owner": "irods-g1", "zone": "seq", "level": "own"},
# {"owner": "public", "zone": "seq", "level": "read"},
# {"owner": "psdpipe", "zone": "Sanger1", "level": "read"}]}


# OWNED:
# {"collection": "/seq/10080", "data_object": "10080_8#64.bam",
# "replicate": [{"checksum": "dd6163040f095c571f714169e079f50d", "number": 0, "valid": true},
# {"checksum": "dd6163040f095c571f714169e079f50d", "number": 1, "valid": true}],
# "checksum": "dd6163040f095c571f714169e079f50d",
# "access": [{"owner": "trace", "zone": "Sanger1", "level": "read"},
# {"owner": "ss_2034", "zone": "seq", "level": "read"}, {"owner": "srpipe", "zone": "Sanger1", "level": "own"},
# {"owner": "rodsBoot", "zone": "seq", "level": "own"}, {"owner": "irods-g1", "zone": "seq", "level": "own"},
# {"owner": "psdpipe", "zone": "Sanger1", "level": "read"}]}



class IrodsACL:
    def __init__(self, access_group: str, zone: str, permission: str):
        self.access_group = access_group
        self.zone = zone
        self.permission = permission

    def __eq__(self, other):
        return self.access_group == other.access_group and self.zone == other.zone and \
               self.permission == other.permission

    def __str__(self):
        return "Access group = " + str(self.access_group) + ", zone: " + \
               str(self.zone) + ", permission = " + str(self.permission)

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.access_group) + hash(self.zone) + hash(self.permission)

    def provides_public_access(self):
        r = re.compile(irods_consts.IRODS_GROUPS.PUBLIC)
        if r.match(self.access_group):
            return True
        return False

    def provides_access_for_ss_group(self):
        r = re.compile(irods_consts.IRODS_GROUPS.SS_GROUP_REGEX)
        if r.match(self.access_group):
            return True
        return False

    def provides_read_permission(self):
        return self.permission == irods_consts.IRODS_PERMISSIONS.READ

    def provides_write_permission(self):
        return self.permission == irods_consts.IRODS_PERMISSIONS.WRITE

    def provides_own_permission(self):
        return self.permission == irods_consts.IRODS_PERMISSIONS.OWN

    @staticmethod
    def _validate_permission(permission):
        if not type(permission) is str:
            raise TypeError("This permission is not a string, it is a: " + str(type(permission)))
        return permission in irods_consts.IRODS_PERMISSIONS

    @staticmethod
    def _validate_irods_zone(zone):
        if not type(zone) is str:
            raise TypeError("This zone is not a string, it is a: " + str(type(zone)))
        return zone in irods_consts.IRODS_ZONES

    def validate(self):
        problems = []
        if not self._validate_irods_zone():
            problems.append(ValueError("This ACL doesn't contain a valid iRODS zone: " + str(self.zone)))
        if not self._validate_permission(self.permission):
            problems.append(ValueError("This ACL doesn't contain a valid iRODS permission: " + str(self.permission)))
        return problems


class IrodsFileReplica:
    def __init__(self, checksum: str, replica_nr: int):
        self.checksum = checksum
        self.replica_nr = replica_nr

    def __eq__(self, other):
        return self.checksum == other.checksum and self.replica_nr == other.replica_nr

    def __str__(self):
        return "Replica nr =  " + str(self.replica_nr) + ", checksum = " + str(self.checksum)

    def __repr__(self):
        return self.__repr__()

    def __hash__(self):
        return hash(self.checksum) + hash(self.replica_nr)

    @staticmethod
    def _validate_replica_nr(replica_nr):
        if not replica_nr.isdigit():
            raise TypeError("WRONG type of parameter: replica_nr should be a digit and is: " + str(replica_nr))
        if int(replica_nr) >= 0:
            return True
        return False

    @staticmethod
    def _validate_checksum(checksum):
        if not type(checksum) is str:
            raise TypeError("WRONG TYPE: the checksum must be a string, and is: " + str(type(checksum)))
        r = re.compile(irods_consts.MD5_REGEX)
        return True if r.match(checksum) else False

    def validate(self):
        problems = []
        if not self._validate_checksum():
            problems.append(ValueError("Replica's checksum doesn't look like a checksum: " + str(self.checksum)))
        if not self._validate_replica_nr():
            problems.append(ValueError("Replica's number(id) doesn't look like an id: " + str(self.replica_nr)))
        return problems


class IrodsRawFileMetadata:
    def __init__(self, fname: str, dir_path: str, file_replicas: List[IrodsFileReplica]=None,
                 acls: List[IrodsACL]=None):
        self.fname = fname
        self.dir_path = dir_path
        self.file_replicas = file_replicas
        self.acls = acls
        self._avus = {}

    def set_attributes_from_avus(self, avus_list: List[data_types.MetaAVU]):
        self._avus = IrodsRawFileMetadata.group_attributes(avus_list)

    def set_attributes_from_dict(self, avus_dict: Dict[str, List[str]]):
        self._avus = avus_dict

    def get_values_for_attribute(self, attribute: str):
        return self._avus[attribute] if self._avus.has_key(attribute) else None

    @classmethod
    def group_attributes(cls, avus):
        avus_grouped = defaultdict(list)
        for avu in avus:
            avus_grouped[avu.attribute].append(avu.value)
        return avus_grouped

    def validate(self):
        problems = []
        for replica in self.replicas:
            problems.extend(replica.validate())
        for acl in self.acls:
            problems.extend(acl.validate())
        return problems

    def __str__(self):
        return "Location: dir_path = " + str(self.dir_path) + ", fname = " + str(self.fname) + ", AVUS: " + self._avus \
               + ", md5_at_upload = " + str(self.file_replicas)

    def __repr__(self):
        return self.__str__()

    def _is_true_comparison(self, left_operand: int, right_operand: int, operator: str):
        if operator == Operators.EQUAL:
            return left_operand == right_operand
        elif operator == Operators.GREATER_THAN:
            return left_operand > right_operand
        elif operator == Operators.LESS_THAN:
            return left_operand < right_operand

    def check_attribute_count(self, avu_counts: List[AttributeCount]):
        problems = []
        for avu_count in avu_counts:
            count = self.get_values_for_attribute(avu_counts.attribute)
            threshold = avu_count.count
            if not self._is_true_comparison(count, threshold, avu_count.operator):
                problems.append(error_types.MetadataAttributeCountError(attribute=avu_count.attribute,
                                                                        desired_occurances=threshold,
                                                                        actual_occurances=count,
                                                                        operator=avu_count.operator))
        return problems

    def check_all_replicas_have_same_checksum(self):
        if not self.replicas:
            return []
        problems = []
        first_replica = self.replicas[0]
        for replica in self.replicas:
            if not replica.checksum == first_replica.checksum:
                problems.append(error_types.DifferentFileReplicasWarning(message="Replicas different ",
                                                                         replicas=[str(first_replica), str(replica)]))
        return problems


    def check_more_than_one_replicas(self):
        if len(self.replicas) <= 1:
            return [ValueError("Too few replicas for this file: " + str(len(self.replicas)))]


    def check_non_public_acls(self):
        """
        Checks that the iRODS object doesn't have associated an ACL giving public access to users to it.
        :param acls:
        :return:
        """
        problems = []
        for acl in self.acls:
            if acl.provides_public_access():
                problems.append(error_types.WrongACLWarning(message="ACL for public access found " + str(acl)))
        return problems


    def check_has_read_permission_ss_group(self):
        """
        Checks if any of the ACLs is for an ss group.
        :param acls:
        :return:
        """
        problems = []
        found_ss_gr_acl = False
        for acl in self.acls:
            if acl.provides_access_for_ss_group():
                found_ss_gr_acl = True
                if not acl.provides_read_permission():
                    problems.append(
                        error_types.WrongACLWarning(message="ACL provides user/group: " + str(acl.access_group) +
                                                            " permission=" + str(acl.permission)))
                break
        if not found_ss_gr_acl:
            problems.append(error_types.MissingACLWarning("There is no ACL for an ss_* group, probably nobody "
                                                          "outside of NPG can access this file"))
        return problems


class IrodsFileMetadata(object):
    def __init__(self, fpath: str=None, fname:str=None, samples=None, libraries=None, studies=None,
                 checksum_in_meta:str=None, checksum_at_upload:str=None, references:List[str]=None,
                 run_ids:List[str]=None, lane_ids:List[str]=None, npg_qc:str=None, target:str=None):
        self.fname = fname
        self.fpath = fpath
        self.samples = samples
        self.libraries = libraries
        self.studies = studies
        self.checksum_in_meta = checksum_in_meta
        self.checksum_at_upload = checksum_at_upload
        self._reference_paths = references
        self.run_ids = run_ids
        self.lane_ids = lane_ids
        self._npg_qc_values = [npg_qc]
        self._target_values = [target]

    @classmethod
    def from_raw_metadata(cls, raw_metadata: IrodsRawFileMetadata):
        irods_metadata = IrodsFileMetadata()
        irods_metadata.fname = raw_metadata.fname
        irods_metadata.dir_path = raw_metadata.dir_path
        irods_metadata.checksum_at_upload = raw_metadata.file_replicas

        # Sample
        irods_metadata.samples = {'name': raw_metadata.get_values_for_attribute('sample'),
                                  'accession_number': raw_metadata.get_values_for_attribute(
                                      'sample_accession_number'),
                                  'internal_id': raw_metadata.get_values_for_attribute('sample_id')
        }

        # Library: Hack to correct NPG mistakes (they submit under library names the actual library ids)
        library_identifiers = raw_metadata.get_values_for_attribute('library') + \
                              raw_metadata.get_values_for_attribute('library_id')
        irods_metadata.libraries = EntityIdentifier.separate_identifiers_by_type(library_identifiers)

        # Study:
        irods_metadata.studies = {'name': raw_metadata.get_values_for_attribute('study'),
                                  'accession_number': raw_metadata.get_values_for_attribute(
                                      'study_accession_number'),
                                  'internal_id': raw_metadata.get_values_for_attribute('study_id')
        }

        irods_metadata.checksum_in_meta = raw_metadata.get_values_for_attribute('md5')
        irods_metadata.run_ids = raw_metadata.get_values_for_attribute('id_run')
        irods_metadata.lane_ids = raw_metadata.get_values_for_attribute('lane')
        irods_metadata._reference_paths = raw_metadata.get_values_for_attribute('reference')
        irods_metadata._npg_qc_values = raw_metadata.get_values_for_attribute('manual_qc')
        irods_metadata._target_values = raw_metadata.get_values_for_attribute('target')
        return irods_metadata

    def get_run_ids(self):
        return self.run_ids

    def get_lane_ids(self):
        return self.lane_ids

    def get_reference_paths(self):
        if len(self._reference_paths) != 1:
            raise error_types.MetadataAttributeCountError(self.fpath, attribute='reference', desired_occurances='1',
                                                          actual_occurances=len(self._reference_paths))
        return self._reference_paths[0]

    def get_references(self):
        return [self.extract_reference_name_from_ref_path(ref) for ref in self._reference_paths]

    def get_npg_qc(self):
        if len(self._npg_qc_values) != 1:
            raise error_types.MetadataAttributeCountError(self.fpath, attribute='npg_qc', desired_occurances='1',
                                                          actual_occurances=len(self._npg_qc_values))
        return self._npg_qc_values[0]

    def get_target(self):
        if len(self._target_values) != 1:
            raise error_types.MetadataAttributeCountError(self.fpath, attribute='target', desired_occurances='1',
                                                          actual_occurances=len(self._target_values))

        return self._target_values[0]


    @classmethod
    def extract_lanelet_name_from_irods_fpath(cls, irods_fpath):
        """
        This method extracts the lanelet name (without extension) from an irods path.
        It checks first that it is an iRODS seq lanelet.
        :raises ValueError if the irods_path param is not a seq/run_id/lanelet.
        :param irods_fpath:
        :return:
        """
        cls.check_is_irods_lanelet_fpath(irods_fpath)
        fname_without_ext = common_utils.extract_fname_without_ext(irods_fpath)
        return fname_without_ext


    @classmethod
    def get_run_from_irods_path(cls, irods_fpath):
        """
            This function extracts the run_id from the filename of the irods_path given as parameter.
        :param irods_fpath:
        :return:
        :raises: ValueError if the path doesnt look like an irods sequencing path or the file is not a lanelet.
        """
        fname = cls.extract_lanelet_name_from_irods_fpath(irods_fpath)
        return cls.get_run_from_irods_fname(fname)


    @classmethod
    def get_run_from_irods_fname(cls, fname):
        cls.check_is_lanelet_filename(fname)
        r = re.compile(irods_consts.LANLET_NAME_REGEX)
        matched_groups = r.match(fname).groupdict()
        return matched_groups['run_id']


    @classmethod
    def get_lane_from_irods_path(cls, irods_fpath):
        cls.check_is_irods_seq_fpath(irods_fpath)
        fname = common_utils.extract_fname_without_ext(irods_fpath)
        return cls.get_lane_from_irods_fname(fname)


    @classmethod
    def get_lane_from_irods_fname(cls, fname):
        cls.check_is_lanelet_filename(fname)
        r = re.compile(irods_consts.LANLET_NAME_REGEX)
        matched_groups = r.match(fname).groupdict()
        return matched_groups['lane_id']


    @classmethod
    def extract_reference_name_from_ref_path(cls, ref_path):
        ref_file_name = common_utils.extract_fname(ref_path)
        if ref_file_name.find(".fa") != -1:
            ref_name = ref_file_name.split(".fa")[0]
            return ref_name
        else:
            raise ValueError("Not a reference file: " + str(ref_path))


    def __str__(self):
        return "Fpath = " + str(self.fpath) + ", fname = " + str(self.fname) + ", samples = " + str(self.samples) + \
               ", libraries = " + str(self.libraries) + ", studies = " + str(self.studies) + ", md5 = " + str(self.md5) \
               + ", ichksum_md5 = " + str(self.ichksum_md5) + ", reference = " + str(self.reference)

    def __repr__(self):
        return self.__str__()

    def run_field_sanity_checks(self):
        problems = []
        if not self.is_checksum(self.checksum_in_meta):
            problems.append(
                error_types.WrongMetadataValue(attribute='Checksum_in_metadata', value=self.checksum_in_meta))

        if not self.is_checksum(self.checksum_at_upload):
            problems.append(
                error_types.WrongMetadataValue(attribute='Checksum_at_upload', value=self.checksum_at_upload))

        for lane in self.lane_ids:
            if not self.is_lane_id(lane):
                problems.append(error_types.WrongMetadataValue(attribute='lane'), value=lane)

        for run in self.run_ids:
            if not self.is_run_id(run):
                problems.append(error_types.WrongMetadataValue(attribute='run_id'), value=run)

        if not self.is_npg_qc(self.get_npg_qc()):
            problems.append(error_types.WrongMetadataValue(attribute='npg_qc'), value=self.get_npg_qc())

        if not self.is_target(self.get_target()):
            problems.append(error_types.WrongMetadataValue(attribute='target', value=self.get_target()))
        return problems

    def check_file_metadata(self, desired_reference: str):
        problems = []
        try:
            self.test_checksum_calculated_vs_metadata()
        except error_types.TestImpossibleToRunError:
            pass
            # TODO: think what to do in this case...
        except error_types.WrongChecksumError as e:
            problems.append(e)

        try:
            self.test_lane_from_fname_vs_metadata(self)
        except error_types.TestImpossibleToRunError as e:
            # problems.append(e)
            pass
            # TODO: not sure
        except error_types.IrodsMetadataAttributeVsFileNameError as e:
            problems.append(e)

        try:
            self.test_run_id_from_fname_vs_metadata(self)
        except error_types.TestImpossibleToRunError as e:
            #problems.append(e)
            #TODO: not sure where to save these...
            pass
        except error_types.IrodsMetadataAttributeVsFileNameError as e:
            problems.append(e)

        try:
            self.test_reference(self, desired_reference)
        except error_types.WrongReferenceError as e:
            problems.append(e)
        except error_types.TestImpossibleToRunError as e:
            pass

        return problems

    @staticmethod
    def _validate_checksum(checksum):
        if not type(checksum) is str:
            raise TypeError("WRONG TYPE: the checksum must be a string, and is: " + str(type(checksum)))
        r = re.compile(irods_consts.MD5_REGEX)
        return True if r.match(checksum) else False

    @staticmethod
    def _validate_run_id(run_id):
        if not type(run_id) in [str, int]:
            raise TypeError("WRONG TYPE: the run_id must be a string or int and is: " + str(type(run_id)))
        r = re.compile(irods_consts.RUN_ID_REGEX)
        return True if r.match(str(run_id)) else False

    @staticmethod
    def _validate_lane_id(lane_id):
        if not type(lane_id) in [str, int]:
            raise TypeError("WRONG TYPE: the lane_id must be either string or int and is: " + str(type(lane_id)))
        r = re.compile(irods_consts.LANE_ID_REGEX)
        return True if r.match(str(lane_id)) else False

    @staticmethod
    def _validate_npg_qc(npg_qc):
        if not type(npg_qc) in [str, int]:
            raise TypeError("WRONG TYPE: the npg_qc must be either string or int and is: " + str(npg_qc))
        r = re.compile(irods_consts.NPG_QC_REGEX)
        return True if r.match(str(npg_qc)) else False


    @staticmethod
    def is_target(target):
        if not type(target) in [str, int]:
            raise TypeError("WRONG TYPE: the target must be either string or int and is: " + str(target))
        r = re.compile(irods_consts.TARGET_REGEX)
        return True if r.match(str(target)) else False


    # @staticmethod
    # def check_is_irods_seq_fpath(fpath):
    #     r = re.compile(irods_consts.IRODS_SEQ_LANELET_PATH_REGEX)
    #     if not r.match(fpath):
    #         raise ValueError("Not an iRODS seq path: " + str(fpath))


    # @staticmethod
    # def check_is_lanelet_filename(fname):
    #     """
    #     Checks if a filename looks like: 1234_5.* or 1234_5#6.*
    #     :param fname: file name
    #     :return: bool
    #     """
    #     r = re.compile(irods_consts.LANLET_NAME_REGEX)
    #     if not r.match(fname):
    #         raise ValueError("Not a lanelet filename: " + str(fname))


    # @staticmethod
    # def check_is_irods_lanelet_fpath(fpath):
    #     """
    #     Checks if a given file path is an irods seq path and that it is a lanelet. e.g. 1234_5.bam, 1234_5#6.cram
    #     :param fpath:
    #     :return:
    #     """
    #     cls.check_is_irods_seq_fpath(fpath)
    #     fname = common_utils.extract_fname_without_ext(fpath)
    #     cls.check_is_lanelet_filename(fname)

    def test_checksum_calculated_vs_metadata(self):
        if self.checksum_in_meta and self.checksum_at_upload:
            if self.checksum_in_meta != self.checksum_at_upload:
                raise error_types.WrongChecksumError(fpath=self.fpath,
                                                     checksum_in_meta=self.checksum_at_upload,
                                                     chksum_at_upload=self.checksum_in_meta)
        else:
            if not self.checksum_in_meta:
                raise error_types.TestImpossibleToRunError(fpath=self.fpath, test_name='Test md5',
                                                           reason='The md5 returned by ichksum is missing')
            if not self.checksum_at_upload:
                raise error_types.TestImpossibleToRunError(fpath=self.fpath, test_name='Test md5',
                                                           reason='The md5 in iRODS metadata is either missing or more than 1.')

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
            raise error_types.TestImpossibleToRunError(fpath=self.fpath, reason=str(e),
                                                       test_name='Check run_id from filename vs. run_id from iRODS metadata')  # 'Cant extract the run id from file name. Not a sequencing file?'
        else:
            if str(self.run_id) != str(run_id_from_fname):
                raise error_types.IrodsMetadataAttributeVsFileNameError(fpath=self.fpath, attribute='run_id',
                                                                        irods_value=self.run_id,
                                                                        filename_value=run_id_from_fname)


    # TODO: actually the user can't know exactly the name of the files - this needs refactoring, in order to associate the name of the ref file with the name of the ref

    def test_reference(self, desired_ref):
        if not self.reference:
            raise error_types.TestImpossibleToRunError(fpath=self.fpath, test_name='Check reference',
                                                       reason='The reference from iRODS metadata is either missing or more than 1.')
        if not desired_ref:
            raise error_types.TestImpossibleToRunError(fpath=self.fpath, test_name='Check_reference',
                                                       reason='Missing desired reference parameter.')
        if self.reference.find(desired_ref) == -1:
            raise error_types.WrongReferenceError(fpath=self.fpath, desired_ref=desired_ref,
                                                  header_ref='not implemented', irods_ref=self.reference)


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
                raise error_types.IrodsMetadataAttributeVsFileNameError(fpath=self.fpath, attribute='lane',
                                                                        irods_value=self.lane_id,
                                                                        filename_value=lane_from_fname)

