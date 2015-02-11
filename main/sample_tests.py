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


def get_samples_from_seqsc(ids_list, id_type):
    return seqsc.query_all_samples_as_batch(ids_list, id_type)


# TODO: rename all these methods to a more general name - check consistencies across different types of ids against Seqscape
def compare_sample_sets_obtained_by_seqscape_ids_lookup(samples_dict):
    """
        This function compares the sample sets identified by different types of ids,
        by looking up each set of ids in Seqscape, and comparing them with the samples found
        when querying by the other types of ids.
        Parameters
        ----------
            irods_samples : dict - {'name' : list, 'accession_number' : list, 'internal_id' : list}
        Returns
        -------
            differences : list - list of differences between the samples found by querying by name,
                                as opposed to those found by querying by accession number and internal_id
    """
    differences = []
    seqsc_samples_by_acc_nr, seqsc_samples_by_name, seqsc_samples_by_internal_id = None, None, None
    if samples_dict.get('name'):
        seqsc_samples_by_name = get_samples_from_seqsc(samples_dict['name'], 'name')
        if not seqsc_samples_by_name:
            differences.append("NO SAMPLES found in SEQSCAPE by sample names taken from iRODS metadata = " +
                               str(samples_dict['name']))
    if samples_dict.get('accession_number'):
        seqsc_samples_by_acc_nr = get_samples_from_seqsc(samples_dict['accession_number'], 'accession_number')
        if not seqsc_samples_by_acc_nr:
            differences.append("NO SAMPLES found in SEQSCAPE by sample accession_number from iRODS metadata = " +
                               str(samples_dict['accession_number']))
    if samples_dict.get('internal_id'):
        seqsc_samples_by_internal_id = get_samples_from_seqsc(samples_dict['internal_id'], 'internal_id')
        if not seqsc_samples_by_internal_id:
            differences.append("NO SAMPLES found in SEQSCAPE by sample internal_id from iRODS metadata = " +
                               str(samples_dict['internal_id']))

    # Compare samples found in Seqscape by different identifiers:
    if seqsc_samples_by_acc_nr and seqsc_samples_by_name:
        if not set(seqsc_samples_by_acc_nr) == set(seqsc_samples_by_name):
            diff = "The samples found in Seqscape when querying it by sample names from iRODS metadata: " + \
                   str(seqsc_samples_by_name) + " != as when querying by accession number from iRODS metadata: " + \
                   str(seqsc_samples_by_acc_nr)
            differences.append(diff)

    if seqsc_samples_by_internal_id and seqsc_samples_by_name:
        if not set(seqsc_samples_by_internal_id) == set(seqsc_samples_by_internal_id):
            diff = "The samples found in Seqscape when querying it by sample names from iRODS metadata: " + \
                   str(seqsc_samples_by_name) + " != as when querying by internal_ids from iRODS metadata: " + \
                   str(seqsc_samples_by_internal_id)
            differences.append(diff)
    return differences



def extract_samples_from_irods_metadata(irods_metadata):
    irods_sample_names_list = utils.extract_values_for_key_from_irods_metadata(irods_metadata, 'sample')
    irods_sample_acc_nr_list = utils.extract_values_for_key_from_irods_metadata(irods_metadata, 'sample_accession_number')
    irods_sample_internal_id_list = utils.extract_values_for_key_from_irods_metadata(irods_metadata, 'sample_id')
    irods_samples = {'name': irods_sample_names_list,
                     'accession_number': irods_sample_acc_nr_list,
                     'internal_id': irods_sample_internal_id_list
    }
    return irods_samples


def run_tests_on_samples(irods_metadata, header_metadata=None,
                         irods_vs_header=True, irods_vs_seqscape=True):
    if not irods_vs_header and not irods_vs_seqscape:
        print "Called tests_on_samples, but nothing to be done because both " \
              "irods_vs_header and irods_vs_seqscape parameters are False."
        return
    if header_metadata and not irods_vs_header:
        print "ERROR - called tests_on_samples, but irods_vs_header parameter is false."
        return
    if not header_metadata and irods_vs_header:
        print "ERROR - called tests_on_samples, but header_metadata is None."
        return

    issues = []
    if irods_vs_header or irods_vs_seqscape:
        irods_samples = extract_samples_from_irods_metadata(irods_metadata)
        missing_ids = utils.check_all_identifiers_in_metadata(irods_samples)
        issues.extend(missing_ids)

    # Compare IRODS vs. HEADER:
    if irods_vs_header:
        header_samples = utils.sort_entities_by_guessing_id_type(header_metadata.samples)
        irods_vs_head_diffs = utils.get_diff_irods_and_header_metadata(header_samples, irods_samples)
        issues.extend(irods_vs_head_diffs)

    # Compare IRODS vs. SEQSCAPE:
    if irods_vs_seqscape:
        irods_vs_seqsc_diffs = compare_sample_sets_obtained_by_seqscape_ids_lookup(irods_samples)
        issues.extend(irods_vs_seqsc_diffs)
    return issues

