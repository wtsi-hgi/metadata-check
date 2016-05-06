"""
Copyright (C) 2015  Genome Research Ltd.

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

This file has been created on Nov 19, 2015.
"""


class AttributeCount:
    """
    This class is for keeping track of how many attributes with different values are there within a type of metadata.
    """
    def __init__(self, attribute: str, count: int, operator: str):
        self.attribute = attribute
        self.count = count
        self.operator = operator

    def __str__(self):
        return "Attribute = " + str(self.attribute) + ", count = " + str(self.count) + ", operator = " + str(self.operator)

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.attribute) + hash(self.count) + hash(self.operator)


# class AttributeCountComparison:
#
#     def __init__(self, attribute: str, actual_count: int, threshold: int, operator: str, ):
#         self.attribute = attribute
#         self.actual_count = actual_count
#         self.threshold = threshold
#         self.operator = operator
