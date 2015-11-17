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

This file has been created on Jun 18, 2015.
"""

from main import error_types
import seqscape.queries as seqsc


def fetch_studies_by_samples(samples):
    sample_ids = [s.internal_id for s in samples]
    entities_fetched = seqsc.query_for_studies_by_samples(sample_ids)
    entities_fetched = SeqscapeEntitiesFetchedBasedOnIds(entities_fetched=entities_fetched, query_ids=sample_ids,
                                                         query_id_type='internal_id', query_entity_type='sample',
                                                         fetched_entity_type='study'
                                                         )
    return entities_fetched



def check_sample_is_in_desired_study(sample_ids, study_name):
    """

    :param sample_ids: a list of sample internal_id
    :param study_name: the name of the study that all the samples should be part of
    :return: Nothing if everything is ok, error_types.SampleDoesntBelongToGivenStudy if there are inconsistencies
    """
    actual_studies_from_seqsc = seqsc.query_for_studies_by_samples(sample_ids)
    studies_by_name = [s.name for s in actual_studies_from_seqsc]
    if study_name not in studies_by_name:
        return error_types.SamplesDontBelongToGivenStudy(sample_ids=sample_ids, actual_study=str(studies_by_name), desired_study=study_name)


