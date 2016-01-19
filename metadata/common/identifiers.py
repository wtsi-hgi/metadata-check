"""
Copyright (C) 2013, 2014, 2015  Genome Research Ltd.

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

This file has been created on Nov 19, 2015.
"""

import re
from com import wrappers
from typing import List, Dict


class EntityIdentifier(object):

    @classmethod
    @wrappers.check_args_not_none
    def is_identifier(cls, identifier: str):
        return identifier not in ['N/A', 'undefined', 'unspecified']

    @classmethod
    @wrappers.check_args_not_none
    def is_accession_nr(cls, field: str) -> bool:
        """
            The ENA accession numbers all start with: ERS, SRS, DRS or EGA.
        """
        if type(field) == int:
            return False
        if field.startswith('ER') or field.startswith('SR') or field.startswith('DR') or field.startswith('EGA'):
            return True
        return False

    @classmethod
    @wrappers.check_args_not_none
    def is_internal_id(cls, field: str) -> bool:
        """ All internal ids are int. You can't really tell if one identifier
            is an internal id just by the fact that it's type is int, but you
            can tell if it isn't, if it contains characters other than digits.
        """
        if type(field) == int:
            return True
        if field.isdigit():
            return True
        return False

    @classmethod
    @wrappers.check_args_not_none
    def is_name(cls, field: str) -> bool:
        """ You can't tell for sure if one identifier is a name or not either.
            Basically if it contains numbers and alphabet characters, it may be a name."""
        if not type(field) == str:
            return False
        is_match = re.search('^[0-9a-zA-Z]*$', field)
        if is_match:
            return True
        return False

    @classmethod
    @wrappers.check_args_not_none
    def guess_identifier_type(cls, identifier: str) -> str:
        """
            This method receives the value of an identifier and returns its inferred type,
            where the identifier type options are: internal_id, name and accession_number
        """
        if cls.is_accession_nr(identifier):
            identifier_type = 'accession_number'
        elif cls.is_internal_id(identifier):
            identifier_type = 'internal_id'
        else:
            identifier_type = 'name'
        return identifier_type

    @classmethod
    @wrappers.check_args_not_none
    def separate_identifiers_by_type(cls, identifiers: List[str]) -> Dict[str, List[str]]:
        ids, names, accession_nrs = [], [], []
        for identifier in identifiers:
            if cls.is_internal_id:
                ids.append(identifier)
            elif cls.is_accession_nr:
                accession_nrs.append(identifier)
            else:
                names.append(identifier)
        return { 'name': names,
                 'accession_number': accession_nrs,
                 'internal_id': ids
        }


    # @classmethod
    # def filter_out_non_ids(cls, ids_list):
    #     return [id for id in ids_list if id not in ]

    # ugly method - these things should be separated (filtering out, reporting errors, and putting together the right error to be returned directly to the user)
    # plus I silently access the fpath field from this object, dirty!!!
    # @classmethod
    # def filter_out_non_entities(cls, fpath, entity_dict, entity_type):
    #     filtered_entities = {}
    #     problems = []
    #     for id_type, ids_list in list(entity_dict.items()):
    #         filtered_ids = cls.filter_out_non_ids(ids_list)
    #         non_ids = set(ids_list).difference(set(filtered_ids))
    #         problems.extend([error_types.WrongMetadataValue(fpath=fpath, attribute=str(entity_type)+'_'+str(id_type), value=id) for id in non_ids])
    #         filtered_entities[id_type] = filtered_ids
    #     return filtered_entities, problems


