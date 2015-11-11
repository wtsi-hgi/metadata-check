"""
Created on Dec 02, 2014
Author: Irina Colgiu <ic4@sanger.ac.uk>

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
 
"""

RUNNING_LOCATION = 'remote'

#SAMTOOLS_IRODS_PATH = '/software/solexa/bin/samtools_irods'

SAMTOOLS_IRODS_PATH = '/software/hgi/pkglocal/samtools-git-1.2-4-g76870cc/bin/samtools'
SAMTOOLS_PATH = '/nfs/users/nfs_m/mercury/local-precise-x86_64/bin/samtools'

# Seqscape configurations:
SEQSC_HOST 		= "seqw-db.internal.sanger.ac.uk"
SEQSC_PORT 		= 3379
SEQSC_USER 		= "warehouse_ro"
SEQSC_DB_NAME 	= "sequencescape_warehouse"


LUSTRE_HOME = '/lustre/scratch113/teams/hgi/users/ic4/'

IRODS_ATTRIBUTE_FREQUENCY_CONFIG_FILE = '/nfs/users/nfs_i/ic4/Projects/metadata-check/irods_meta.conf'

BATON_METAQUERY_BIN_PATH =  "/software/gapi/pkg/baton/0.15.0/bin/baton-metaquery"
BATON_LIST_BIN_PATH =  "/software/gapi/pkg/baton/0.15.0/bin/baton-list"