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

from . import irods_metadata
from irods import api as irods_api
from irods import icommands_wrapper
from irods import data_types
from header_parser import sam_header_analyser as header_analyser
import os
from .identifiers import EntityIdentifier as Identif
from com import  utils as common_utils
from . import error_types
from collections import defaultdict


class GeneralUtils:

    @classmethod
    def check_same_entities(cls, seqsc_entities, entity_type):
        problems = []
        id_types = list(seqsc_entities.keys())
        for i in range(1, len(id_types)-1):
            if seqsc_entities.get(id_types[i-1]) and seqsc_entities.get(id_types[i]):
                if not set(seqsc_entities.get(id_types[i-1])) == set(seqsc_entities.get(id_types[i])):
                    problems.append(str(error_types.DiffEntitiesRetrievedFromSeqscapeByDiffIdTypesError(entity_type=entity_type,
                                                                                         id_type1=id_types[i-1],
                                                                                         id_type2=id_types[i],
                                                                                         entities_set1=seqsc_entities[id_types[i-1]],
                                                                                         entities_set2=seqsc_entities[id_types[i]])))
        return problems


    @classmethod
    def filter_out_non_ids(cls, ids_list):
        return [id for id in ids_list if id not in ['N/A', 'undefined', 'unspecified']]

    # ugly method - these things should be separated (filtering out, reporting errors, and putting together the right error to be returned directly to the user)
    # plus I silently access the fpath field from this object, dirty!!!
    @classmethod
    def filter_out_non_entities(cls, fpath, entity_dict, entity_type):
        filtered_entities = {}
        problems = []
        for id_type, ids_list in list(entity_dict.items()):
            filtered_ids = cls.filter_out_non_ids(ids_list)
            non_ids = set(ids_list).difference(set(filtered_ids))
            problems.extend([error_types.WrongMetadataValue(fpath=fpath, attribute=str(entity_type)+'_'+str(id_type), value=id) for id in non_ids])
            filtered_entities[id_type] = filtered_ids
        return filtered_entities, problems



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
    def _get_parsed_header(cls, path, location):
        if location == 'irods':
            full_header = header_analyser.BAMHeaderAnalyser.extract_header_from_irods_file(path)
        elif location == 'lustre':
            full_header = header_analyser.BAMHeaderAnalyser.extract_header_from_file(path)
        else:
            raise ValueError("This function accepts as file location only irods or lustre.")
        parsed_header = header_analyser.BAMHeaderAnalyser.parse_header(full_header)
        header_metadata = header_analyser.BAMHeaderAnalyser.extract_metadata_from_header(parsed_header)
        return header_metadata

    @classmethod
    def get_parsed_header_from_irods_file(cls, irods_path):
        return cls._get_parsed_header(irods_path, 'irods')


    @classmethod
    def get_parsed_header_from_lustre_file(cls, lustre_path):
        return cls._get_parsed_header(lustre_path, 'lustre')


class iRODSUtils(object):

    @classmethod
    def extract_lanelet_name(cls, irods_path):
        lanelet_file = os.path.basename(irods_path)
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



import json
import ijson

