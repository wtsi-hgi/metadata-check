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


def get_studies_from_seqsc(ids_list, id_type):
    return seqsc.query_all_studies_as_batch(ids_list, id_type)


# TODO: rename all these methods to a more general name - check consistencies across different types of ids against Seqscape
def compare_study_sets_obtained_by_seqscape_ids_lookup(irods_studies):
    """
        This function receives list of studies and checks that the studies identified by internal_id in Sequencescape
        are the same as the studies identified by accession number and name (also in Sequencescape).
        Parameters
        ----------
            irods_studies : { 'name' : list, 'accession_number' : list, 'internal_id' : list}
        Returns
        -------
            differences : list
    """
    differences = []
    seqsc_studies_by_name, seqsc_studies_by_acc_nr, seqsc_studies_by_internal_id = None, None, None
    if irods_studies.get('name'):
        seqsc_studies_by_name = get_studies_from_seqsc(irods_studies['name'], 'name')
        if not seqsc_studies_by_name:
            differences.append("NO STUDIES in SEQSCAPE by study names from iRODS = " + str(irods_studies['name']))

    if irods_studies.get('accession_number'):
        seqsc_studies_by_acc_nr = get_studies_from_seqsc(irods_studies['accession_number'], 'accession_number')
        if not seqsc_studies_by_acc_nr:
            differences.append("NO STUDIES in SEQSCAPE by study accession_number from iRODS = " + str(
                irods_studies['accession_number']))

    if irods_studies.get('internal_id'):
        seqsc_studies_by_internal_id = get_studies_from_seqsc(irods_studies['internal_id'], 'internal_id')
        if not seqsc_studies_by_internal_id:
            differences.append(
                "NO STUDIES in SEQSCAPE by study internal_id from iRODS = " + str(irods_studies['internal_id']))

    # Compare studies found in Seqscape by different identifiers:
    if seqsc_studies_by_acc_nr and seqsc_studies_by_name:
        if not set(seqsc_studies_by_acc_nr) == set(seqsc_studies_by_name):
            diff = "The studies found in Seqscape when querying it by name from iRODS metadata: " + \
                   str(seqsc_studies_by_name) + " != as when querying by accession number from iRODS metadata: " + \
                   str(seqsc_studies_by_acc_nr)
            differences.append(diff)

    if seqsc_studies_by_internal_id and seqsc_studies_by_name:
        if not set(seqsc_studies_by_internal_id) == set(seqsc_studies_by_internal_id):
            diff = "The studies found in Seqscape when querying it by name from iRODS metadata: " + \
                   str(seqsc_studies_by_name) + " != as when querying by internal_ids from iRODS metadata: " + \
                   str(seqsc_studies_by_internal_id)
            differences.append(diff)
    return differences



def extract_studies_from_irods_metadata(irods_metadata):
    irods_study_names_list = utils.extract_values_for_key_from_irods_metadata(irods_metadata, 'study')
    irods_study_internal_id_list = utils.extract_values_for_key_from_irods_metadata(irods_metadata, 'study_id')
    irods_study_acc_nr_list = utils.extract_values_for_key_from_irods_metadata(irods_metadata, 'study_accession_number')
    irods_studies = {'name': irods_study_names_list,
                     'internal_id': irods_study_internal_id_list,
                     'accession_number': irods_study_acc_nr_list
    }
    return irods_studies



def run_tests_on_studies(irods_metadata):
    if not irods_metadata:
        print "ERROR - irods_metadata parameter missing. Returning now!"
        return

    issues = []
    irods_studies = utils.extract_studies_from_irods_metadata(irods_metadata)
    missing_ids = utils.check_all_identifiers_in_metadata(irods_studies)
    issues.extend(missing_ids)

    # Compare IRODS vs. SEQSCAPE:
    irods_vs_seqsc_diffs = compare_study_sets_obtained_by_seqscape_ids_lookup(irods_studies)
    issues.extend(irods_vs_seqsc_diffs)
    return issues
