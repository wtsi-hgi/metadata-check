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

This file has been created on Feb 11, 2015.
"""

from main import metadata_utils
from com import utils
from irods import icommands_wrapper as irods_wrapper

import error_types

def check_md5_metadata(irods_fpath, irods_metadata):
    md5_metadata = metadata_utils.iRODSUtils.extract_values_for_key_from_irods_metadata(irods_metadata, 'md5')
    if not md5_metadata:
        print "This file doesn't have md5 in irods metadata"
        return None

    md5_chksum = irods_wrapper.iRODSChecksumOperations.get_checksum(irods_fpath)
    if md5_chksum:
        if not md5_metadata[0] == md5_chksum.md5:
            return error_types.WrongMD5Error(imeta_value=md5_metadata[0], ichksum_value=md5_chksum.md5, fpath=irods_fpath)
    return None


def check_run_id(irods_fpath, irods_metadata):
    """
    This test assumes that all the files in iRODS have exactly 1 run (=LANELETS)
    """
    irods_run_ids = metadata_utils.iRODSUtils.extract_values_for_key_from_irods_metadata(irods_metadata, 'id_run')
    path_run_id = metadata_utils.iRODSUtils.get_run_from_irods_path(irods_fpath)
    if len(irods_run_ids) > 1:
        return ["ERROR: > 1 runs for this file."]
    elif len(irods_run_ids) < 1:
        return ["ERROR: MISSING run_id from iRODS metadata"]
    else:
        irods_run_id = irods_run_ids[0]
    if not irods_run_id == path_run_id:
        return ["The run id in the iRODS file path is not the same as the run id in the iRODS metadata: " + \
                str(irods_run_id) + " vs. " + str(path_run_id)]
    return []


def check_lane_metadata(irods_fpath, irods_metadata):
    lane_id = metadata_utils.iRODSUtils.get_lane_from_irods_path(irods_fpath)
    irods_lane_ids = metadata_utils.iRODSUtils.extract_values_for_key_from_irods_metadata(irods_metadata, 'lane')
    if len(irods_lane_ids) > 1:
        return [" > 1 LANE in iRODS metadata"]
    elif len(irods_lane_ids) < 1:
        return ["NO LANE in iRODS metadata"]
    else:
        irods_lane_id = irods_lane_ids[0]
    if not irods_lane_id == lane_id:
        return ["iRODS fpath lane_id != lane_id in iRODS metadata: " +
                str(irods_lane_id) + " vs. " + str(lane_id)]
    return []



def check_lanelet_name(irods_fpath, header_lanelets):
    if len(header_lanelets) > 1:
        return [" > 1 lanelets in the header: "+str(header_lanelets)]
    elif len(header_lanelets) < 1:
        return [" < 1 lanelets in the header."]
    irods_lanelet_name = metadata_utils.iRODSUtils.extract_lanelet_name_from_irods_fpath(irods_fpath)
    fname = utils.extract_basename(irods_lanelet_name)
    if fname != header_lanelets[0]:
        return [
            "HEADER LANELET = " + str(header_lanelets[0]) + " different from FILE NAME = " + str(irods_lanelet_name)]
    return []



def check_reference(irods_fpath, irods_metadata, desired_ref):
    ref_paths = metadata_utils.iRODSUtils.extract_values_for_key_from_irods_metadata(irods_metadata, 'reference')
    if len(ref_paths) > 1:
        #return [" > 1 REFERENCE ATTRIBUTE in iRODS metadata"]
        raise error_types.WrongReferenceError(fpath=irods_fpath, desired_ref=desired_ref, header_ref='not implemented', irods_ref=str(ref_paths))
    elif len(ref_paths) < 1:
        #return ["NO REFERENCE ATTRIBUTE in iRODS metadata"]
        raise error_types.WrongReferenceError(fpath=irods_fpath, desired_ref=desired_ref, header_ref='not implemented', irods_ref='missing')
    else:
        ref_path = ref_paths[0]
    ref_name = metadata_utils.iRODSUtils.extract_reference_name_from_path(ref_path)
    print "REF NAME = " + str(ref_name) + " and desired_ref: " + str(desired_ref)
    if ref_name != desired_ref:
        #return ["WANTED REFERENCE =: " + str(desired_ref) + " different from ACTUAL REFERENCE = " + str(ref_name)]
        raise error_types.WrongReferenceError(fpath=irods_fpath, desired_ref=desired_ref, header_ref='not implemented', irods_ref=ref_name)
    return None


def run_irods_seq_specific_tests(irods_path, irods_metadata, header_metadata, desired_ref=None):
    issues = []
    try:
        check_md5_metadata(irods_path, irods_metadata)
    except error_types.WrongMD5Error as e:
        issues.append(e)

    try:
        run_id_issues = check_run_id(irods_path, irods_metadata)
    except Exception as e:
        issues.extend(run_id_issues)

    lane_metadata_issues = check_lane_metadata(irods_path, irods_metadata)
    if lane_metadata_issues:
        issues.extend(lane_metadata_issues)

    lane_name_issues = check_lanelet_name(irods_path, header_metadata.lanelets)
    if lane_name_issues:
        issues.extend(lane_name_issues)

    if desired_ref:
        try:
            check_reference(irods_path, irods_metadata, desired_ref)
        except error_types.WrongReferenceError as e:
            #issues.append(str(e))
            print str(e)
    return issues
