"""
Copyright (C) 2016  Genome Research Ltd.

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

This file has been created on Jan 12, 2016.
"""

import subprocess

import config
from mcheck.com import wrappers


class SamFileHeaderExtractor:
    @classmethod
    @wrappers.check_args_not_none
    def extract(cls, fpath):
        """
            This method extract the header from a file and returns it as text (string)
        """
        child_proc = subprocess.Popen([config.SAMTOOLS_PATH, 'view', '-H', fpath],
                                      stderr=subprocess.PIPE,
                                      stdout=subprocess.PIPE)
        (out, err) = child_proc.communicate()
        if err:
            print("ERROR calling samtools on " + str(fpath))
            raise IOError(err)
        out = out.decode("utf-8")
        return out


class IrodsSamFileHeaderExtractor(SamFileHeaderExtractor):
    @classmethod
    @wrappers.check_args_not_none
    def extract(cls, fpath):
        """
            This method extracts the header from iRODS storage and returns it as text.
            Parameters
            ----------
            path : str
                The path to the file in iRODS
            Returns
            -------
            header : str
                The header of the file as text.
            Raises
            ------
            IOError - if the file header could not have been extracted
                        (probably because the file could not be accessed in iRODS)
        """
        irods_fpath = 'irods:' + str(fpath)
        return super().extract(irods_fpath)


class LustreSamFileHeaderExtractor(SamFileHeaderExtractor):
    """
    This class inherits all its functionality from the parent. It's been created for consistency reasons.
    """
    pass



