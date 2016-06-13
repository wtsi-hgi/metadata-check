"""
Copyright (C) 2016  Genome Research Ltd.

Author: Irina Colgiu <ic4@sanger.ac.uk>

This program is part of meta-check

meta-check is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.
You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

This file has been created on Jun 13, 2016.
"""

class ComparableMetadata:

    def __init__(self, samples, libraries, studies):
        self.samples = samples
        self.studies = studies
        self.libraries = libraries

    def differences(self, other):
        """
        This method finds the differences between metadata1 and metadata2, given a list of entities of interest.
        Basically does metadata1 - metadata2 (finds all the entities that are present within metadata1, but not within metadata2).
        :param metadata1:
        :param metadata2:
        :param entity_types_list:
        :return:
        """
        if not isinstance(other, ComparableMetadata):
            raise TypeError("Can't compare with a non-ComparableMetadata type")
        differences = {}
        for entity_type in ['samples', 'studies', 'libraries']:
            metadata_entities1 = getattr(self, entity_type)  # header
            metadata_entities2 = getattr(other, entity_type)  # seqsc
            ent_type_diffs = {}
            for id_type, values in metadata_entities1.items():
                if values and metadata_entities2.get(id_type):
                    if values != metadata_entities2.get(id_type):
                        ent_type_diffs[id_type] = set(values).difference(set(metadata_entities2.get(id_type)))
            if ent_type_diffs:
                differences[entity_type] = ent_type_diffs
        return differences

    # @staticmethod
    # def _find_differences(metadata1, metadata2, entity_types_list):