class iRODSBatonUtils(iRODSUtils):

    def reader(self):
        f = open('main/dddx10_avu_acls_checksum.txt', 'r')
        objs = ijson.items(f, "")
        #objs = [o['collection'] for o in objs]
        for o in objs:
            for subitem in o:
                found = False
                checksum = None
                for attr, val in list(subitem.items()):
                    #print "ATTR: " + str(attr) + " VAL = " + str(val) + "\n"
                    if attr == 'data_object' and val == '14633_3.cram':
                        found = True
                    if attr == 'checksum':
                        checksum = val
                if checksum and found:
                    print("CHECKSUM: " + str(checksum))

                    if attr == 'avus':
                        #avus = json.loads(val)
                        print("AFTER json load: " + str(val))
                        for avu in val:
                            print("A = " + str(avu['attribute']) + " V = " + str(avu['value']) + "\n")
                        for a, v in list(attr.items()):
                            print("A = " + str(a) + " V = " + str(v) + "\n")

            #print "COLL: " + str(o['collection']) + " \n"

    @classmethod
    def from_metalist_results_to_avus(cls, search_results_json):
        """
            This method takes as parameter the json result of a metaquery containing avus and checksum,
            and turns the json into a dict having as key a fpath, and as value: dict of
            [MetaAVU(), MetaAVU()]
        :param search_results_json:
        :param filters: optional (not implemented yet)
        :return: dict key = fpath, value = {'avus' : [MetaAVU(), MetaAVU()], 'checksum' : 'the_result_of_ichksum'}
        """
        do_avus = []
        data_dict = json.loads(search_results_json)
        for do_item, do_item_val in list(data_dict.items()):
            if do_item == 'avus':
                for avu in do_item_val:
                    avu_obj = data_types.MetaAVU(attribute=str(avu['attribute']), value=str(avu['value']))  # MetaAVU = namedtuple('MetaAVU', ['attribute', 'value'])    # list of attribute-value tuples
                    do_avus.append(avu_obj)
            # TODO: sometimes there is an error here instead of a list of avus !!!!
        return do_avus


    @classmethod
    def _parse_metaquery_result(cls, metaquery_result, fields_list):
        """
        :param metaquery_result:  metaquery element to parse (usually a dict)
        :param fields_list: the fields of interest to extract from the json
        :return:
        """
        result = []
        coll, do = None, None
        for item, item_val in list(metaquery_result.items()):
            if str(item) == 'collection':
                coll = item_val
            elif str(item) == 'data_object':
                do = item_val
            else:
                avu = data_types.MetaAVU(attribute=str(item), value=str(item_val))
                result.append(avu)
        #     if item in fields_list:
        #         result[item] = item_val
        return result, coll, do

    @classmethod
    def from_metaquery_results_to_fpaths_and_avus(cls, search_results_json):
        """
            This method takes as parameter the json result of a metaquery containing avus and checksum,
            and turns the json into a dict having as key a fpath, and as value: dict of
            {'avus' : [MetaAVU(), MetaAVU()], 'checksum' : 'the_result_of_ichksum'}
        :param search_results_json:
        :param filters: optional (not implemented yet)
        :return: dict key = fpath, value = {'avus' : [MetaAVU(), MetaAVU()], 'checksum' : 'the_result_of_ichksum'}
        """
        files_with_chksum_and_avus = defaultdict(dict)
        for data_obj in json.loads(search_results_json):
            coll = None
            fname = None
            do_avus = []
            do_checksum = None
            for do_item, do_item_val in list(data_obj.items()):
#                print "DATA obj item: " + str(do_item)
                if do_item == 'collection':
                    coll = do_item_val
                elif do_item == 'data_object':
                    fname = do_item_val
                elif do_item == 'avus':
                    for avu in do_item_val:
                        avu_obj = data_types.MetaAVU(attribute=str(avu['attribute']), value=str(avu['value']))  # MetaAVU = namedtuple('MetaAVU', ['attribute', 'value'])    # list of attribute-value tuples
                        do_avus.append(avu_obj)
                elif do_item == 'checksum':
                    do_checksum = str(do_item_val)

                # sometimes there is an error here!!!!!

                # TODO: can add also: 1) data access checks, 2) replicate checksum checks, plus verify there are actually 2 replicas of each DO
            # print "PARsed do: " + str(parsed_do) + " coll = " + str(coll) + " do = " + str(do)
            # fpath = os.path.join(coll, do)
            # files_with_chksum_and_avus[fpath] = parsed_do
            fpath = os.path.join(coll, fname)
            files_with_chksum_and_avus[fpath] = {'avus' : do_avus, 'checksum' : do_checksum}
        return files_with_chksum_and_avus

    @classmethod
    def from_multi_metaquery_results_to_fpaths_and_avus(cls, search_results_json_list):
        """
            This method takes as parameter the json result of a metaquery containing avus and checksum,
            and turns the json into a dict having as key a fpath, and as value: dict of
            {'avus' : [MetaAVU(), MetaAVU()], 'checksum' : 'the_result_of_ichksum'}
        :param search_results_json_list: a list of json documents, one for each fpath that was queried for
        :param filters: optional (not implemented yet)
        :return: dict key = fpath, value = {'avus' : [MetaAVU(), MetaAVU()], 'checksum' : 'the_result_of_ichksum'}
        """
        results = {}
        for json_doc in search_results_json_list:
            do_avus = []
            #file_with_checksum_and_avu = cls.from_metaquery_results_to_fpaths_and_avus(json_doc)
            for do_item, do_item_val in list(json.loads(json_doc).items()):
