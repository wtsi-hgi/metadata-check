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
#{"collection": "/seq/10080", "data_object": "10080_8#64.bam",
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


class IrodsRawFileMetadata:
    def __init__(self, fname: str, dir_path: str, file_replicas: List[IrodsFileReplica]=None, acls: List[IrodsACL]=None):
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
        return self._avus[attribute]

    @classmethod
    def group_attributes(cls, avus):
        avus_grouped = defaultdict(list)
        for avu in avus:
            avus_grouped[avu.attribute].append(avu.value)
        return avus_grouped

    def __str__(self):
        return "Location: dir_path = " + str(self.dir_path) + ", fname = " + str(self.fname) + ", AVUS: " + self._avus\
               + ", md5_at_upload = " + str(self.file_replicas)

    def __repr__(self):
        return self.__str__()


class IrodsFileMetadata(object):
    def __init__(self, fpath: str=None, fname :str=None, samples=None, libraries=None, studies=None,
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