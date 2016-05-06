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

import re
import typing

from mcheck.header_parser.sam.header import SAMFileHeader, SAMFileRGTag
from mcheck.com import wrappers


class SAMFileHeaderParser:
    """
        Abstract class to be inherited by all the classes that contain header parsing functionality.
    """
    @classmethod
    def parse(cls, header_as_text: str):
        """
        Receives a BAM header as text (string) and parses it.
        It returns a SAMFileHeader - containing the tags as lists of strings,
        where each string is a line from the header.
        According to the docs, a SAM header has:
            - RG = REGION tag
            - PG = PROGRAM tag
            - HD = HEAD tag
            - SQ = SEQUENCE tag
        Parameters
        ----------
        header_as_text : str
            Header as text (string)
        Returns
        -------
        header: SAMFileHeader
        """
        rg_list, sq_list, pg_list, hd_list = [], [], [], []
        lines = header_as_text.split('\n')
        for line in lines:
            if line.startswith('@SQ'):
                sq_list.append(line)
            elif line.startswith('@HD'):
                hd_list.append(line)
            elif line.startswith('@PG'):
                pg_list.append(line)
            elif line.startswith('@RG'):
                rg_list.append(line)
        return SAMFileHeader(rg_tag=rg_list, pg_tag=pg_list, hd_tag=hd_list, sq_tag=sq_list)


class SAMFileRGTagParser:

    @classmethod
    def _from_read_grp_to_dict(cls, read_grp):
        result = {}
        rg_tags = read_grp.split('\t')
        for tag in rg_tags[1:]:
            tokens = tag.split(':', 1)
            if len(tokens) < 2:
                print("What threw an exception: %s" % tokens)
                raise ValueError("The read grp is not formatted correctly.")
            result[tokens[0]] = tokens[1]
        return result


    @classmethod
    def parse(cls, read_grps):
        seq_center_list, seq_dates, platforms, libraries, samples, platform_units = [], [], [], [], [], []
        for read_grp in read_grps:
            read_grp_dict = cls._from_read_grp_to_dict(read_grp)
            if 'CN' in read_grp_dict:
                seq_center_list.append(read_grp_dict['CN'])
            if 'DT' in read_grp_dict:
                seq_dates.append(read_grp_dict['DT'])
            if 'SM' in read_grp_dict:
                samples.append(read_grp_dict['SM'])
            if 'LB' in read_grp_dict:
                libraries.append(read_grp_dict['LB'])
            if 'PU' in read_grp_dict:
                platform_units.append(read_grp_dict['PU'])
            if 'PL' in read_grp_dict:
                platforms.append(read_grp_dict['PL'])

        return SAMFileRGTag(
            seq_centers=[_f for _f in list(set(seq_center_list)) if _f],
            seq_dates=[_f for _f in list(set(seq_dates)) if _f],
            platforms=[_f for _f in list(set(platforms)) if _f],
            libraries=[_f for _f in list(set(libraries)) if _f],
            samples=[_f for _f in list(set(samples)) if _f],
            platform_units=[_f for _f in list(set(platform_units)) if _f]
        )


class SangerSeqSAMFileRGTagParser:

