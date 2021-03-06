"""
Copyright (C) 2014  Genome Research Ltd.

Author: Irina Colgiu <ic4@sanger.ac.uk>

This program is part of metadata-check.

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

This file has been created on Oct 28, 2014

"""

from collections import namedtuple


# FileLine = namedtuple('FileLine', ['owner', 'replica_id', 'resc_name','size', 'timestamp', 'is_paired', 'fname'])
# CollLine = namedtuple('CollLine', ['coll_name'])
#
#
# CollListing = namedtuple('CollListing', ['coll_list', 'files_list'])    # where files_list = list of FileLine
#                                                                         # coll_list = list of CollLine
# ChecksumResult = namedtuple('ChecksumResult', ['md5'])

MetaAVU = namedtuple('MetaAVU', ['attribute', 'value'])    # list of attribute-value tuples