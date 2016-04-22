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
from typing import List, Dict, Union, Set

from mcheck.com.operators import Operators
from mcheck.main import error_types
from mcheck.com import wrappers
from mcheck.irods import data_types
from mcheck.metadata.common.identifiers import EntityIdentifier
from mcheck.metadata.common.attribute_count import AttributeCount
from mcheck.results.checks_results import CheckResult
from mcheck.com import utils as common_utils
from mcheck.irods import constants as irods_consts
from mcheck.results.constants import SEVERITY
from mcheck.metadata.irods_metadata.acl import IrodsACL
from mcheck.metadata.irods_metadata.file_replica import IrodsFileReplica


class IrodsRawFileMetadata:
    def __init__(self, fname: str, dir_path: str, file_replicas: List[IrodsFileReplica]=None,
                 acls: List[IrodsACL]=None):
        self.fname = fname
        self.dir_path = dir_path
        self.file_replicas = file_replicas
        self.acls = acls
        self._attributes = defaultdict(set)

    @staticmethod
    def from_baton_wrapper(data_object):
        fname = data_object.get_name()
        collection = data_object.get_collection_path()
        replicas = [IrodsFileReplica.from_baton_wrapper(replica) for replica in data_object.replicas]
        print("ACLS before initializing: %s" % data_object.acl)
        acls = [IrodsACL.from_baton_wrapper(ac_item) for ac_item in data_object.acl if ac_item]
        raw_meta = IrodsRawFileMetadata(fname=fname, dir_path=collection, file_replicas=replicas, acls=acls)
        if data_object.metadata:
            raw_meta.set_attributes_from_dict(data_object.metadata.to_dict())
        return raw_meta


    def set_attributes_from_avus(self, avus_list: Set[data_types.MetaAVU]) -> None:
        self._attributes = IrodsRawFileMetadata._group_avus_per_attribute(avus_list)

    def set_attributes_from_dict(self, avus_dict: Dict[str, Set[str]]) -> None:
        if not type(avus_dict) == dict:
            raise TypeError("The avus_dict parameter of set_attributes_from_dict must be a dict, and is a {0}".format(
                str(type(avus_dict))))
        self._attributes = avus_dict

    def get_values_for_attribute(self, attribute: str) -> list:
        found = self._attributes.get(attribute)
        return found if found else set()

    def get_values_count_for_attribute(self, attribute: str) -> int:
        return len(self.get_values_for_attribute(attribute))

    @staticmethod
    def _group_avus_per_attribute(avus: List[data_types.MetaAVU]) -> Dict[str, Set[str]]:
        avus_grouped = defaultdict(set)
        for avu in avus:
            avus_grouped[avu.attribute].add(avu.value)
        return avus_grouped

    def validate_fields(self) -> List[CheckResult]:
        problems = []
        for replica in self.file_replicas:
            problems.extend(replica.validate_fields())
        for acl in self.acls:
            problems.extend(acl.validate_fields())
        return problems

    @staticmethod
    def _is_true_comparison(left_operand: int, right_operand: int, operator: str) -> bool:
        if operator == Operators.EQUAL:
            return left_operand == right_operand
        elif operator == Operators.GREATER_THAN:
            return left_operand > right_operand
        elif operator == Operators.LESS_THAN:
            return left_operand < right_operand

    def check_attribute_count(self, avu_counts: List[AttributeCount]) -> List[CheckResult]:
        problems = []
        for avu_count in avu_counts:
            actual_count = self.get_values_count_for_attribute(avu_counts.attribute)
            threshold = avu_count.count
            if not self._is_true_comparison(actual_count, threshold, avu_count.operator):
                error_msg = "Attribute: " + str(avu_count.attribute) + " appears: " + str(actual_count) + \
                            " and should appear: " + str(avu_count.operator) + " " + str(threshold)
                problems.append(CheckResult(check_name="Check attribute count is as configured",
                                            severity=SEVERITY.IMPORTANT, error_message=error_msg))
        return problems

    def check_all_replicas_have_same_checksum(self) -> List[CheckResult]:
        if not self.file_replicas:
            return []
        problems = []
        first_replica = self.file_replicas[0]
        for replica in self.file_replicas:
            if not replica.checksum == first_replica.checksum:
                problems.append(CheckResult(check_name="Check all replicas have the same checksum",
                                            error_message="Replica: " + str(replica) +
                                                          " has different checksum than replica: " + str(
                                                first_replica)))
        return problems

    def check_more_than_one_replicas(self) -> List[CheckResult]:
        problems = []
        if len(self.file_replicas) <= 1:
            problems.append(CheckResult(check_name="Check that file has more than 1 replica", error_message="File has "
                                                                            + str(len(self.file_replicas)) + " replicas"))
        return problems

    def check_non_public_acls(self) -> List[CheckResult]:
        """
        Checks that the iRODS object doesn't have associated an ACL giving public access to users to it.
        :param acls:
        :return:
        """
        problems = []
        for acl in self.acls:
            if acl.provides_public_access():
                problems.append(CheckResult(check_name="Check there are no public ACLS",
                                            error_message="The following ACL was found: " + str(acl)))
        return problems


    def check_has_read_permission_ss_group(self) -> List[CheckResult]:
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
                    problems.append(CheckResult(check_name="Check that the permission for ss_<id> group is READ",
                                                error_message="ACL found: " + str(acl)))
                break
        if not found_ss_gr_acl:
            problems.append(CheckResult(check_name="Check there is at least one ss_<id> group that has access to data"))
        return problems


    def __str__(self):
        return "Location: dir_path = " + str(self.dir_path) + ", fname = " + str(self.fname) + ", AVUS: " + \
               str(self._attributes) + ", md5_at_upload = " + str(self.file_replicas)

    def __repr__(self):
        return self.__str__()


