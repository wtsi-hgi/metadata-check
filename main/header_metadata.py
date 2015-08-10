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

This file has been created on Jun 30, 2015.
"""

import metadata_utils
from com import utils as common_utils
import error_types


class HeaderSAMFileMetadata(object):

    def __init__(self, fpath, fname, samples=[], libraries=[], studies=[], lanelets=None, reference=None):
        self.fname = fname
        self.fpath = fpath
        self.samples = samples
        self.libraries = libraries
        self.studies = studies
        self.reference = reference
        self.lanelets = lanelets


    @classmethod
    def from_header_to_metadata(cls, header, fpath):
        """

        :param header: of type BAMHeader = namedtuple('BAMHeader', ['rg', 'pg', 'hd', 'sq'])
        :return:
        """
        header_rg = header.rg
        samples = metadata_utils.HeaderUtils.sort_entities_by_guessing_id_type(header_rg.samples)
        libraries = metadata_utils.HeaderUtils.sort_entities_by_guessing_id_type(header_rg.libraries)
        fname = common_utils.extract_fname(fpath)
        return HeaderSAMFileMetadata(fpath=fpath, fname=fname, samples=samples, libraries=libraries, lanelets=header_rg.lanelets)

            # from previous impl:
            # header_samples = metadata_utils.HeaderUtils.sort_entities_by_guessing_id_type(header_metadata.samples)
            # try:
            #     check_irods_vs_header_metadata(irods_fpath, header_samples, irods_samples, 'sample')
            # except error_types.HeaderVsIrodsMetadataAttributeError as e:
            #

#         BAMHeaderRG = namedtuple('BAMHeaderRG', [
    #     'seq_centers',
    #     'seq_dates',
    #     'lanelets',
    #     'platforms',
    #     'libraries',
    #     'samples',
    # ])


    def run_field_sanity_checks_and_filter(self):
        problems = []
        if self.samples:
            #self.samples, pbs = self._filter_out_non_entities(self.samples)
            self.samples, pbs = metadata_utils.GeneralUtils.filter_out_non_entities(self.fpath, self.samples, 'sample')
            pbs = [error_types.WrongHeaderMetadataValue(err.fpath, err.attribute, err.value) for err in pbs]
            problems.extend(pbs)

        if self.libraries:
            self.libraries, pbs = metadata_utils.GeneralUtils.filter_out_non_entities(self.fpath, self.libraries, 'library')
            pbs = [error_types.WrongHeaderMetadataValue(err.fpath, err.attribute, err.value) for err in pbs]
            problems.extend(pbs)

        if self.studies:
            self.studies, pbs = metadata_utils.GeneralUtils.filter_out_non_entities(self.fpath, self.studies, 'study')
            pbs = [error_types.WrongHeaderMetadataValue(err.fpath, err.attribute, err.value) for err in pbs]
            problems.extend(pbs)
        return problems


    def __str__(self):
        return "Fpath = " + str(self.fpath) + ", fname = "+ str(self.fname) + ", samples = " + str(self.samples) + \
               ", libraries = " + str(self.libraries) + ", lanelets = " + str(self.lanelets)

    def __repr__(self):
        return self.__str__()