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


This file has been created on Nov 3, 2014.
"""


import subprocess
import config


class BAMHeaderParser(object):

    @classmethod
    def extract_header_from_file(cls, path):
        """
            This method extract the header from a file stored in a
            non-irods file system and returns it as text (string)
        """
        child_proc = subprocess.Popen([config.SAMTOOLS_PATH, 'view', '-H', path], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        (out, err) = child_proc.communicate()
        if err:
            print "ERROR calling samtools on " + str(path)
            raise IOError(err)
        return out


    @classmethod
    def extract_header_from_irods_file(cls, irods_path):
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
    def parse_header(cls, header):
        """
            Receives a BAM header as text (string) and parses it.
            It returns a dict containing as keys the header tags.
            Parameters
            ----------
            header : str
                Header as text (string)
            Returns
            -------
            header_dict : dict
                The contents of the header as dict of tags and tag-contents
        """
        header_dict = {}
        rg_list, sq_list, pg_list, hd_list = [], [], [], []
        lines = header.split('\n')
        for line in lines:
            if line.startswith('@SQ'):
                # sq_list.append(line)
                pass
            elif line.startswith('@HD'):
                # hd_list.append(line)
                pass
            elif line.startswith('@PG'):
                break
            elif line.startswith('@RG'):
                rg_list.append(line)
        rg_parsed_list = cls._parse_RG_tag(rg_list)
        #sq_parsed_list = cls._parse_SQ_tag(sq_list)

        header_dict['RG'] = rg_parsed_list
        header_dict['SQ'] = sq_list  #should be sq_parsed_list, but since we don't have a parser for these tags...
        header_dict['HD'] = hd_list
        header_dict['PG'] = pg_list
        return header_dict


header = BAMHeaderParser.extract_header_from_irods_file('/seq/11010/11010_8#21.bam')
rgs_list = BAMHeaderParser.parse_header(header)
print "EXTRACTED HEADER from file from iRODS: "+str(rgs_list)

print "\n"

header = BAMHeaderParser.extract_header_from_file('/lustre/scratch113/teams/hgi/mc14-vb-carl-fvg-hdd/F12HPCEUHK0358/WCAZAK513578/F12HPCEUHK0358_HUMcoqR/582009/Alignment_result/582009.dedup.realn.recal.bam')
rgs_list = BAMHeaderParser.parse_header(header)
print "Extracted header from file in lustre: "+str(rgs_list)