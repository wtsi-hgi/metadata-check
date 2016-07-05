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
import os
from collections import defaultdict, Iterable
from typing import List, Dict, Union, Set

from mcheck.com.operators import Operators
from mcheck.main import error_types
from mcheck.com import wrappers
from mcheck.metadata.common.comparable_metadata import ComparableMetadata
from mcheck.metadata.common.identifiers import EntityIdentifier
from mcheck.metadata.common.attribute_count import AttributeCount
from mcheck.metadata.irods_metadata import constants as irods_consts, avu
from mcheck.results.checks_results import CheckResult
from mcheck.com import utils as common_utils
from mcheck.results.constants import SEVERITY, RESULT
from mcheck.metadata.irods_metadata.acl import IrodsACL
from mcheck.metadata.irods_metadata.file_replica import IrodsFileReplica
from mcheck.check_names import CHECK_NAMES


class IrodsRawFileMetadata(ComparableMetadata):
    def __init__(self, fpath: str, file_replicas: List[IrodsFileReplica]=None,
                 acls: List[IrodsACL]=None, avus: Dict[str, Set]=None):
        self.fpath = fpath
        self.file_replicas = file_replicas if file_replicas else []
        self.acls = acls if acls else []
        self.avus = avus if avus else defaultdict(set)

    @classmethod
    def from_baton_wrapper(cls, data_object):
        fname = data_object.get_name()
        collection = data_object.get_collection_path()
        if data_object.replicas is not None:
            replicas = [IrodsFileReplica.from_baton_wrapper(replica) for replica in data_object.replicas]
        else:
            replicas = []
        if data_object.access_controls is not None:
            acls = [IrodsACL.from_baton_wrapper(ac_item) for ac_item in data_object.access_controls if ac_item]
        else:
            acls = []
        raw_meta = cls(fpath=os.path.join(collection, fname), file_replicas=replicas, acls=acls)
        if data_object.metadata:
            raw_meta.avus = dict(data_object.metadata)
        return raw_meta


    def init_avus_from_avu_tuples(self, avus_list: Set[avu.MetaAVU]) -> None:
        avus_grouped = defaultdict(set)
        for avu in avus_list:
            avus_grouped[avu.attribute].add(avu.value)
        self.avus = avus_grouped

    def get_values_for_attribute(self, attribute: str) -> list:
        found = self.avus.get(attribute)
        return found if found else set()

    def get_values_count_for_attribute(self, attribute: str) -> int:
        return len(self.get_values_for_attribute(attribute))

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
        check_result = CheckResult(check_name=CHECK_NAMES.check_attribute_count,
                                   severity=SEVERITY.IMPORTANT)
        wrong_counts = []
        for avu_count in avu_counts:
            actual_count = self.get_values_count_for_attribute(avu_count.attribute)
            threshold = avu_count.count
            if not self._is_true_comparison(actual_count, threshold, avu_count.operator):
                wrong_counts.append("attribute %s should appear %s %s times and appears %s" % (
                    avu_count.attribute, avu_count.operator, threshold, actual_count))
        if wrong_counts:
            check_result.result = RESULT.FAILURE
            check_result.error_message = ','.join(wrong_counts)
        return check_result


    class ReplicasChecks:

        @classmethod
        def validate_replicas_individually(cls, replicas):
            check_results = []
            for replica in replicas:
                check_results.extend(replica.validate_fields())
            return check_results

        @classmethod
        def check_all_replicas_have_same_checksum(cls, replicas) -> CheckResult:
            result = CheckResult(check_name=CHECK_NAMES.check_all_replicas_same_checksum, severity=SEVERITY.IMPORTANT)
            if not replicas:
                result.executed = False
                result.error_message = ["No replicas to compare with."]
                result.result = None
                return result
            first_replica = replicas[0]
            error_message = ''
            for replica in replicas:
                if not replica.checksum == first_replica.checksum:
                    result.result = RESULT.FAILURE
                    error_message += "Replica: " + str(replica) + " has different checksum than replica: " + str(
                        first_replica)
            if error_message:
                result.error_message = error_message
            return result

        @classmethod
        def check_more_than_one_replicas(cls, replicas) -> CheckResult:
            check_result = CheckResult(check_name=CHECK_NAMES.check_more_than_one_replica, severity=SEVERITY.WARNING)
            if len(replicas) <= 1:
                check_result.executed = True
                check_result.result = RESULT.FAILURE
                check_result.error_message = "File has " + str(len(replicas)) + " replicas"
            return check_result

        # Checking the replicas:
        @classmethod
        def check(cls, replicas):
            check_results = []
            check_results.extend(cls.validate_replicas_individually(replicas))
            check_results.append(cls.check_all_replicas_have_same_checksum(replicas))
            check_results.append(cls.check_more_than_one_replicas(replicas))
            return check_results


    class ACLsChecks:
        @classmethod
        def check_non_public_acls(cls, acls) -> List[CheckResult]:
            """
            Checks that the iRODS object doesn't have associated an ACL giving public access to users to it.
            :param acls:
            :return:
            """
            # problems = []
            check_result = CheckResult(check_name=CHECK_NAMES.check_no_public_acl, severity=SEVERITY.WARNING)
            if not acls:
                check_result.result = None
                check_result.executed = False
                check_result.error_message = "There are no ACLs."
                return check_result
            for acl in acls:
                if acl.provides_public_access():
                    check_result.error_message = error_message = "The following ACL was found: " + str(acl)
                    check_result.result = RESULT.FAILURE
                    break
            return check_result

        @classmethod
        def check_read_permission_exists_for_ss_group(cls, acls) -> List[CheckResult]:
            """
            Checks if any of the ACLs is for an ss group.
            :param acls:
            :return:
            """
            # problems = []
            check_result_read_permission = CheckResult(check_name=CHECK_NAMES.check_ss_irods_group_read_permission,
                                                       severity=SEVERITY.WARNING)
            check_result_ss_group_present = CheckResult(check_name=CHECK_NAMES.check_there_is_ss_irods_group,
                                                        severity=SEVERITY.WARNING)
            found_ss_gr_acl = False
            for acl in acls:
                if acl.provides_access_for_ss_group():
                    found_ss_gr_acl = True
                    if not acl.provides_read_permission():
                        check_result_read_permission.result = RESULT.FAILURE
                        check_result_read_permission.error_message = "ACL found: " + str(acl)
                    break
            if not found_ss_gr_acl:
                check_result_ss_group_present.result = RESULT.FAILURE
                check_result_read_permission.result = RESULT.FAILURE
            return [check_result_ss_group_present, check_result_read_permission]

        @classmethod
        def check_acls_individually(cls, acls):
            check_results = []
            for acl in acls:
                check_results.extend(acl.validate_fields())
            return check_results

        # Check the acls:
        @classmethod
        def check(cls, acls):
            check_results = []
            check_results.extend(cls.check_acls_individually(acls))
            check_results.append(cls.check_non_public_acls(acls))
            check_results.extend(cls.check_read_permission_exists_for_ss_group(acls))
            return check_results


    class CompleteMetadataChecks:
        GENERAL_ATTRIBUTE_FREQUENCY_CONFIG_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                               'conf_files/general.conf')

        @classmethod
        def read_and_parse_config_file(cls, path):
            attributes_frequency = {}
            config_file = open(path)
            for line in config_file:
                line = line.strip()
                tokens = line.split()
                if len(tokens) != 2:
                    raise ValueError(
                        "Non standard config file - each line must have 2 items. This line looks like:" + str(line))
                attribute = tokens[0]
                if not tokens[1].isdigit():
                    raise ValueError("The config file doesn't contain integers as frequencies" + str(line))
                freq = int(tokens[1])
                attributes_frequency[attribute] = freq
            return attributes_frequency


        @classmethod
        def build_freq_dict_from_avus_list(cls, avus_list):
            print("Type of avu list element: %s" % str(avus_list))
            freq_dict = {}
            for attribute, values in avus_list.items():
                freq_dict[attribute] = len(values)
            return freq_dict


        @classmethod
        def check_attributes_have_the_right_frequency(cls, standard_attr_dict, actual_attr_dict):
            check_results = []
            for attr, freq in standard_attr_dict.items():
                if not attr in actual_attr_dict:
                    check_results.append(CheckResult(check_name=CHECK_NAMES.check_attribute_count, executed=True, result=RESULT.FAILURE, error_message="Missing attribute %s" % attr))
                elif freq != actual_attr_dict[attr]:
                    check_results.append(CheckResult(check_name=CHECK_NAMES.check_attribute_count, executed=True,
                                                     result=RESULT.FAILURE,
                                                     error_message="Attribute %s should appear %s times and instead appears %s times" % (attr, freq, actual_attr_dict[attr])))
            return check_results


        @classmethod
        def from_tuples_to_exceptions(cls, tuples_list):
            excs = []
            for attr_name, desired_freq, actual_freq in tuples_list:
                excs.append(error_types.MetadataAttributeCountError(fpath=None, attribute=attr_name,
                                                                    desired_occurances=desired_freq,
                                                                    actual_occurances=actual_freq))
            return excs
            # should return: check_names.check_attribute_count

        @classmethod
        def check_attribute_frequencies(cls, avus):
            #print("PATH To config file: %s" % cls.GENERAL_ATTRIBUTE_FREQUENCY_CONFIG_FILE)
            print("AVUs: %s" % avus)
            general_attribute_frequencies = cls.read_and_parse_config_file(cls.GENERAL_ATTRIBUTE_FREQUENCY_CONFIG_FILE)
            crt_attribute_frequencies = cls.build_freq_dict_from_avus_list(avus)
            #print("General attribute frequencies: %s" % general_attribute_frequencies)
            #print("Crt attribute frequencies: %s" % crt_attribute_frequencies)
            diffs = cls.check_attributes_have_the_right_frequency(general_attribute_frequencies, crt_attribute_frequencies)
            #diffs = cls.get_dict_differences(general_attribute_frequencies, crt_attribute_frequencies)
            print("Diffs: %s" % diffs)
            return diffs

            # @classmethod
            # def check_irods_metadata_is_complete_for_file(cls, fpath, config_path):
            # irods_avus = metadata_utils.iRODSiCmdsUtils.retrieve_irods_avus(fpath)
            #     return check_avus_freq_vs_config_freq(irods_avus, config_path)
            #
            # @classmethod
            # def check_avus_freq_vs_config_freq(cls, avus, config_path):
            #     irods_attr_freq_dict = build_freq_dict_from_avus_list(avus)
            #     config_attr_freq_dict = read_and_parse_config_file(config_path)
            #     return get_dict_differences(config_attr_freq_dict, irods_attr_freq_dict)


    def check_metadata(self, avu_counts=None):
        check_results = []
        check_results.extend(self.ACLsChecks.check(self.acls))
        check_results.extend(self.ReplicasChecks.check(self.file_replicas))
        check_results.extend(self.CompleteMetadataChecks.check_attribute_frequencies(self.avus))
        if avu_counts:
            check_results.append(self.check_attribute_count(avu_counts))
        return check_results

    def __str__(self):
        return "Location: fpath = " + str(self.fpath) + ", AVUS: " + \
               str(self.avus) + ", replicas = " + str(self.file_replicas) + ", acls = " + str(self.acls)

    def __repr__(self):
        return self.__str__()


