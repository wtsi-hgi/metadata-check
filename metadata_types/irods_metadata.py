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
from main import error_types
from main import metadata_utils
from com import utils as common_utils
from irods import constants as irods_consts
from metadata_types.identifiers import EntityIdentifier


class IRODSRawFileMetadata:
    def __init__(self, fname, dir_path, avus_list, md5_at_upload=None):
        self.avus = avus_list
        self.fname = fname
        self.dir_path = dir_path
        self.md5_at_upload = md5_at_upload

    def extract_values_for_attribute(self, attribute):
        results = []
        for avu in self.avus:
            if avu.attribute == attribute:
                results.append(avu.value)
        return results

    def __str__(self):
        return "Location: dir_path = " + str(self.dir_path) + ", fname = " + str(self.fname) + ", samples = " + str(
            self.samples) + \
               ", libraries = " + str(self.libraries) + ", studies = " + str(self.studies) + ", md5_in_meta = " + str(
            self.md5_in_meta) \
               + ", md5_at_upload = " + str(self.md5_on_server) + ", reference = " + str(self.reference)

    def __repr__(self):
        return self.__str__()


class IRODSFileMetadata(object):
    def __init__(self, fpath=None, fname=None, samples=None, libraries=None, studies=None, md5_in_meta=None,
                 md5_at_upload=None, reference=None, run_id=None, lane_id=None, npg_qc=None, target=None):
        self.fname = fname
        self.fpath = fpath
        self.samples = samples
        self.libraries = libraries
        self.studies = studies
        self.md5_in_meta = md5_in_meta
        self.md5_at_upload = md5_at_upload
        self.reference = reference
        self.run_id = run_id
        self.lane_id = lane_id
        self.npg_qc = npg_qc
        self.target = target

    @classmethod
    def from_raw_metadata(cls, raw_metadata: IRODSRawFileMetadata):
        irods_metadata = IRODSFileMetadata()
        irods_metadata.fname = raw_metadata.fname
        irods_metadata.dir_path = raw_metadata.dir_path

        # Sample
        irods_metadata.samples = {'name': raw_metadata.extract_values_for_attribute('sample'),
                                  'accession_number': raw_metadata.extract_values_for_attribute(
                                      'sample_accession_number'),
                                  'internal_id': raw_metadata.extract_values_for_attribute('sample_id')
        }

        # Library: Hack to correct NPG mistakes (they submit under library names the actual library ids)
        library_identifiers = raw_metadata.extract_values_for_attribute('library') + \
                              raw_metadata.extract_values_for_attribute('library_id')
        irods_metadata.libraries = EntityIdentifier.separate_identifiers_by_type(library_identifiers)

        # Study:
        irods_metadata.studies = {'name': raw_metadata.extract_values_for_attribute('study'),
                                  'accession_number': raw_metadata.extract_values_for_attribute(
                                      'study_accession_number'),
                                  'internal_id': raw_metadata.extract_values_for_attribute('study_id')
        }

        irods_metadata.md5_in_meta = raw_metadata.extract_values_for_attribute('md5')
        irods_metadata.md5_at_upload = raw_metadata.md5_at_upload
        irods_metadata.reference = raw_metadata.extract_values_for_attribute('reference')
        irods_metadata.run_id = raw_metadata.extract_values_for_attribute('id_run')
        irods_metadata.lane_id = raw_metadata.extract_values_for_attribute('lane')
        irods_metadata.npg_qc = raw_metadata.extract_values_for_attribute('manual_qc')
        irods_metadata.target = raw_metadata.extract_values_for_attribute('target')

        return irods_metadata


    # @classmethod
    # def from_avus_to_irods_metadata(cls, avus, fpath):
    #     '''
    #     :param avus: data_types.MetaAVU
    #     :param fpath:
    #     :return: an iRODSFileMetadata object
    #     WARNING: this assumes that a file has metadata as the data objects in seq zone - ie assumes there should be
    #     exactly 1 md5, 1 lane id, 1 run id, 1 manual_qc field => won't work for more complex metadata schemes
    #     => ignores avu frequency errors => this should be checked beforehands...somewhere...
    #     '''
    #     fname = common_utils.extract_fname(fpath)
    #     samples = metadata_utils.iRODSUtils.extract_samples_from_irods_metadata(avus)
    #     libraries = metadata_utils.iRODSUtils.extract_libraries_from_irods_metadata(avus)
    #     studies = metadata_utils.iRODSUtils.extract_studies_from_irods_metadata(avus)
    #
    #     md5_list = metadata_utils.iRODSUtils.extract_values_for_key_from_irods_metadata(avus, 'md5')
    #     md5 = md5_list[0] if len(md5_list) == 1 else None
    #
    #     # TODO: actually this is not according to the method's name, it doesn't build up metadata from avus but also queries irods independently
    #     # ichksum_md5 = icommands_wrapper.iRODSChecksumOperations.get_checksum(fpath)
    #
    #     ref_list = metadata_utils.iRODSiCmdsUtils.extract_values_for_key_from_irods_metadata(avus, 'reference')
    #     ref = ref_list[0] if len(ref_list) == 1 else None
    #
    #     # TODO: I don't deal with the exception thrown from extract_reference_name.. if the ref doesn't look like a ref
    #     if ref:
    #         ref = cls.extract_reference_name_from_ref_path(ref)
    #
    #     run_id_list = metadata_utils.iRODSiCmdsUtils.extract_values_for_key_from_irods_metadata(avus, 'id_run')
    #     run_id = run_id_list[0] if len(run_id_list) == 1 else None
    #
    #     lane_id_list = metadata_utils.iRODSiCmdsUtils.extract_values_for_key_from_irods_metadata(avus, 'lane')
    #     lane_id = lane_id_list[0] if len(lane_id_list) == 1 else None
    #
    #     npg_qc_list = metadata_utils.iRODSiCmdsUtils.extract_values_for_key_from_irods_metadata(avus, 'manual_qc')
    #     npg_qc = npg_qc_list[0] if len(npg_qc_list) == 1 else None
    #
    #     target_list = metadata_utils.iRODSiCmdsUtils.extract_values_for_key_from_irods_metadata(avus, 'target')
    #     target = target_list[0] if len(target_list) == 1 else None
    #
    #     return IRODSFileMetadata(fpath=fpath, fname=fname, samples=samples, libraries=libraries,
    #                              studies=studies, md5=md5, reference=ref, run_id=run_id,
    #                              lane_id=lane_id, npg_qc=npg_qc, target=target)


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