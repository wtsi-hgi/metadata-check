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

This file has been created on Jul 27, 2016.
"""

import json
from mcheck.results.checks_results import RESULT, CheckResult    #, CheckResultJSONEncoder
from hgijson import MappingJSONEncoderClassBuilder, JsonPropertyMapping, MappingJSONDecoderClassBuilder

def format_output_as_tsv(check_results_by_path):
    """
    This function converts a dictionary of key = fpath, values = CheckResults into a tab delimited values string.
    :param check_results_by_path:
    :return:
    """
    result_str = ''
    if check_results_by_path:
        result_str += "Fpath\tExecuted\tResult\tErrors\t"
        for fpath, issues in check_results_by_path.items():
            for issue in issues:
                errors = issue.error_message if (issue.error_message or issue.error_message is None) else None
                result_str = result_str + str(fpath) + '\t' + str(issue.check_name) + '\t' + str(
                    issue.executed) + '\t' + str(
                    issue.result) + '\t' + str(errors) + '\n'
    return result_str



def format_output_as_json(check_results_by_path):
    """
    This function takes as input a dict where key = filepath, value = list of CheckResults and formats them to json.
    :param check_results_by_path: dict - key = str (filepath), value = list[CheckResult]
    :return: json formatted string
    """
    CheckResultJSONEncoder = MappingJSONEncoderClassBuilder(CheckResult, CheckResult.to_json_mapping()).build()
    return json.dumps(check_results_by_path, cls=CheckResultJSONEncoder)