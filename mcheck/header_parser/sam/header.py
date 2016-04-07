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


class SAMFileHeader:
    def __init__(self, rg_tag=None, sq_tag=None, hd_tag=None, pg_tag=None):
        self.rg_tags = rg_tag
        self.sq_tags = sq_tag
        self.hd_tags = hd_tag
        self.pg_tags = pg_tag

    def __str__(self):
        return "RG tags: " + str(self.rg_tags)  # + ", SQ tags: " + str(self.sq_tags) + ", HD tags: " + \
        # str(self.hd_tags) + ", PG tags: " + str(self.pg_tags)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        print(self)
        print(str(type(self.rg_tags)))
        return self.rg_tags == other.rg_tags and self.sq_tags == other.sq_tags and \
               self.hd_tags == other.hd_tags and self.pg_tags == other.pg_tags

    class RGTag:
        def __init__(self, seq_centers=None, seq_dates=None, lanelets=None, platforms=None,
                     libraries=None, samples=None, platform_units=None):
            self.seq_centers = seq_centers if seq_centers else []
            self.seq_dates = seq_dates if seq_dates else []
            self.lanelets = lanelets if lanelets else []
            self.platforms = platforms if platforms else []
            self.libraries = libraries if libraries else []
            self.samples = samples if samples else []
            self.platform_units = platform_units if platform_units else []

        def __str__(self):
            return "CN: " + str(self.seq_centers) + "\n DATE: " + str(self.seq_dates) + "\n LANELETS: " + \
                   str(self.lanelets) + "\n PLATFORMS: " + str(self.platforms) + "\n PLATFORM UNITS: " + \
                   str(self.platform_units) + "\n LIBRARIES: " + str(self.libraries) + "\n SAMPLES: " + str(
                self.samples)

        def __repr__(self):
            return self.__str__()

        def __eq__(self, other):
            return set(self.seq_dates) == set(other.seq_dates) and set(self.seq_centers) == set(other.seq_centers) and \
                   set(self.lanelets) == set(other.lanelets) and set(self.platforms) == set(other.platforms) and \
                   set(self.libraries) == set(other.libraries) and set(self.samples) == set(other.samples) and \
                   set(self.platform_units) == set(other.platform_units)




