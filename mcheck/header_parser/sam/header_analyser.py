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

from collections import namedtuple


# Named tuples for each header type used as container for returning results:
from mcheck.com import wrappers

BAMHeaderRG = namedtuple('BAMHeaderRG', [
    'seq_centers',
    'seq_dates',
    'lanelets',
    'platforms',
    'libraries',
    'samples',
])

BAMHeaderPG = namedtuple('BAMHeaderPG', [])

BAMHeaderSQ = namedtuple('BAMHeaderSQ', [])

BAMHeaderHD = namedtuple('BAMHeaderHD', [])

BAMHeader = namedtuple('BAMHeader', ['rg', 'pg', 'hd', 'sq'])


class _RGTagAnalyser(object):

    @classmethod
    @wrappers.check_args_not_none
    def analyse_all(cls, rgs_list):
        pass




class _SQTagAnalyser(object):
    @classmethod
    def analyse_all(cls, sqs_list):
        raise NotImplementedError


class _HDTagAnalyser(object):
    @classmethod
    def analyse_all(cls, hds_list):
        raise NotImplementedError


class _PGTagAnalyser(object):
    @classmethod
    def analyse_all(cls, pgs_list):
        raise NotImplementedError


class BAMHeaderAnalyser(object):
    """
        Class containing the functionality for parsing BAM file's header.
    """

    # @classmethod
    # @wrappers.check_args_not_none
    # def extract_and_parse_header_from_file(cls, path):
    #     """ This method extracts the header from a BAM file, given its path and parses it
    #         returning the header as a dict, where the keys are header tags (e.g. 'SM', 'LB')
    #         Parameters
    #         ----------
    #         path: str
    #             The path to the file - in a non-iRODS File System
    #         Returns
    #         -------
    #         header : dict
    #             A dict containing the groups in the BAM header.
    #         Raises
    #         ------
    #         ValueError - if the file is not SAM/BAM format
    #
    #     """
    #     with pysam.Samfile(path, "rb") as bamfile:
    #         return bamfile.header
    #


    @classmethod
    @wrappers.check_args_not_none
    def _parse_RG_tag(cls, rg_list):
        """
        Takes a list of rg tags, each tag is represented as text.
        Parameters
        ----------
        rg_list : list
            A list of RG tags, as they appear in the BAM header.
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
    @wrappers.check_args_not_none
    def extract_metadata_from_header(cls, header_dict, rg=True, sq=False, hd=False, pg=False):
        """ This method takes a BAM file path and processes its header into a BAMHeader object
            Parameters
            ----------
            path: str
                THe path to the BAM file
            rg: bool
                Flag - True(default) if the result should contain also the RG (ReadGroups) of the parsed header
            hd: bool
                Flag - True(default) if the result should contain also the HD (head) of the parsed header
            sq: bool
                Flag - True(default) if the result should contain also the SQ (Sequnce) of the parsed header
            pg: bool
                Flag - True(default) if the result should contain also the PG (Programs) of the parsed header
            Returns
            -------
            header: BAMHeader
                The header parsed, containing the parts specified as paramter
            Raises
            ------
            ValueError - if the file is not SAM/BAM format
        """
        sq = _SQTagAnalyser.analyse_all(header_dict['SQ']) if sq else None
        hd = _HDTagAnalyser.analyse_all(header_dict['HD']) if hd else None
        pg = _PGTagAnalyser.analyse_all(header_dict['PG']) if pg else None
        rg = _RGTagAnalyser.analyse_all(header_dict['RG']) if rg else None
        return BAMHeader(sq=sq, hd=hd, pg=pg, rg=rg)



#if __name__ == '__main__':

# header = BAMHeaderAnalyser.extract_header_from_irods_file('/seq/11010/11010_8#21.bam')
# rgs_list = BAMHeaderAnalyser.parse_header(header)
# print "EXTRACTED HEADER from file from iRODS: "+str(rgs_list)

# print "\n"

# header = BAMHeaderAnalyser.extract_header_from_file('/lustre/scratch113/teams/hgi/mc14-vb-carl-fvg-hdd/F12HPCEUHK0358/WCAZAK513578/F12HPCEUHK0358_HUMcoqR/582009/Alignment_result/582009.dedup.realn.recal.bam')
# rgs_list = BAMHeaderAnalyser.parse_header(header)
# print "Extracted header from file in lustre: "+str(rgs_list)
