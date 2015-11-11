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

This file has been created on Jul 16, 2015.
"""

import json
from irods import constants
import config
import subprocess
import os
import tempfile

class BatonAPI:

    @classmethod
    def _from_dict_to_irods_avus(cls, avus_tuple_list):
        irods_avu_list = []
        for attr, val in avus_tuple_list:
            irods_avu_list.append({ "attribute": attr, "value" : val, "o" : "="})
        return {'avus' : irods_avu_list}

    @classmethod
    def _split_path_in_data_obj_and_coll(cls, fpath_irods):
        dir, fname = os.path.split(fpath_irods)
        return {'data_object' : fname, 'collection' : dir}

    @classmethod
    def _get_baton_metaquery_result(cls, query_as_json, zone=constants.IRODS_SEQ_ZONE):
        """
        This method queries by metadata iRODS using BATON and returns the result as json writen to a temp file.
        :param query_as_json:
        :param zone:
        :return: the path to a temp file where the results are
        """
        # Open/create a tempfile:
        #temp = tempfile.NamedTemporaryFile(mode='w')
        p = subprocess.Popen([config.BATON_METAQUERY_BIN_PATH, '--zone', zone, '--obj', '--checksum', '--avu', '--acl'],   # not necessary to add also '--checksum' if --replicate is there
                             stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE) # ,stdout=temp, stderr=subprocess.STDERR
        out, err = p.communicate(input=query_as_json)
        if err:
            #print "ERROR REPORT: " + str(err)
            raise IOError("Some irods error : " + str(err))
        # if err:
        #     print "ERROR VIA stderr " + str(err)
        #     #raise IOError
        return out
        #return temp

    @classmethod
    def _get_baton_list_metadata_result(cls, data_obj_as_json):
        #jq -n '[{data_object: "10080_8#64.bam", collection: "/seq/10080/"}]' | /software/gapi/pkg/baton/0.15.0/bin/baton-list -avu --acl
        p = subprocess.Popen([config.BATON_LIST_BIN_PATH, '--avu', '--acl', '--checksum'],     # not necessary to add also '--checksum' if --replicate is there
                             stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
        out, err = p.communicate(input=data_obj_as_json)
        #print "OUT: " + str(out) + "ERR " + str(err)
        if err:
            raise IOError("Some irods error : " + str(err))
        return out


    @classmethod
    def _get_baton_list_metadata_for_list_of_files_result(cls, list_of_data_obj_as_json):
        p = subprocess.Popen([config.BATON_LIST_BIN_PATH, '--avu', '--acl', '--checksum'],     # not necessary to add also '--checksum' if --replicate is there
                             stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
        for f in list_of_data_obj_as_json:
            p.stdin.write(f)
        out, err = p.communicate()
        #print "OUT: " + str(out) + "ERR " + str(err)
        if err:
            raise IOError("Some irods error : " + str(err))
        return out



    @classmethod
    def query_by_metadata_and_get_results_as_json(cls, avu_tuple_list, zone=constants.IRODS_SEQ_ZONE, operator='='):
        """
        THis method is querying iRODS using BATON in order to get the metadata for the files (data objects) that match the search criteria.
        The information is returned as a dict of collection, data_object and avus. It can be filtered afterwards for leaving in only the info of interest.
        :param avu_tuple_list: key = attribute name, value = attribute_value
        :param zone:
        :param operator:
        :return: a tempfile
        WARNING:
            1. This assumes that the operator is always =
            2. This assumes that there is exactly 1 entry for each type of attribute - there can't be a query for 2 samples for exp.
        """
        irods_avus = cls._from_dict_to_irods_avus(avu_tuple_list)
        irods_avus_json = json.dumps(irods_avus)
        return cls._get_baton_metaquery_result(irods_avus_json, zone)


    @classmethod
    def get_file_metadata(cls, fpath):
        """
        :param fpath:
        :return:
        """
        fpath_as_dict = cls._split_path_in_data_obj_and_coll(fpath)
        irods_fpath_dict_as_json = json.dumps(fpath_as_dict)
        return cls._get_baton_list_metadata_result(irods_fpath_dict_as_json)


    @classmethod
    def get_all_files_metadata(cls, fpaths):
        """
        :param fpath:
        :return:
        """
        list_of_fpaths_as_json = []
        for f in fpaths:
            fpath_as_dict = cls._split_path_in_data_obj_and_coll(f)
            irods_fpath_dict_as_json = json.dumps(fpath_as_dict)
            list_of_fpaths_as_json.append(irods_fpath_dict_as_json)
        return cls._get_baton_list_metadata_for_list_of_files_result(list_of_fpaths_as_json)


