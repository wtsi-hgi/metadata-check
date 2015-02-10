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

import seqscape.queries as seqsc
from main import utils




def get_libraries_from_seqsc(ids_list, id_type):
    return seqsc.query_all_libraries_as_batch(ids_list, id_type)


def get_all_possible_libraries_from_seqsc(ids_list, id_type):
    libs = seqsc.query_all_libraries_as_batch(ids_list, id_type)
    if not libs:
        libs = seqsc.query_all_wells_as_batch(ids_list, id_type)
    if not libs:
        libs = seqsc.query_all_multiplexed_libraries_as_batch(ids_list, id_type)
    return libs


# TODO: rename all these methods to a more general name - check consistencies across different types of ids against Seqscape
def get_diff_seqsc_and_irods_libraries_metadata(irods_libraries):
    differences = []
    seqsc_libraries_by_name, seqsc_libraries_by_internal_id = None, None
    if irods_libraries.get('name'):
        seqsc_libraries_by_name = get_all_possible_libraries_from_seqsc(irods_libraries['name'], 'name')
        if not seqsc_libraries_by_name:
            differences.append("NO LIBRARIES in SEQSCAPE by library names from iRODS = " + str(irods_libraries['name']))
    if irods_libraries.get('internal_id'):
        seqsc_libraries_by_internal_id = get_all_possible_libraries_from_seqsc(irods_libraries['internal_id'],
                                                                               'internal_id')
        if not seqsc_libraries_by_internal_id:
            differences.append(
                "NO LIBRARIES in SEQSCAPE by library internal_id from iRODS = " + str(irods_libraries['internal_id']))

    if seqsc_libraries_by_internal_id and seqsc_libraries_by_name:
        if not (set(seqsc_libraries_by_internal_id) == set(seqsc_libraries_by_name)):
            diff = "LIBRARIES in iRODS= " + str(irods_libraries) + " != LIBRARIES IN SEQSCAPE SEARCHED by name: " + \
                   str(seqsc_libraries_by_name) + \
                   " != LIBRARIES IN SEQSCAPE searched by internal_id: " + str(seqsc_libraries_by_internal_id)
            differences.append(diff)
    return differences



def extract_libraries_from_irods_metadata(irods_metadata):
    irods_lib_internal_id_list = utils.extract_values_by_key_from_irods_metadata(irods_metadata, 'library_id')
    if not irods_lib_internal_id_list:
        irods_lib_names_list = utils.extract_values_by_key_from_irods_metadata(irods_metadata, 'library')
        irods_libraries = {'name': irods_lib_names_list}
    else:
        irods_libraries = {'internal_id': irods_lib_internal_id_list}
    return irods_libraries


def run_tests_on_libraries(irods_metadata, header_metadata=None,
                           irods_vs_header=True, irods_vs_seqscape=True):
    if not irods_vs_header and not irods_vs_seqscape:
        print "Called tests_on_libraries, but nothing to be done because both " \
              "irods_vs_header and irods_vs_seqscape parameters are False."
        return
    if header_metadata and not irods_vs_header:
        print "ERROR - called tests_on_libraries, but irods_vs_header parameter is false."
        return
    if not header_metadata and irods_vs_header:
        print "ERROR - called tests_on_libraries, but header_metadata is None."
        return

    issues = []
    if irods_vs_header or irods_vs_seqscape:
        irods_libraries = extract_libraries_from_irods_metadata(irods_metadata)
        missing_ids = utils.check_all_identifiers_in_metadata(irods_libraries, accession_number=False, name=False)
        issues.extend(missing_ids)

    # Compare IRODS vs. HEADER:
    if irods_vs_header:
        header_libraries = utils.extract_entities_from_header_metadata(header_metadata.libraries)
        irods_vs_head_diffs = utils.get_diff_irods_and_header_metadata(header_libraries, irods_libraries)
        issues.extend(irods_vs_head_diffs)

    # Compare IRODS vs. SEQSCAPE:
    if irods_vs_seqscape:
        irods_vs_seqsc_diffs = get_diff_seqsc_and_irods_libraries_metadata(irods_libraries)
        issues.extend(irods_vs_seqsc_diffs)
    return issues
