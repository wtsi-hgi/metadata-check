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
#from collections import namedtuple

# HeaderVsIrodsMetadataError = namedtuple('HeaderVsIrodsMetadataError', ['fpath', 'h_value', 'i_value'])
# IrodsVsSeqscapeMetadataError = namedtuple('IrodsVsSeqscapeMetadataError', ['fpath', 'i_value', 'ss_value'])
# IrodsMetadataAttributeFrequencyError = namedtuple('IrodsMetadataAttributesError', ['fpath', 'attribute', 'desired_frequency', 'actual_frequency'])
# WrongReferenceError = namedtuple('WrongReferenceError', ['fpath', 'desired_ref', 'h_ref', 'i_ref'])
# WrongMD5Error = namedtuple('WrongMD5Error', ['fpath', 'imeta_value', 'ichksum_value'])
#



class HeaderVsIrodsMetadataAttributeError(Exception):

    def __init__(self, fpath, attribute, header_value, irods_value, entity_type=None):
        self.fpath = fpath
        self.attribute = attribute
        self.header_value = header_value
        self.irods_value = irods_value
        self.entity_type = entity_type

    def __str__(self):
        #entity_type = self.entity_type if self.entity_type else ""
        if self.entity_type:
            return "File: " + str(self.fpath) + "'s metadata for " +str(self.entity_type) + ", attribute: " + str(self.attribute) + \
               " is inconsistent between iRODS: " + str(self.irods_value) + " and header value: " + \
               str(self.header_value)
        return "File: " + str(self.fpath) + "'s metadata attribute: " + str(self.attribute) + \
               " is inconsistent between iRODS: " + str(self.irods_value) + " and header value: " + \
               str(self.header_value)

    def __repr__(self):
        return self.__str__()


class IrodsVsSeqscapeMetadataAttributeError(Exception):

    def __init__(self, fpath, attribute, irods_value, seqsc_value, entity_type=None):
        self.fpath = fpath
        self.attribute = attribute
        self.irods_value = irods_value
        self.seqsc_value = seqsc_value
        self.entity_type = entity_type

    def __str__(self):
        if self.entity_type:
            return "File: " + str(self.fpath) + "'s metadata for "+str(self.entity_type)+", attribute: " + str(self.attribute) + \
               " is inconsistent between iRODS " + str(self.irods_value) + " and seqscape value: " + \
               str(self.seqsc_value)
        return "File: " + str(self.fpath) + "'s metadata attribute: " + str(self.attribute) + \
               " is inconsistent between iRODS " + str(self.irods_value) + " and seqscape value: " + \
               str(self.seqsc_value)

    def __repr__(self):
        return self.__str__()


class IrodsMetadataAttributeVsFileNameError(Exception):

    def __init__(self, fpath, attribute, irods_value, filename_value):
        self.fpath = fpath
        self.attribute = attribute
        self.irods_value = irods_value
        self.filename_value = filename_value

    def __str__(self):
        return "File: " + str(self.fpath) + " has in iRODS " + str(self.attribute) + " = " + str(self.irods_value) + \
               " while in the file name it is " +str(self.filename_value)

    def __repr__(self):
        return self.__str__()


class IrodsMetadataAttributeFrequencyError(Exception):

    def __init__(self, fpath, attribute, desired_occurances, actual_occurances):
        self.fpath = fpath
        self.attribute = attribute
        self.desired_occurances = desired_occurances
        self.actual_occurances = actual_occurances

    def __str__(self):
        return "In file: " + str(self.fpath) + " metadata attribute: " + str(self.attribute) + " appears " + \
               str(self.actual_occurances) + " times, while it should appear " + str(self.desired_occurances) + \
               " according to the config you've given."

    def __repr__(self):
        return self.__str__()


class WrongReferenceError(Exception):

    def __init__(self, fpath, desired_ref, irods_ref, header_ref=None):
        self.fpath = fpath
        self.desired_ref = desired_ref
        #self.header_ref = header_ref
        self.irods_ref = irods_ref

    def __str__(self):
        return "File: " + str(self.fpath) + " was aligned to reference: " + str(self.irods_ref) + \
               " while the desired ref is: " + str(self.desired_ref)

    def __repr__(self):
        return self.__str__()


