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
from collections import defaultdict, Iterable
from typing import List, Dict, Union, Set

from mcheck.com.operators import Operators
from mcheck.main import error_types
from mcheck.com import wrappers
from mcheck.metadata.common.identifiers import EntityIdentifier
from mcheck.metadata.common.attribute_count import AttributeCount
from mcheck.metadata.irods_metadata import constants as irods_consts, avu
from mcheck.results.checks_results import CheckResult
from mcheck.com import utils as common_utils
from mcheck.results.constants import SEVERITY, RESULT
from mcheck.metadata.irods_metadata.acl import IrodsACL
from mcheck.metadata.irods_metadata.file_replica import IrodsFileReplica
from mcheck.check_names import CHECK_NAMES


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
        acls = [IrodsACL.from_baton_wrapper(ac_item) for ac_item in data_object.access_controls if ac_item]
        raw_meta = IrodsRawFileMetadata(fname=fname, dir_path=collection, file_replicas=replicas, acls=acls)
        if data_object.metadata:
            raw_meta.set_attributes_from_dict(dict(data_object.metadata))
        return raw_meta


    def set_attributes_from_avus(self, avus_list: Set[avu.MetaAVU]) -> None:
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
    def _group_avus_per_attribute(avus: List[avu.MetaAVU]) -> Dict[str, Set[str]]:
        avus_grouped = defaultdict(set)
        for avu in avus:
            avus_grouped[avu.attribute].add(avu.value)
        return avus_grouped

    def validate_fields(self) -> List[CheckResult]:
        check_results = []
        for replica in self.file_replicas:
            check_results.extend(replica.validate_fields())
        for acl in self.acls:
            check_results.extend(acl.validate_fields())
        return check_results

    @staticmethod
    def _is_true_comparison(left_operand: int, right_operand: int, operator: str) -> bool:
        if operator == Operators.EQUAL:
            return left_operand == right_operand
        elif operator == Operators.GREATER_THAN:
            return left_operand > right_operand
        elif operator == Operators.LESS_THAN:
            return left_operand < right_operand
        else:
            raise ValueError("Operator not defined: %s. It needs to be one of: <>=" % str(operator))

    def check_attribute_count(self, avu_counts: List[AttributeCount]) -> List[CheckResult]:
        check_result = CheckResult(check_name=CHECK_NAMES.attribute_count_check,
                                            severity=SEVERITY.IMPORTANT)
        wrong_counts = []
        for avu_count in avu_counts:
            actual_count = self.get_values_count_for_attribute(avu_count.attribute)
            threshold = avu_count.count
            if not self._is_true_comparison(actual_count, threshold, avu_count.operator):
                wrong_counts.append("attribute %s should appear %s %s times and appears %s" % (avu_count.attribute, avu_count.operator, threshold, actual_count))
        if wrong_counts:
            check_result.result = RESULT.FAILURE
            check_result.error_message = ','.join(wrong_counts)
        return [check_result]

    def check_all_replicas_have_same_checksum(self) -> List[CheckResult]:
        result = CheckResult(check_name=CHECK_NAMES.check_all_replicas_same_checksum, severity=SEVERITY.IMPORTANT)
        if not self.file_replicas:
            result.result = RESULT.FAILURE
            return [result]
        first_replica = self.file_replicas[0]
        error_message = ''
        for replica in self.file_replicas:
            if not replica.checksum == first_replica.checksum:
                result.result = RESULT.FAILURE
                error_message += "Replica: " + str(replica) + " has different checksum than replica: " + str(first_replica)
        if error_message:
            result.error_message = error_message
        return [result]

    def check_more_than_one_replicas(self) -> List[CheckResult]:
        check_result = CheckResult(check_name=CHECK_NAMES.check_more_than_one_replica, severity=SEVERITY.WARNING)
        if len(self.file_replicas) <= 1:
            check_result.result = RESULT.FAILURE
            check_result.error_message="File has " + str(len(self.file_replicas)) + " replicas"
        return [check_result]

    def check_non_public_acls(self) -> List[CheckResult]:
        """
        Checks that the iRODS object doesn't have associated an ACL giving public access to users to it.
        :param acls:
        :return:
        """
        #problems = []
        check_result = CheckResult(check_name=CHECK_NAMES.check_no_public_acl, severity=SEVERITY.WARNING)
        for acl in self.acls:
            if acl.provides_public_access():
                check_result.error_message = error_message="The following ACL was found: " + str(acl)
                check_result.result = RESULT.FAILURE
                break
        return [check_result]


    def check_has_read_permission_ss_group(self) -> List[CheckResult]:
        """
        Checks if any of the ACLs is for an ss group.
        :param acls:
        :return:
        """
        #problems = []
        check_result_read_permission = CheckResult(check_name=CHECK_NAMES.check_ss_irods_group_read_permission, severity=SEVERITY.WARNING)
        check_result_ss_group_present = CheckResult(check_name=CHECK_NAMES.check_there_is_ss_irods_group, severity=SEVERITY.WARNING)
        found_ss_gr_acl = False
        for acl in self.acls:
            if acl.provides_access_for_ss_group():
                found_ss_gr_acl = True
                if not acl.provides_read_permission():
                    check_result_read_permission.result = RESULT.FAILURE
                    check_result_read_permission.error_message="ACL found: " + str(acl)
                break
        if not found_ss_gr_acl:
            check_result_ss_group_present.result = RESULT.FAILURE
        return [check_result_ss_group_present, check_result_read_permission]

    def check_metadata(self):
        check_results = []
        check_results.extend(self.validate_fields())
        check_results.extend(self.check_has_read_permission_ss_group())
        check_results.extend(self.check_non_public_acls())
        check_results.extend(self.check_more_than_one_replicas())
        check_results.extend(self.check_all_replicas_have_same_checksum())
        return check_results

    def __str__(self):
        return "Location: dir_path = " + str(self.dir_path) + ", fname = " + str(self.fname) + ", AVUS: " + \
               str(self._attributes) + ", replicas = " + str(self.file_replicas) + ", acls = " + str(self.acls)

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
        """
        I am relying on the fact that the raw_metadata is a valid object, ie it contains valid values for its fields.
        Hence I am not going to redo the checks on the field values, just take the data for good.
        :param raw_metadata:
        :return:
        """
        irods_metadata = IrodsSeqFileMetadata()
        irods_metadata.fname = raw_metadata.fname
        irods_metadata.dir_path = raw_metadata.dir_path
        irods_metadata.checksum_at_upload = {replica.checksum for replica in raw_metadata.file_replicas}

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
        irods_metadata._reference_paths = raw_metadata.get_values_for_attribute('reference')
        irods_metadata._npg_qc_values = raw_metadata.get_values_for_attribute('manual_qc')
        irods_metadata._target_values = raw_metadata.get_values_for_attribute('target')
        return irods_metadata


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
    def _is_npg_qc_valid(npg_qc):
        if not type(npg_qc) in [str, int]:
            return False
        r = re.compile(irods_consts.NPG_QC_REGEX)
        return True if r.match(str(npg_qc)) else False


    @staticmethod
    def _is_target_valid(target):
        if not type(target) in [str, int]:
            return False
        r = re.compile(irods_consts.TARGET_REGEX)
        return True if r.match(str(target)) else False


    def check_npg_qc_field(self):
        check_npg_qc = CheckResult(check_name=CHECK_NAMES.check_npg_qc_field)
        if not self.get_npg_qc():
            check_npg_qc.result = RESULT.FAILURE
            check_npg_qc.error_message = "Missing npg_qc field"
        if not self._is_npg_qc_valid(self.get_npg_qc()):
            check_npg_qc.error_message="This npg_qc field looks invalid: " + str(self.get_npg_qc())
            check_npg_qc.result = RESULT.FAILURE
        return check_npg_qc

    def check_target_field(self):
        check_target_field = CheckResult(check_name=CHECK_NAMES.check_target_field)
        if not self.get_target():
            check_target_field.result = RESULT.FAILURE
            check_target_field.error_message = "Missing target field"
        if not self._is_target_valid(self.get_target()):
            check_target_field.error_message="The target field looks invalid: " + str(self.get_target())
            check_target_field.result = RESULT.FAILURE
        return check_target_field

    def check_checksum_in_meta_present(self):
        check_result = CheckResult(check_name=CHECK_NAMES.check_checksum_in_metadata_present, severity=SEVERITY.WARNING)
        if self.checksum_in_meta:
            check_result.result = RESULT.SUCCESS

        else:
            check_result.result = RESULT.FAILURE
            check_result.error_message = "Missing checksum from metadata"
        return check_result


    def check_checksum_at_upload_present(self):
        check_result = CheckResult(check_name=CHECK_NAMES.check_checksum_at_upload_present)
        if self.checksum_at_upload:
            if type(self.checksum_at_upload) is Iterable and len(set(self.checksum_at_upload)) > 1:
                check_result.result = RESULT.FAILURE
                check_result.error_message = "Different checksum values at upload (ichksum)"
            else:
                check_result.result = RESULT.SUCCESS
        else:
            check_result.result = RESULT.FAILURE
            check_result.error_message = "Missing checksum from ichksum result"
        return check_result


    def checksum_comparison_check(self):
        check_result = CheckResult(check_name=CHECK_NAMES.check_by_comparison_checksum_in_meta_with_checksum_at_upload)
        if self.checksum_in_meta != self.checksum_at_upload:
            check_result.result = RESULT.FAILURE
            check_result.error_message = "The checksum in metadata = %s different than checksum at upload = %s" % \
                                         (self.checksum_at_upload, self.checksum_in_meta)
        return check_result


    def validate_fields(self) -> List:
        check_results = []
        upl_checksum_check = self.check_checksum_at_upload_present()
        check_results.append(upl_checksum_check)

        meta_checksum_check = self.check_checksum_in_meta_present()
        check_results.append(meta_checksum_check)

        if upl_checksum_check.result == RESULT.SUCCESS and meta_checksum_check.result == RESULT.SUCCESS:
            check_results.append(self.checksum_comparison_check())
        else:
            check_results.append(CheckResult(CHECK_NAMES.check_by_comparison_checksum_in_meta_with_checksum_at_upload, executed=False, result=RESULT.FAILURE))

        check_npg_qc = self.check_npg_qc_field()
        check_results.append(check_npg_qc)

        check_target_field = self.check_target_field()
        check_results.append(check_target_field)
        return check_results


    def check_reference(self, desired_ref_name: str) -> List[CheckResult]:
        check_result = CheckResult(check_name=CHECK_NAMES.check_desired_reference)
        check_result.error_message = []
        if not self.get_references():
            check_result.result = None
            check_result.executed = False
            check_result.error_message.append("Missing reference from the metadata")
        if not desired_ref_name:
            check_result.result = None
            check_result.executed = False
            check_result.error_message.append("Missing desired reference parameter")
        if not check_result.error_message:
            for ref in self.get_references():
                if ref.find(desired_ref_name) == -1:
                    check_result.result = RESULT.FAILURE
                    check_result.error_message = "The desired reference is: %s is different thant the metadata reference: %s" % (desired_ref_name, ref)
        return check_result

    def check_metadata(self, desired_reference: str=None) -> List[CheckResult]:
        check_results = []
        check_results.extend(self.validate_fields())
        if desired_reference:
            check_results.append(self.check_reference(desired_reference))
        return check_results


    def __str__(self):
        return "Fpath = " + str(self.fpath) + ", fname = " + str(self.fname) + ", samples = " + str(self.samples) + \
               ", libraries = " + str(self.libraries) + ", studies = " + str(self.studies) + ", md5 = " + str(self.checksum_in_meta) \
               + ", ichksum_md5 = " + str(self.checksum_at_upload) + ", reference = " + str(self.get_reference_paths())

    def __repr__(self):
        return self.__str__()
