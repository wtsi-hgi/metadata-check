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

from mcheck.main import error_types


class GeneralUtils:

    @classmethod
    def check_same_entities(cls, seqsc_entities, entity_type):
        problems = []
        id_types = list(seqsc_entities.keys())
        for i in range(1, len(id_types)-1):
            if seqsc_entities.get(id_types[i-1]) and seqsc_entities.get(id_types[i]):
                if not set(seqsc_entities.get(id_types[i-1])) == set(seqsc_entities.get(id_types[i])):
                    problems.append(str(error_types.DiffEntitiesRetrievedFromSeqscapeByDiffIdTypesError(entity_type=entity_type,
                                                                                         id_type1=id_types[i-1],
                                                                                         id_type2=id_types[i],
                                                                                         entities_set1=seqsc_entities[id_types[i-1]],
                                                                                         entities_set2=seqsc_entities[id_types[i]])))
        return problems


