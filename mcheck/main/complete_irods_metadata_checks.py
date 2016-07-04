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

This file has been created on Jun 09, 2015.
"""

from collections import defaultdict

from mcheck.com import wrappers
from mcheck.main import error_types


#
# if __name__ == '__main__':
#     #irods_fpath = '/seq/15254/15254_4.cram'
#     irods_fpath = '/seq/8284/8284_5#55_xahuman.bam'
#     print str(check_irods_metadata_is_complete_for_file(irods_fpath, '/nfs/users/nfs_i/ic4/Projects/metadata-check/irods_meta.conf'))
#     # irods_avus = metadata_utils.iRODSUtils.retrieve_irods_avus(irods_fpath)
#     # diffs = compare_avus_vs_config_frequencies(irods_fpath, '/nfs/users/nfs_i/ic4/Projects/metadata-check/irods_meta.conf')
#     # print str(diffs)
#     # excs = from_tuples_to_exceptions(diffs)
#     # print "AS EXCEPTIONS : "+ str(excs)