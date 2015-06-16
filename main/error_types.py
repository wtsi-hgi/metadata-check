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

This file has been created on Jun 12, 2015.
"""
from collections import namedtuple

# HeaderVsIrodsMetadataError = namedtuple('HeaderVsIrodsMetadataError', ['fpath', 'h_value', 'i_value'])
# IrodsVsSeqscapeMetadataError = namedtuple('IrodsVsSeqscapeMetadataError', ['fpath', 'i_value', 'ss_value'])
# IrodsMetadataAttributeFrequencyError = namedtuple('IrodsMetadataAttributesError', ['fpath', 'attribute', 'desired_frequency', 'actual_frequency'])
# WrongReferenceError = namedtuple('WrongReferenceError', ['fpath', 'desired_ref', 'h_ref', 'i_ref'])
# WrongMD5Error = namedtuple('WrongMD5Error', ['fpath', 'imeta_value', 'ichksum_value'])
#


class HeaderVsIrodsMetadataError(Exception):

    def __init__(self, fpath, header_value, irods_value):
        self.fpath = fpath
        self.header_value = header_value
        self.irods_value = irods_value


class IrodsVsSeqscapeMetadataError(Exception):

    def __init__(self, fpath, irods_value, seqsc_Value):
        self.fpath = fpath
        self.irods_value = irods_value
        self.seqsc_value = seqsc_Value


class IrodsMetadataAttributeFrequencyError(Exception):

    def __init__(self, fpath, attribute, desired_occurances, actual_occurances):
        self.fpath = fpath
        self.attribute = attribute
        self.desired_occurances = desired_occurances
        self.actual_occurances = actual_occurances


class WrongReferenceError(Exception):

    def __init__(self, fpath, desired_ref, header_ref, irods_ref):
        self.fpath = fpath
        self.desired_ref = desired_ref
        self.header_ref = header_ref
        self.irods_ref = irods_ref


class WrongMD5Error(Exception):

    def __init__(self, fpath, imeta_value, ichksum_value):
        self.fpath = fpath
        self.imeta_value = imeta_value
        self.ichksum_value = ichksum_value