class IrodsSeqFileMetadata(object):
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
        self._reference_paths = references if references else []
        self.run_ids = run_ids if run_ids else []
        self.lane_ids = lane_ids if lane_ids else []
        self._npg_qc_values = [npg_qc]
        self._target_values = [target]

    @classmethod
    def from_raw_metadata(cls, raw_metadata: IrodsRawFileMetadata):
        irods_metadata = IrodsSeqFileMetadata()
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
        library_identifiers = raw_metadata.get_values_for_attribute('library')\

        library_identifiers = library_identifiers.union(raw_metadata.get_values_for_attribute('library_id'))
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

    def get_run_ids(self) -> List[str]:
        return self.run_ids

    def get_lane_ids(self) -> List[str]:
        return self.lane_ids

    def get_reference_paths(self) -> List[str]:
        if len(self._reference_paths) != 1:
            return []
        return list(self._reference_paths)[0]

    def get_references(self) -> List[str]:
        return [self.extract_reference_name_from_ref_path(ref) for ref in self._reference_paths]

    def get_npg_qc(self) -> Union[str, None]:
        if len(self._npg_qc_values) != 1:
            return None
        return list(self._npg_qc_values)[0]

    def get_target(self) -> Union[str, None]:
        if len(self._target_values) != 1:
            return None
        return list(self._target_values)[0]

    @classmethod
    def extract_reference_name_from_ref_path(cls, ref_path: str) -> str:
        ref_file_name = common_utils.extract_fname(ref_path)
        if ref_file_name.find(".fa") != -1:
            ref_name = ref_file_name.split(".fa")[0]
            return ref_name
        else:
            raise ValueError("Not a reference file: " + str(ref_path))


    @staticmethod
    @wrappers.check_args_not_none
    def _is_checksum_valid(checksum):
        if not type(checksum) is str:
            raise TypeError("WRONG TYPE: the checksum must be a string, and is: " + str(type(checksum)))
        r = re.compile(irods_consts.MD5_REGEX)
        return True if r.match(checksum) else False

    @staticmethod
    @wrappers.check_args_not_none
    def _is_run_id_valid(run_id):
        if not type(run_id) in [str, int]:
            raise TypeError("WRONG TYPE: the run_id must be a string or int and is: " + str(type(run_id)))
        r = re.compile(irods_consts.RUN_ID_REGEX)
        return True if r.match(str(run_id)) else False

    @staticmethod
    @wrappers.check_args_not_none
    def _is_lane_id_valid(lane_id):
        if not type(lane_id) in [str, int]:
            raise TypeError("WRONG TYPE: the lane_id must be either string or int and is: " + str(type(lane_id)))
        r = re.compile(irods_consts.LANE_ID_REGEX)
        return True if r.match(str(lane_id)) else False

    @staticmethod
    @wrappers.check_args_not_none
    def _is_npg_qc_valid(npg_qc):
        if not type(npg_qc) in [str, int]:
            raise TypeError("WRONG TYPE: the npg_qc must be either string or int and is: " + str(npg_qc))
        r = re.compile(irods_consts.NPG_QC_REGEX)
        return True if r.match(str(npg_qc)) else False

    @staticmethod
    @wrappers.check_args_not_none
    def _is_target_valid(target):
        if not type(target) in [str, int]:
            raise TypeError("WRONG TYPE: the target must be either string or int and is: " + str(target))
        r = re.compile(irods_consts.TARGET_REGEX)
        return True if r.match(str(target)) else False

    def validate_fields(self) -> List:
        problems = []
        if self.checksum_in_meta and not self._is_checksum_valid(self.checksum_in_meta):
            problems.append(
                CheckResult(check_name="Check that checksum in metadata is valid",
                            error_message="The checksum looks invalid: " +
                                          str(self.checksum_in_meta)))

        if self.checksum_at_upload and not self._is_checksum_valid(self.checksum_at_upload):
            problems.append(
                CheckResult(check_name="Check that checksum at upload is valid",
                            error_message="The checksum looks invalid: " + str(self.checksum_at_upload)))
        if self.lane_ids:
            for lane in self.lane_ids:
                if lane and not self._is_lane_id_valid(lane):
                    problems.append(CheckResult(check_name="Check that the lane is valid",
                                                error_message="This lane id looks invalid: " + str(lane)))

        if self.run_ids:
            for run in self.run_ids:
                if run and not self._is_run_id_valid(run):
                    problems.append(CheckResult(check_name="Check that the run id is valid",
                                                error_message="This run_id looks invalid: " + str(run)))

        if not self.get_npg_qc() is None and not self._is_npg_qc_valid(self.get_npg_qc()):
            problems.append(CheckResult(check_name="Check that the NPG QC field is valid",
                                        error_message="This npg_qc field looks invalid: " + str(self.get_npg_qc())))

        if not self.get_target() is None and not self._is_target_valid(self.get_target()):
            problems.append(CheckResult(check_name="Check that the target field is valid",
                                        error_message="The target field looks invalid: " + str(self.get_target())))
        return problems


    def check_checksum_calculated_vs_metadata(self):
        problems = []
        check_name = "Check that the checksum in metadata = checksum at upload"
        if self.checksum_in_meta and self.checksum_at_upload:
            if self.checksum_in_meta != self.checksum_at_upload:
                problems.append(CheckResult(check_name=check_name,
                                            error_message="The checksum in metadata = %s different than checksum at "
                                                          "upload = %s" % (
                                                              self.checksum_at_upload, self.checksum_in_meta)))
        else:
            if not self.checksum_in_meta:
                problems.append(CheckResult(check_name=check_name,
                                            executed=False, result=None,
                                            error_message="The checksum in metadata is missing"))
            if not self.checksum_at_upload:
                problems.append((CheckResult(check_name=check_name,
                                             executed=False, result=None,
                                             error_message="The checksum at upload is missing")))
        return problems


    def check_reference(self, desired_ref_name: str) -> List[CheckResult]:
        problems = []
        check_name = "Check that the reference for this file is the one desired"
        if not self.get_references():
            problems.append(CheckResult(check_name=check_name, executed=False, result=None,
                                        error_message="There is no reference for this file in the metadata"))
        if not desired_ref_name:
            problems.append(CheckResult(check_name=check_name, executed=False, result=None,
                                        error_message="The desired reference wasn't provided in order "
                                                      "to compare it with the reference in metadata."))
        for ref in self.get_references():
            if ref.find(desired_ref_name) == -1:
                problems.append(CheckResult(check_name=check_name,
                                            error_message="The desired reference is: %s is different thant the metadata "
                                                          "reference: %s" % (desired_ref_name, ref)))
        return problems

    def check_file_metadata(self, desired_reference: str=None) -> List[CheckResult]:
        problems = []
        problems.extend(self.check_checksum_calculated_vs_metadata())
        problems.extend(self.check_reference(self, desired_reference))
        return problems


    def __str__(self):
        return "Fpath = " + str(self.fpath) + ", fname = " + str(self.fname) + ", samples = " + str(self.samples) + \
               ", libraries = " + str(self.libraries) + ", studies = " + str(self.studies) + ", md5 = " + str(self.checksum_in_meta) \
               + ", ichksum_md5 = " + str(self.checksum_at_upload) + ", reference = " + str(self.get_reference_paths())

    def __repr__(self):
        return self.__str__()