#                print "DATA obj item: " + str(do_item)
                if do_item == 'collection':
                    coll = do_item_val
                elif do_item == 'data_object':
                    fname = do_item_val
                elif do_item == 'avus':
                    for avu in do_item_val:
                        avu_obj = data_types.MetaAVU(attribute=str(avu['attribute']), value=str(avu['value']))  # MetaAVU = namedtuple('MetaAVU', ['attribute', 'value'])    # list of attribute-value tuples
                        do_avus.append(avu_obj)
                elif do_item == 'checksum':
                    do_checksum = str(do_item_val)
            fpath = os.path.join(coll, fname)
            results[fpath] = {'avus': do_avus, 'checksum': do_checksum}
            #results.append(file_with_checksum_and_avu)
        return results


class iRODSiCmdsUtils(iRODSUtils):

    # @classmethod
    # def retrieve_list_of_bams_by_study_from_irods(cls, study_name):
    #     avus = {'study': study_name, 'type': 'bam'}
    #     bams = icommands_wrapper.iRODSMetaQueryOperations.query_by_metadata(avus)
    #     filtered_files = icommands_wrapper.iRODSMetaQueryOperations.filter_out_bam_phix_files(bams)
    #     return filtered_files
    #
    # @classmethod
    # def retrieve_list_of_crams_by_study_from_irods(cls, study_name):
    #     avus = {'study': study_name, 'type': 'cram'}
    #     crams = icommands_wrapper.iRODSMetaQueryOperations.query_by_metadata(avus)
    #     filtered_files = icommands_wrapper.iRODSMetaQueryOperations.filter_out_cram_phix_files(crams)
    #     return filtered_files
    #
    # @classmethod
    # def retrieve_list_of_files_by_study_name(cls, study_name):
    #     avus = {'study' : study_name}
    #     files = icommands_wrapper.iRODSMetaQueryOperations.query_by_metadata(avus)
    #     filtered_files = icommands_wrapper.iRODSMetaQueryOperations.filter_out_phix(files)
    #     return filtered_files

    @classmethod
    def retrieve_list_of_target_qc_pass_files_by_metadata(cls, attribute, value):
        avus = {attribute : value, 'target' : '1', 'manual_qc' : '1'}
        files = icommands_wrapper.iRODSMetaQueryOperations.query_by_metadata(avus)
        #filtered_files = icommands_wrapper.iRODSMetaQueryOperations.filter_out_phix(files)
        #return filtered_files
        return files

    @classmethod
    def retrieve_list_of_target_files_by_metadata(cls, attribute, value):
        avus = {attribute : value, 'target' : '1'}
        files = icommands_wrapper.iRODSMetaQueryOperations.query_by_metadata(avus)
        #filtered_files = icommands_wrapper.iRODSMetaQueryOperations.filter_out_phix(files)
        #return filtered_files
        return files

    @classmethod
    def retrieve_list_of_files_by_avus(cls, avus_dict):
        #avus = {attribute : value, 'target' : '1', 'manual_qc' : '1'}
        files = icommands_wrapper.iRODSMetaQueryOperations.query_by_metadata(avus_dict)
        #filtered_files = icommands_wrapper.iRODSMetaQueryOperations.filter_out_phix(files)
        #return filtered_files
        return files

    @classmethod
    def retrieve_list_of_files_by_metadata(cls, attribute, value):
        avus = {attribute : value}
        files = icommands_wrapper.iRODSMetaQueryOperations.query_by_metadata(avus)
        #filtered_files = icommands_wrapper.iRODSMetaQueryOperations.filter_out_phix(files)
        #return filtered_files
        return files


    @classmethod
    def retrieve_irods_avus(cls, irods_path):
        return irods_api.iRODSAPI.retrieve_metadata_for_file(irods_path)

    @classmethod
    def extract_values_for_key_from_irods_metadata(cls, avus_list, key):
        results = []
        for avu in avus_list:
            if avu.attribute == key:
                results.append(avu.value)
        return results


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
        irods_lib_names_list = cls.extract_values_for_key_from_irods_metadata(irods_metadata, 'library')

        # HACKS for the inconsistencies in iRODS, in which NPG submits under library name the actual library id
        lib_ids = list(set(irods_lib_internal_id_list + irods_lib_names_list))
        ids_dict = {'name': [], 'accession_number': [], 'internal_id': []}
        for id in lib_ids:
            id_type = Identif.guess_identifier_type(id)
            ids_dict[id_type].append(id)
        return ids_dict