class IrodsSeqFileMetadata(IrodsRawFileMetadata):
    def __init__(self, fpath: str, samples=None, libraries=None, studies=None,
                 checksum_in_meta:str=None, checksum_at_upload:str=None, references:List[str]=None,
                 run_ids:List[str]=None, lane_ids:List[str]=None, npg_qc:str=None, target:str=None, file_replicas=None,
                 acls=None):
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
        super().__init__(fpath=fpath, file_replicas=file_replicas, acls=acls)

    @classmethod
    def set_attributes_from_avus(cls, obj_to_set):
        # Sample
        obj_to_set.samples = {'name': obj_to_set.get_values_for_attribute('sample'),
                              'accession_number': obj_to_set.get_values_for_attribute(
                                  'sample_accession_number'),
                              'internal_id': obj_to_set.get_values_for_attribute('sample_id')
        }

        # Library: Hack to correct NPG mistakes (they submit under library names the actual library ids)
        library_identifiers = obj_to_set.get_values_for_attribute('library')

        library_identifiers = library_identifiers.union(obj_to_set.get_values_for_attribute('library_id'))
        obj_to_set.libraries = EntityIdentifier.separate_identifiers_by_type(library_identifiers)

        # Study:
        obj_to_set.studies = {'name': obj_to_set.get_values_for_attribute('study'),
                              'accession_number': obj_to_set.get_values_for_attribute(
                                  'study_accession_number'),
                              'internal_id': obj_to_set.get_values_for_attribute('study_id')
        }

        obj_to_set.checksum_in_meta = obj_to_set.get_values_for_attribute('md5')
        obj_to_set._reference_paths = obj_to_set.get_values_for_attribute('reference')
        obj_to_set._npg_qc_values = obj_to_set.get_values_for_attribute('manual_qc')
        obj_to_set._target_values = obj_to_set.get_values_for_attribute('target')
        return obj_to_set

    @classmethod
    def from_baton_wrapper(cls, data_object):
        irods_metadata = super().from_baton_wrapper(data_object)
        irods_metadata.checksum_at_upload = {replica.checksum for replica in irods_metadata.file_replicas}
        irods_metadata.file_replicas = irods_metadata.file_replicas
        irods_metadata.acls = [IrodsACL.from_baton_wrapper(ac_item) for ac_item in data_object.access_controls if
                               ac_item]
        irods_metadata.avus = data_object.metadata
        cls.set_attributes_from_avus(irods_metadata)
        return irods_metadata


    @classmethod
    def from_raw_metadata(cls, raw_metadata: IrodsRawFileMetadata):
        """
        I am relying on the fact that the raw_metadata is a valid object, ie it contains valid values for its fields.
        Hence I am not going to redo the checks on the field values, just take the data for good.
        :param raw_metadata:
        :return:
        """
        irods_metadata = IrodsSeqFileMetadata(raw_metadata.fpath)
        irods_metadata.checksum_at_upload = {replica.checksum for replica in raw_metadata.file_replicas}
        irods_metadata.file_replicas = raw_metadata.file_replicas
        irods_metadata.acls = raw_metadata.acls
        irods_metadata.avus = raw_metadata.avus
        irods_metadata = cls.set_attributes_from_avus(irods_metadata)

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
        npg_qc = self.get_npg_qc()
        if self.get_npg_qc() is None:
            check_npg_qc.result = RESULT.FAILURE
            check_npg_qc.error_message = "Missing npg_qc field"
        elif not self._is_npg_qc_valid(self.get_npg_qc()):
            check_npg_qc.error_message = "This npg_qc field looks invalid: " + str(self.get_npg_qc())
            check_npg_qc.result = RESULT.FAILURE
        return check_npg_qc

    def check_target_field(self):
        check_target_field = CheckResult(check_name=CHECK_NAMES.check_target_field)
        if self.get_target() is None:
            check_target_field.result = RESULT.FAILURE
            check_target_field.error_message = "Missing target field"
        elif not self._is_target_valid(self.get_target()):
            check_target_field.error_message = "The target field looks invalid: " + str(self.get_target())
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


    def validate_fields(self) -> List:
        check_results = []
        upl_checksum_check = self.check_checksum_at_upload_present()
        check_results.append(upl_checksum_check)

        meta_checksum_check = self.check_checksum_in_meta_present()
        check_results.append(meta_checksum_check)

        comp_check = CheckResult(check_name=CHECK_NAMES.check_by_comparison_checksum_in_meta_with_checksum_at_upload)
        if upl_checksum_check.result == RESULT.SUCCESS and meta_checksum_check.result == RESULT.SUCCESS:
            if self.checksum_in_meta != self.checksum_at_upload:
                comp_check.result = RESULT.FAILURE
                comp_check.error_message = "The checksum in metadata = %s different than checksum at upload = %s" % \
                                           (self.checksum_in_meta, self.checksum_at_upload)
            else:
                comp_check.result = RESULT.SUCCESS
        else:
            comp_check.executed = False
            comp_check.result = None
        check_results.append(comp_check)

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
                if ref.lower().find(desired_ref_name.lower()) == -1:
                    check_result.result = RESULT.FAILURE
                    check_result.error_message = "The desired reference is: %s is different thant the metadata reference: %s" % (
                        desired_ref_name, ref)
        return check_result


    class CompleteMetadataChecks(IrodsRawFileMetadata.CompleteMetadataChecks):

        @classmethod
        def check_attribute_frequencies(cls, avus):
            res = super().check_attribute_frequencies(avus)
            #TODO: implement the library-specific code when we know the requirements
            return res


    def check_metadata(self, desired_reference: str=None) -> List[CheckResult]:
        check_results = []
        check_results.extend(super().check_metadata())
        check_results.extend(self.validate_fields())
        if desired_reference:
            check_results.append(self.check_reference(desired_reference))
        return check_results


    def __str__(self):
        return "Fpath = " + str(self.fpath) + ", samples = " + str(self.samples) + \
               ", libraries = " + str(self.libraries) + ", studies = " + str(self.studies) + ", md5 = " + str(
            self.checksum_in_meta) \
               + ", ichksum_md5 = " + str(self.checksum_at_upload) + ", reference = " + str(self.get_reference_paths())

    def __repr__(self):
        return self.__str__()
