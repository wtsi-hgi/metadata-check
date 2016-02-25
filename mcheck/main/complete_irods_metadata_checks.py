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

This file has been created on Jun 09, 2015.
"""

from collections import defaultdict

from . import metadata_utils
from mcheck.com import wrappers
from mcheck.main import error_types


@wrappers.check_args_not_none
def read_and_parse_config_file(path):
    attributes_frequency = {}
    config_file = open(path)
    for line in config_file:
        line = line.strip()
        tokens = line.split()
        if len(tokens) != 2:
            raise ValueError("Non standard config file - each line must have 2 items. This line looks like:"+str(line))
        attribute = tokens[0]
        if not tokens[1].isdigit():
            raise ValueError("The config file doesn't contain integers as frequencies" + str(line))
        freq = int(tokens[1])
        attributes_frequency[attribute] = freq
    return attributes_frequency

def build_freq_dict_from_avus_list(avus_list):
    freq_dict = defaultdict(int)
    for avu in avus_list:
        freq_dict[avu.attribute] += 1
    return freq_dict

@wrappers.check_args_not_none
def get_dict_differences(dict1, dict2):
#    return set(dict1.items()) - set(dict2.items())
    diffs = []
    for k,v, in list(dict1.items()):
        if not dict2.get(k):
            diffs.append((k, v, 0))
        elif v != dict2[k]:
            diffs.append((k,v,dict2[k]))
    return diffs


# def compare_avus_vs_config_frequencies(irods_avus, config_fpath):
#     #config_attrs_freq = read_and_parse_config_file(config_fpath)
#     pass

def from_tuples_to_exceptions(tuples_list):
    excs = []
    for attr_name, desired_freq, actual_freq in tuples_list:
        excs.append(error_types.MetadataAttributeCountError(fpath=None, attribute=attr_name, desired_occurances=desired_freq, actual_occurances=actual_freq))
    return excs

def check_irods_metadata_is_complete_for_file(fpath, config_path):
    irods_avus = metadata_utils.iRODSiCmdsUtils.retrieve_irods_avus(fpath)
    return check_avus_freq_vs_config_freq(irods_avus, config_path)


def check_avus_freq_vs_config_freq(avus, config_path):
    irods_attr_freq_dict = build_freq_dict_from_avus_list(avus)
    config_attr_freq_dict = read_and_parse_config_file(config_path)
    return get_dict_differences(config_attr_freq_dict, irods_attr_freq_dict)


#
# if __name__ == '__main__':
#     #irods_fpath = '/seq/15254/15254_4.cram'
#     irods_fpath = '/seq/8284/8284_5#55_xahuman.bam'
#     print str(check_irods_metadata_is_complete_for_file(irods_fpath, '/nfs/users/nfs_i/ic4/Projects/metadata-check/irods_meta.conf'))
#     # irods_avus = metadata_utils.iRODSUtils.retrieve_irods_avus(irods_fpath)
#     # diffs = compare_avus_vs_config_frequencies(irods_fpath, '/nfs/users/nfs_i/ic4/Projects/metadata-check/irods_meta.conf')
#     # print str(diffs)
#     # excs = from_tuples_to_exceptions(diffs)
#     # print "AS EXCEPTIONS : "+ str(excs)