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

This file has been created on Feb 10, 2015.
"""

from irods import api as irods_api
from irods import icommands_wrapper
from header_parser import bam_h_analyser as header_analyser
import os
from identifiers import EntityIdentifier as Identif
from com import  utils as common_utils



class HeaderUtils:

    @classmethod
    def sort_entities_by_guessing_id_type(cls, ids_list):
        """
            This function takes a list of ids, which it doesn't know what type they are,
            guesses the id type and then returns a dict containing 3 lists - one for each type of id
            (internal_id, accession_number, name).
            Parameters
            ----------
                ids_list : list - containing together all sorts of ids that identify entities.
            Returns
            -------
                sorted_ids : dict - {'name': list, 'accession_number': list, 'internal_id': list}
        """
        sorted_ids = {'name': [], 'accession_number': [], 'internal_id': []}
        for entity_id in ids_list:
            id_type = Identif.guess_identifier_type(entity_id)
            sorted_ids[id_type].append(entity_id)
        return sorted_ids


    @classmethod
    def _get_file_header_metadata(cls, path, location):
        if location == 'irods':
            full_header = header_analyser.BAMHeaderAnalyser.extract_header_from_irods_file(path)
        elif location == 'lustre':
            full_header = header_analyser.BAMHeaderAnalyser.extract_header_from_file(path)
        else:
            raise ValueError("This function accepts as file location only irods or lustre.")
        parsed_header = header_analyser.BAMHeaderAnalyser.parse_header(full_header)
        header_metadata = header_analyser.BAMHeaderAnalyser.extract_metadata_from_header(parsed_header)
        return header_metadata.rg

    @classmethod
    def get_header_metadata_from_irods_file(cls, irods_path):
        return cls._get_file_header_metadata(irods_path, 'irods')


    @classmethod
    def get_header_metadata_from_lustre_file(cls, lustre_path):
        return cls._get_file_header_metadata(lustre_path, 'lustre')



class iRODSUtils:

    @classmethod
    def retrieve_list_of_bams_by_study_from_irods(cls, study_name):
        avus = {'study': study_name, 'type': 'bam'}
        bams = icommands_wrapper.iRODSMetaQueryOperations.query_by_metadata(avus)
        filtered_bams = icommands_wrapper.iRODSMetaQueryOperations.filter_out_phix_files(bams)
        return filtered_bams

    @classmethod
    def extract_lanelet_name(cls, lanelet_path):
        lanelet_file = os.path.basename(lanelet_path)
        return lanelet_file


    # TODO: test - what if the lanelet is a whole lane (x10 data)? TO add unittest for this!
    @classmethod
    def guess_seq_irods_path_from_lustre_path(cls, lustre_path):
        """
            Applies only for the data delivered by NPG.

        """
        fname = common_utils.extract_fname_from_path(lustre_path)
        run_id = fname.split("_")
        irods_fpath = "/seq/" + run_id[0] + "/" + fname
        return irods_fpath


    @classmethod
    def retrieve_irods_metadata(cls, irods_path):
        return irods_api.iRODSAPI.retrieve_metadata_for_file(irods_path)


    @classmethod
    def extract_values_for_key_from_irods_metadata(cls, avus_list, key):
        results = []
        for avu in avus_list:
            if avu.attribute == key:
                results.append(avu.value)
        return results


    @classmethod
    def get_run_from_irods_path(cls, irods_fpath):
        tokens = irods_fpath.split("/")
        if len(tokens) >= 2 and tokens[1] == 'seq':
            return tokens[-2]
        return ''


    @classmethod
    def get_lane_from_irods_path(cls, irods_fpath):
        fname = os.path.basename(irods_fpath)
        if fname.find("_") != -1:
            lane_id = ''
            lane_token = fname.split("_")[1]
            if lane_token.find("#") != -1:
                lane_id = lane_token.split("#")[0]
            elif lane_token.find(".bam") != -1:
                lane_id = lane_token.split(".bam")[0]
            return lane_id
        return ''

    @classmethod
    def extract_reference_name_from_path(cls, ref_path):
        ref_file_name = os.path.basename(ref_path)
        if ref_file_name.find(".fa") != -1:
            ref_name = ref_file_name.split(".fa")[0]
            return ref_name
        return ''


    @classmethod
    def extract_lanelet_name_from_irods_fpath(cls, irods_fpath):
        fname = os.path.basename(irods_fpath)
        if fname.find("_") == -1:
            return ''
        if fname.find(".bam") != -1:
            return fname.split(".bam")[0]
        return ''


    @classmethod
    def extract_samples_from_irods_metadata(cls, irods_metadata):
        irods_sample_names_list = cls.extract_values_for_key_from_irods_metadata(irods_metadata, 'sample')
        irods_sample_acc_nr_list = cls.extract_values_for_key_from_irods_metadata(irods_metadata, 'sample_accession_number')
        irods_sample_internal_id_list = cls.extract_values_for_key_from_irods_metadata(irods_metadata, 'sample_id')
        irods_samples = {'name': irods_sample_names_list,
                         'accession_number': irods_sample_acc_nr_list,
                         'internal_id': irods_sample_internal_id_list
        }
        return irods_samples

    @classmethod
    def extract_studies_from_irods_metadata(cls, irods_metadata):
        irods_study_names_list = cls.extract_values_for_key_from_irods_metadata(irods_metadata, 'study')
        irods_study_internal_id_list = cls.extract_values_for_key_from_irods_metadata(irods_metadata, 'study_id')
        irods_study_acc_nr_list = cls.extract_values_for_key_from_irods_metadata(irods_metadata, 'study_accession_number')
        irods_studies = {'name': irods_study_names_list,
                         'internal_id': irods_study_internal_id_list,
                         'accession_number': irods_study_acc_nr_list
        }
        return irods_studies


    @classmethod
    def extract_libraries_from_irods_metadata(cls, irods_metadata):
        irods_lib_internal_id_list = cls.extract_values_for_key_from_irods_metadata(irods_metadata, 'library_id')
        if not irods_lib_internal_id_list:
            irods_lib_names_list = cls.extract_values_for_key_from_irods_metadata(irods_metadata, 'library')
            irods_libraries = {'name': irods_lib_names_list}
        else:
            irods_libraries = {'internal_id': irods_lib_internal_id_list}
        return irods_libraries

