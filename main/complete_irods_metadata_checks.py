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
import metadata_utils


def parse_config_file(path):
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

def get_dict_differences(dict1, dict2):
#    return set(dict1.items()) - set(dict2.items())
    diffs = []
    for k,v, in dict1.items():
        #print k,v,dict2[k]
        if not dict2.get(k):
            diffs.append((k, v, 0))
        elif v != dict2[k]:
            diffs.append((k,v,dict1[k]))
    return diffs


def check_irods_meta_complete(irods_fpath, config_fpath):
    config_attrs_freq = parse_config_file(config_fpath)
    file_metadata = metadata_utils.iRODSUtils.retrieve_irods_avus(irods_fpath)
    metadata_freq_dict = build_freq_dict_from_avus_list(file_metadata)
    return get_dict_differences(config_attrs_freq, metadata_freq_dict)

# diffs = compare_irods_meta_with_configured_attributes('/seq/15254/15254_4.cram', '/nfs/users/nfs_i/ic4/Projects/metadata-check/irods_meta.conf')
# print str(diffs)