# NOT USED - tests to be excluded, too specific, irelevant
class IrodsSeqLaneletFileMetadata(IrodsSeqFileMetadata):
    @classmethod
    def extract_lanelet_name_from_irods_fpath(cls, irods_fpath):
        """
        This method extracts the lanelet name (without extension) from an irods_metadata path.
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
        :raises: ValueError if the path doesnt look like an irods_metadata sequencing path or the file is not a lanelet.
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

    @staticmethod
    def check_is_irods_seq_fpath(fpath):
        r = re.compile(irods_consts.IRODS_SEQ_LANELET_PATH_REGEX)
        if not r.match(fpath):
            raise ValueError("Not an iRODS seq path: " + str(fpath))


    @staticmethod
    def check_is_lanelet_filename(fname):
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
        Checks if a given file path is an irods_metadata seq path and that it is a lanelet. e.g. 1234_5.bam, 1234_5#6.cram
        :param fpath:
        :return:
        """
        cls.check_is_irods_seq_fpath(fpath)
        fname = common_utils.extract_fname_without_ext(fpath)
        cls.check_is_lanelet_filename(fname)

    def check_file_metadata(self, desired_reference: str):
        problems = []
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
            # problems.append(e)
            # TODO: not sure where to save these...
            pass
        except error_types.IrodsMetadataAttributeVsFileNameError as e:
            problems.append(e)

        return problems