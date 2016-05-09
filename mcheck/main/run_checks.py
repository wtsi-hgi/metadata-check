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

This file has been created on May 05, 2016.
"""

import os

from mcheck.main import arg_parser
from mcheck.metadata.irods_metadata.irods_meta_provider import iRODSMetadataProvider
from mcheck.metadata.seqscape_metadata.seqscape_meta_provider import SeqscapeRawMetadataProvider
from mcheck.metadata.file_header_metadata.header_meta_provider import SAMFileHeaderMetadataProvider
from mcheck.metadata.seqscape_metadata.seqscape_metadata import SeqscapeMetadata
from mcheck.metadata.irods_metadata.irods_file_metadata import IrodsSeqFileMetadata

def read_file_into_list(fofn_path):
    fofn_fd = open(fofn_path)
    files_list = [f.strip() for f in fofn_fd]
    fofn_fd.close()
    return files_list


def write_list_to_file(input_list, output_file, header=None):
    out_fd = open(output_file, 'a')
    if header:
        out_fd.write(header+'\n')
    for entry in input_list:
        out_fd.write(entry+'\n')
    out_fd.write('\n')
    out_fd.close()

def write_tuples_to_file(tuples, output_file, header_tuple=None):
    out_fd = open(output_file, 'a')
    for elem in header_tuple:
        out_fd.write(str(elem)+"\t")
    out_fd.write("\n")
    for tup in tuples:
        for elem in tup:
            out_fd.write(str(elem)+"\t")
        out_fd.write("\n")
    out_fd.close()

class BulkMetadataRetrieval:

    @staticmethod
    def fetch_irods_metadata_by_metadata(search_criteria):
        """
        Queries iRODS for all the files that match the search criteria and fetch all the metadata for them.
        :param search_criteria: a dict with: key = search field name, value = search field value
        :return:
        """
        return iRODSMetadataProvider.retrieve_raw_files_metadata_by_metadata(search_criteria)


class FileMetadataRetrieval:

    @staticmethod
    def fetch_and_check_seqscape_metadata(samples, libraries, studies):
        raw_metadata = SeqscapeRawMetadataProvider.fetch_raw_metadata(samples, libraries, studies)
        problems = raw_metadata.check_metadata()
        seqsc_metadata = SeqscapeMetadata.from_raw_metadata(raw_metadata)
        problems.extend(seqsc_metadata.check_metadata())
        return seqsc_metadata, problems

    @staticmethod
    def fetch_and_check_header_metadata(fpath):
        header_metadata = SAMFileHeaderMetadataProvider.fetch_metadata(fpath, irods=True)
        problems = header_metadata.check_metadata()
        header_metadata.fix_metadata()
        return header_metadata, problems

    @staticmethod
    def fetch_and_check_irods_metadata_by_path(fpath, reference):
        raw_metadata = iRODSMetadataProvider.fetch_raw_file_metadata_by_path(fpath)
        problems = raw_metadata.check_metadata()
        seq_metadata = IrodsSeqFileMetadata.from_raw_metadata(raw_metadata)
        problems.extend(seq_metadata.check_metadata(reference))
        return seq_metadata, problems


# @classmethod
# def retrieve_files_metadata_by_metadata(cls, search_criteria_dict, zone=None):
#     search_crit_list = []
#     for k, v in search_criteria_dict.items():
#         search_criterion = SearchCriterion(k, v)
#         search_crit_list.append(search_criterion)
#
#     # Getting metadata from iRODS:
#     connection = connect_to_irods_with_baton(config.BATON_BIN, skip_baton_binaries_validation=True) # type: Connection
#     list_of_data_objs_and_metadata = connection.data_object.get_by_metadata(search_crit_list, zone)
#     raw_meta_objects = [IrodsRawFileMetadata.from_baton_wrapper(data_obj) for data_obj in list_of_data_objs_and_metadata]
#     return raw_meta_objects
#




def main():
    args = arg_parser.parse_args()

    # print('args: %s' %args.metadata_fetching_strategy)
    print('args: %s' %args)
    files_metadata_dict = {}    # key = filepath, value = metadata (avus + checksum and others)

    if args.metadata_fetching_strategy == 'fetch_by_metadata':
        search_criteria = {}
        if args.filter_npg_qc:
            search_criteria['manual_qc'] = args.filter_npg_qc
        if args.filter_target:
            search_criteria['target'] = args.filter_target

        # Parse input parameters and obtain files+metadata:
        if args.study_name:
            search_criteria['study'] = args.study_name
        elif args.study_acc_nr:
            search_criteria['study_accession_number'] = args.study_acc_nr
        elif args.study_internal_id:
            search_criteria['study_internal_id'] = args.study_internal_id

        files_metadata_objs_list = iRODSMetadataProvider.retrieve_raw_files_metadata_by_metadata(search_criteria, args.irods_zone)
        for obj in files_metadata_objs_list:
            fpath = os.path.join(obj.dir_path, obj.fname)
            files_metadata_dict[fpath] = obj

    elif args.metadata_fetching_strategy == 'fetch_by_path':
        for fpath in args.fpaths_irods:
            file_metadata = iRODSMetadataProvider.fetch_raw_file_metadata_by_path(fpath)
            files_metadata_dict[fpath] = file_metadata




main()





fpath = '/seq/illumina/library_merge/13841100.CCXX.paired310.4199421624/13841100.CCXX.paired310.4199421624.cram'
h_meta = FileMetadataRetrieval.fetch_and_check_header_metadata(fpath)
seqsc_meta, errs = FileMetadataRetrieval.fetch_and_check_seqscape_metadata(samples=h_meta.samples, libraries=h_meta.libraries, studies=h_meta.studies )
irods_meta = FileMetadataRetrieval.fetch_and_check_irods_metadata_by_path(fpath)
print("H METAAAAA: %s\n" % h_meta)
print("Seqscape meta: %s\n" % str(seqsc_meta))
print("Irods meta: %s\n" % irods_meta)


print("\nSamples from H META:     %s" % h_meta.samples)
print("\nSamples from IRODS META: %s" % irods_meta.samples)
print("\nSamples from SEQSCAPE:   %s" % seqsc_meta.samples)

print("\nLibraries from H META:     %s" % h_meta.libraries)
print("\nLibraries from IRODS META: %s" % irods_meta.libraries)
print("\nLibraries from SEQSCAPE:   %s" % seqsc_meta.libraries)

print("Metadata comparison head vs irod: %s" % FileMetadataComparison.compare_entities(h_meta.libraries, irods_meta.libraries))
print("Metadata comparison irod vs seqs: %s" % FileMetadataComparison.compare_entities(irods_meta.libraries, seqsc_meta.libraries))
print("Metadata comparison head vs seqs: %s" % FileMetadataComparison.compare_entities(h_meta.libraries, seqsc_meta.libraries))


    