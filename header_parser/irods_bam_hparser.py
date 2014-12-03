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

import subprocess
import config


class BAMHeaderParser(object):

    @classmethod
    def extract(cls, irods_path):
        irods_path = 'irods:'+str(irods_path)
        child_proc = subprocess.Popen([config.SAMTOOLS_IRODS_PATH, 'view', '-H', irods_path], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        (out, err) = child_proc.communicate()
        if err:
            print "ERROR calling samtools irods on " + str(irods_path)
            raise IOError(err)
        return out


    @classmethod
    def _parse_RG_tag(cls, rg_list):
        """
        Parameters
        ----------
        Takes a list of rg tags, each tag is represented as text.
        """
        rgs_parsed = []
        for rg in rg_list:
            new_rg = {}
            groups = rg.split('\t')
            for grp in groups:
                tag_name = grp[0:2]
                if tag_name in ['SM', 'LB', 'PL', 'PU', 'DS', 'DT', 'CN']:
                    tag_value = grp[3:]
                    new_rg[tag_name] = tag_value
            rgs_parsed.append(new_rg)
        return rgs_parsed


    @classmethod
    def parse(cls, header):
        rg_list = []
        lines = header.split('\n')
        for line in lines:
            if line.startswith('@RG'):
                rg_list.append(line)
            #elif line.startswith(...) -- TODO: implement for other tags if needed
        rgs_parsed = cls._parse_RG_tag(rg_list)
        return rgs_parsed

header = BAMHeaderParser.extract('/seq/11010/11010_8#21.bam')
rgs_list = BAMHeaderParser.parse(header)
print "EXTRACTED HEADER: "+str(rgs_list)