class WrongMD5Error(Exception):

    def __init__(self, fpath, imeta_value, ichksum_value):
        self.fpath = fpath
        self.imeta_value = imeta_value
        self.ichksum_value = ichksum_value

    def __str__(self):
        return "File: " + str(self.fpath) + " has different MD5 checksum in iRODS metadata: " + str(self.imeta_value) +\
               " compared to the value returned by ichksum: " + str(self.ichksum_value)

    def __repr__(self):
        return self.__str__()


class NotFoundInSeqscapeError(Exception):

    def __init__(self, id_type, id_missing, entity_type, fpath=None):
        self.fpath = fpath
        self.id_type = id_type
        self.id_missing = id_missing
        self.entity_type = entity_type

    def __str__(self):
        if not self.fpath:
            return "The " + str(self.entity_type) + " couldn't be found in Seqscape when querying by "+ str(self.id_type) +" = " + str(self.id_missing)
        return "For file " + str(self.fpath) + " the " + str(self.entity_type) + " couldn't be found in Seqscape when querying by "+ str(self.id_type) +" = " + str(self.id_missing)

    def __repr__(self):
        return self.__str__()

class TooManyEntitiesSameIdSeqscapeError(Exception):

    def __init__(self, id_type, id_value, entities, entity_type, fpath=None):
        self.fpath = fpath
        self.id_type = id_type
        self.ids_list = id_value
        self.entity_type = entity_type
        self.entites = entities

    def __str__(self):
        if not self.fpath:
            return "There were more than 1 " + str(self.entity_type) + "s with  "+ str(self.id_type) + " = " + \
                   str(self.ids_list) +" found in Seqscape: " + str(self.entites)
        return "For file " + str(self.fpath) + " there were more than 1 " + str(self.entity_type) + "s with  " + \
               str(self.id_type) + " = " + str(self.ids_list) +" found in Seqscape: " + str(self.entites)


class DifferentEntitiesFoundInSeqscapeQueryingByDiffIdTypesError(Exception):

    def __init__(self, entity_type, id_type1, entities_set1, id_type2, entities_set2, fpath=None):
        self.entity_type = entity_type
        self.id_type1 = id_type1
        self.id_type2 = id_type2
        self.entities_set1 = entities_set1
        self.entities_set2 = entities_set2
        self.fpath = fpath

    def __str__(self):
        if not self.fpath:
            return "I found different "+ str(self.entity_type) +"s in Seqscape when querying by " + \
               str(self.id_type1) +": " + str(self.entities_set1) + " compared to querying by " + \
               str(self.id_type2) + ": " + str(self.entities_set2)
        return "For file: " + str(self.fpath) + " I found different "+ str(self.entity_type) + \
               "s in Seqscape when querying by " + \
               str(self.id_type1) +": " + str(self.entities_set1) + " compared to querying by " + \
               str(self.id_type2) + ": " + str(self.entities_set2)


class WrongMetadataValue(Exception):

    def __init__(self, fpath, attribute, value):    # , correct_range=None
        self.fpath = fpath
        self.attribute = attribute
        self.value = value
#        self.correct_range = correct_range

    def __str__(self):
        # if self.correct_range:
        #     return "ERROR - The attribute: " + str(self.attribute) + " has a value outside of its range: " + \
        #            str(self.value) + " (correct range = " + str(self.correct_range) + ")"

        return "ERROR - for file: " + self.fpath + " the attribute: " + str(self.attribute) + " has a value outside of its range: " + str(self.value)


class TestImpossibleToRunError(Exception):

    def __init__(self, fpath, test_name, reason):
        self.fpath = fpath
        self.test_name = test_name
        self.reason = reason

    def __str__(self):
        return "Can't run test " + str(self.test_name) + " on file: " + str(self.fpath) + ". Reason: " + str(self.reason)

    def __repr__(self):
        return self.__str__()

class SamplesDontBelongToGivenStudy(Exception):

    def __init__(self, sample_ids,  actual_study, desired_study):
        self.sample_ids = sample_ids
        self.actual_study = actual_study
        self.desired_study = desired_study

    def __str__(self):
        return "The sample " + str(self.sample_ids) + " belongs to study: " + str(self.actual_study) + \
               " while it should belong to: " + str(self.desired_study)

    def __repr__(self):
        return self.__str__()

class DifferentFilesRetrievedByDiffStudyIdsOfSameStudy(Exception):

    def __init__(self, diffs, id1, id2):
        self.diffs = diffs
        self.id1 = id1
        self.id2 = id2

    def __str__(self):
        return "ERROR - these files were retrieved when querying by " + str(self.id1) + " but not when querying by " + str(self.id2)

    def __repr__(self):
        return self.__str__()
