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

This file has been created on Jun 26, 2015.
"""

LANLET_NAME_REGEX = '^(?P<run_id>[0-9]{4,5})_(?P<lane_id>[0-9]{1})((?:#(?P<tag_id>[0-9]{1,2}))|$|\.)'
IRODS_SEQ_LANELET_PATH_REGEX = '^/seq/(?P<run_id>[0-9]{4,5})/(?P=run_id)_(?P<lane_id>[0-9]{1})(?:#?(?P<tag_id>[0-9]{1,2})?)\.'
MD5_REGEX = '^[0-9a-z]+$'
RUN_ID_REGEX = '^[0-9]{4,5}$'
LANE_ID_REGEX = '^[0-9]{1}$'
NPG_QC_REGEX = '^0|1$'
TARGET_REGEX = '^0|1$'

######################## CONSTANTS ###############################

IRODS_HUMGEN_ZONE = 'humgen'
IRODS_SEQ_ZONE = 'seq'

iRODS_READ_PERMISSION = "read"
iRODS_MODIFY_PERMISSION = "write"
iRODS_OWN_PERMISSION = "own"
iRODS_NULL_PERMISSION = "null"