#    class RGTagParser:
    LANELET_NAME_REGEX = '[0-9]{4}_[0-9]{1}#[0-9]{1,2}'
    LANE_NAME_REGEX = '[0-9]{4}_[0-9]{1}'

    @classmethod
    def parse(cls, tags: typing.Sequence):
        """ This method parses all the RGs (ReadGroup) in the list received as parameter
        and returns a BAMHeaderRG containing the information found there.
        Parameters
        ----------
        rgs_list: list
            A list of dicts, in which each dict represents a RG - e.g.:[{'ID': 'SZAIPI037128-51',
            'LB': 'SZAIPI037128-51', 'PL': 'illumina', 'PU': '131220_I875_FCC3K7HACXX_L4_SZAIPI037128-51',
            'SM': 'F05_XX629745'}]
        Returns
        -------
        BAMHeaderRG
            An object containing the fields of the RG tags.
        """
        seq_center_list, seq_dates, lanelets, platforms, libraries, samples = [], [], [], [], [], []
        for read_grp in tags:
            is_sanger_sample = False
            if 'CN' in read_grp:
                seq_center_list.append(read_grp['CN'])
                if read_grp['CN'] == 'SC':
                    is_sanger_sample = True
            if 'DT' in read_grp:
                seq_dates.append(read_grp['DT'])
            if 'SM' in read_grp:
                samples.append(read_grp['SM'])
            if 'LB' in read_grp:
                libraries.append(read_grp['LB'])
            if 'PU' in read_grp and is_sanger_sample:
                lanelet = cls._extract_lanelet_name_from_pu_entry(read_grp['PU'])
                if lanelet:
                    lanelets.append(lanelet)
                platf = cls._extract_platform_list_from_rg(read_grp)
                if platf:
                    platforms.append(platf)
            if not is_sanger_sample and 'PL' in read_grp:
                platforms.append(read_grp['PL'])

        return SAMFileHeader.RGTag(
            seq_centers=[_f for _f in list(set(seq_center_list)) if _f],
            seq_dates=[_f for _f in list(set(seq_dates)) if _f],
            lanelets=[_f for _f in list(set(lanelets)) if _f],
            platforms=[_f for _f in list(set(platforms)) if _f],
            libraries=[_f for _f in list(set(libraries)) if _f],
            samples=[_f for _f in list(set(samples)) if _f]
        )


    @classmethod
    @wrappers.check_args_not_none
    def _extract_platform_list_from_rg(cls, rg_dict):
        """ This method extracts the platform from a file's rg list
            In Sanger BAM files, the header contains:
            'PL': 'ILLUMINA' - for platform
            and
            'PU': '120910_HS11_08408_B_C0PNFACXX_7#71'
            which in this case has HS (= Illumina HiSeq) as mention of the platform on which it has been run.
        """
        platform = ''
        if 'PL' in rg_dict:
            platform = rg_dict['PL']
        if 'PU' in rg_dict:
            platform = str(platform) + ' ' + str(cls._extract_platform_from_pu_entry(rg_dict['PU']))
        return platform


    @classmethod
    @wrappers.check_args_not_none
    def _extract_lanelet_name_from_pu_entry(cls, pu_entry):
        """ This method extracts the lanelet name from the pu entry.
            WARNING! This works only for Sanger-sequenced data.
            Parameters
            ----------
            PU entry: str
                This is part of RG part of the header, it looks like this: 121211_HS2_08985_B_C16GWACXX_4#16
            Returns
            -------
            lanelet: str
                This is the name of the lanelet extracted from this part of the header, looking like: e.g. 1234_1#1
        """
        pattern = re.compile(cls.LANELET_NAME_REGEX)
        if pattern.match(pu_entry) is not None:  # PU entry is just the name of a lanelet
            return pu_entry
        else:
            run = cls._extract_run_from_pu_entry(pu_entry)
            lane = cls._extract_lane_from_pu_entry(pu_entry)
            tag = cls._extract_tag_from_pu_entry(pu_entry)
            if run and lane and tag:
                return cls._build_lanelet_name(run, lane, tag)
        return None


    @classmethod
    @wrappers.check_args_not_none
    def _extract_platform_from_pu_entry(cls, pu_entry):
        """ This method extracts the platform from the string found in
            the BAM header's RG section, under PU entry:
            e.g.'PU': '120815_HS16_08276_A_C0NKKACXX_4#1'
            => after the first _ : HS = Illumina HiSeq
        """
        beats_list = pu_entry.split("_")
        if len(beats_list) < 6:
            return None
        platf_beat = beats_list[1]
        pat = re.compile(r'([a-zA-Z]+)(?:[0-9])+')
        if pat.match(platf_beat) is not None:
            return pat.match(platf_beat).groups()[0]
        return None


    @classmethod
    @wrappers.check_args_not_none
    def _extract_lane_from_pu_entry(cls, pu_entry):
        """ This method extracts the lane from the string found in
            the BAM header's RG section, under PU entry => between last _ and #.
            A PU entry looks like: '120815_HS16_08276_A_C0NKKACXX_4#1'.
        """
        beats_list = pu_entry.split("_")
        if len(beats_list) < 6:
            return None
        if beats_list:
            last_beat = beats_list[-1]
            if last_beat[0].isdigit():
                return int(last_beat[0])
        return None

    @classmethod
    @wrappers.check_args_not_none
    def _extract_tag_from_pu_entry(cls, pu_entry):
        """ This method extracts the tag nr from the string found in the
            BAM header - section RG, under PU entry => the nr after last #
        """
        last_hash_index = pu_entry.rfind("#", 0, len(pu_entry))
        if last_hash_index != -1:
            if pu_entry[last_hash_index + 1:].isdigit():
                return int(pu_entry[last_hash_index + 1:])
        return None

    @classmethod  #to unittest this one - cause it seems to be correct but it doesn't detect the lane correctly...
    @wrappers.check_args_not_none
    def _extract_run_from_pu_entry(cls, pu_entry):
        """ This method extracts the run nr from the string found in
            the BAM header's RG section, under PU entry => between 2nd and 3rd _.
        """
        beats_list = pu_entry.split("_")
        if len(beats_list) < 6:
            return None
        run_beat = beats_list[2]
        if run_beat[0] == '0':
            return int(run_beat[1:])
        if run_beat.isdigit():
            return int(run_beat)
        return None


    @classmethod
    def _build_lanelet_name(cls, run, lane, tag=None):
        if run and lane:
            if tag:
                return str(run) + '_' + str(lane) + '#' + str(tag)
            else:
                return str(run) + '_' + str(lane)
        return None

