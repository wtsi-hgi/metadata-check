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


class IdentifierMapper:

    @classmethod
    def seqsc2irods(cls, id_type_in_seqsc, entity_type):
        if id_type_in_seqsc is 'name':
            return entity_type
        elif id_type_in_seqsc is 'accession_number':
            return str(entity_type) + "_" + id_type_in_seqsc
        elif id_type_in_seqsc is 'internal_id':
            return str(entity_type) + "_id"
        else:
            raise ValueError("Identifier not recongnized: " + str(id_type_in_seqsc))



