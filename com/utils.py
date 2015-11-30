"""
Copyright (C) 2013, 2014  Genome Research Ltd.

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

"""

import os
import time
import unicodedata
import datetime
import collections

from os.path import isfile, join, exists
from collections import defaultdict
from com import wrappers


#################################################################################
'''
 This class contains small utils functions, for general purpose and not specific
 to the controller side or the workers side.
'''
#################################################################################

########################## GENERAL USE FUNCTIONS ################################



######################### JSON CONVERSION #######################################
#
#
#def serialize(data):
#    return simplejson.dumps(data)
#
#
#def deserialize(data):
#    return simplejson.loads(data)


######################### UNICODE processing ####################################

def __ucode2str__(ucode):
    if type(ucode) == str:
        return unicodedata.normalize('NFKD', ucode).encode('ascii','ignore')
    return ucode

def __ucode2str_list__(ucode_list):
    str_list = []
    for elem in ucode_list:
        elem = unicode2string(elem)
        str_list.append(elem)
    return str_list
    

def __ucode2str_dict__(ucode_dict):
    ''' This function takes a dict of unicode characters
        and returns a dict of strings.
    '''
    str_dict = dict()
    for key, val in list(ucode_dict.items()):
        key = unicode2string(key)
        val = unicode2string(val)
        str_dict[key] = val
    return str_dict

def unicode2string(ucode):
    ''' This function converts a unicode type into string.
        The input type can be a dict, list, or unicode characters.
    '''
    if type(ucode) == dict:
        return __ucode2str_dict__(ucode)
    elif type(ucode) == list:
        return __ucode2str_list__(ucode)
    elif type(ucode) == str:
        return __ucode2str__(ucode)
    return ucode


############## CHECK ON FILES TIMESTAMPS #####################

    
def cmp_timestamp_files(file_path1, file_path2):
    ''' This function receives 2 files and compares their
        timestamp. 
        Returns:
            -1 if file1 is older than file2
             0 if they have the same timestamp
             1 if file1 is newer than files2.
    '''
    tstamp1 = os.path.getmtime(file_path1)
    tstamp2 = os.path.getmtime(file_path2)
    tstamp1 = datetime.datetime.fromtimestamp(tstamp1)
    tstamp2 = datetime.datetime.fromtimestamp(tstamp2)
    return cmp(tstamp1, tstamp2)


############## FILE NAME/PATH/EXTENSION PROCESSING ###########

def extract_fname_and_ext(fpath):
    ''' This function splits the filename in its last extension
        and the rest of it. The name might be confusion, as for
        files with multiple extensions, it only separates the last
        one from the rest of them. 
        e.g. UC123.bam.bai.md5 => fname=UC123.bam.bai, ext=md5
    '''
    _, tail = os.path.split(fpath)
    fname, ext = os.path.splitext(tail)
    ext = ext[1:]
    return (fname, ext)

@wrappers.check_args_not_none
def extract_fname(fpath):
    _, fname = os.path.split(fpath)
    return fname

@wrappers.check_args_not_none
def extract_fname_without_ext(fpath):
    ''' Extracts the file name (and removes the extensions), given a file path.'''
    #_, fname = os.path.split(fpath)
    fname = extract_fname(fpath)
    basename, _ = os.path.splitext(fname)
    return basename

@wrappers.check_args_not_none
def extract_dir_path(fpath):
    ''' Extracts the root directory from a filepath.'''
    if os.path.isdir(fpath):
        return fpath
    return os.path.dirname(fpath)

#def extract_file_extension(fpath):
#    _, tail = os.path.split(fpath)
#    _, ext = os.path.splitext(tail)
#    return ext[1:]
# 
    
    
def list_and_filter_files_from_dir(dir_path, accepted_extensions):
    ''' This function returns all the files of the types of interest 
        (e.g.bam, vcf, and ignore .txt) from a directory given as parameter.
    '''
    files_list = []
    for f_name in os.listdir(dir_path):
        f_path = join(dir_path, f_name)
        if isfile(f_path):
            _, f_extension = os.path.splitext(f_path)
            if f_extension[1:] in accepted_extensions:
                files_list.append(f_path)
    print(files_list)
    return files_list

@wrappers.check_args_not_none
def get_filename_from_path(fpath):
    if fpath in ["\n", " ","","\t"]:
        raise ValueError("File path empty")
    f_path = fpath.lstrip().strip()
    return os.path.basename(f_path)

@wrappers.check_args_not_none
def get_filepaths_from_fofn(fofn):
    files_list = [f for f in open(fofn, 'r')]
    return [_f for _f in files_list if _f]


def get_filenames_from_filepaths(filepaths_list):
    return [get_filename_from_path(file_path) for file_path in filepaths_list]


def filter_list_of_files_by_type(list_of_files, filters):
    ''' Filters the initial list of files and returns a new list of files
        containing only the file types desired (i.e. given as filters parameter).
    '''
    files_filtered = []
    for f in list_of_files:
        _, tail = os.path.split(f)
        _, ext = os.path.splitext(tail)
        ext = ext[1:]
        if ext in filters:
            files_filtered.append(f)
        else:
            print("SMTH else in this dir:",f)
    return files_filtered

@wrappers.check_args_not_none
def extract_file_extension(fpath):
    if not fpath:
        return None
    _, tail = os.path.split(fpath)
    _, ext = os.path.splitext(tail)
    return ext[1:].strip()


def lists_contain_same_elements(list1, list2):
        return set(list1) == set(list2)



#################### PROJECT SPECIFIC UTILITY FUNCTIONS #####################


def filter_out_invalid_paths(file_paths_list):
    return [fpath for fpath in file_paths_list if fpath not in [None, ' ', '']]
    

def get_file_duplicates(files_list):
    if len(files_list)!=len(set(files_list)):
        return [x for x, y in list(collections.Counter(files_list).items()) if y > 1]
    return []


def list_fullpaths_from_dir(path):
    ''' Throws a ValueError if the dir doesn't exist or the path 
        is not a dir or if the dir is empty. 
        Returns the list of files from that dir.
    '''
    return [join(path, fname) for fname in os.listdir(path)]


def split_path_in_components(path):
    folders=[]
    while 1:
        path,folder=os.path.split(path)
    
        if folder!="":
            folders.append(folder)
        else:
            if path!="":
                folders.append(path)
            break
    folders.reverse()
    return folders


def get_all_file_types(fpaths_list):
    ''' 
        This function receives a list of file paths as argument and extracts
        from it a set of all the files types of the files in the list. 
    '''
    file_types = set()
    for f in fpaths_list:
        ext = extract_file_extension(f)
        if ext:
            file_types.add(ext)
    return file_types


def filter_out_none_keys_and_values(my_dict):
    return {k:v for (k,v) in my_dict.items() if k is not None and v is not None}

def check_all_keys_have_the_same_value(my_dict, my_value=None):
        if my_value:
            return all(val==my_value for val in list(my_dict.values()))
        return len(set(my_dict.values()))==1
    

###########################################################################

# MOVED TO files.py
# def build_irods_staging_path(submission_id):
#     ''' This function returns the path to the corresponding staging area
#         collection, given the submission id. 
#     '''
#     return os.path.join(configs.IRODS_STAGING_AREA, submission_id)
# 
# def build_irods_file_staging_path(submission_id, file_path_client):
#     ''' 
#         This function puts together the path where a file is stored in irods_metadata staging area.
#     '''
#     (_, fname) = os.path.split(file_path_client)
#     return os.path.join(configs.IRODS_STAGING_AREA, submission_id, fname)
#         

#def build_file_path_irods(client_file_path, irods_coll_path):
#    (_, src_file_name) = os.path.split(client_file_path)  
#    return os.path.join(irods_coll_path, src_file_name)


def is_field_empty(obj, field):
    return not (hasattr(obj, field) and getattr(obj, field) != None)


def is_date_correct(date):
    try:
        date_struct = time.strptime(date, "%Y-%m-%d")
    except ValueError:
        # Only caught the error to change the message with a more relevant one
        raise ValueError("Error: date is not in the correct format.")
    year = date_struct.tm_year
    print(year)
    max_year = datetime.date.today().year
    if int(year) < 2010:
        raise ValueError("The year given is incorrect. Min year = 2013")
    if int(year) > max_year:
        raise ValueError("The year given is incorrect. Max year = "+str(max_year))
    return True
        

############## OTHER GENERAL UTILS ################

def get_today_date():
    today = datetime.date.today()
    return today.isoformat()

def get_date_and_time_now():
    return time.strftime("%H:%M on %d/%m/%Y")
    
    

    # Working - gets both date and time:
    #    now = datetime.datetime.now()
    #    return now.isoformat()
    
    #today = datetime.date.today()
    #    year = str(today.year)
    #    month = str(today.month)
    #    day = str(today.day)
    #    if len(month) == 1:
    #        month = "0" + month
    #    if len(day) == 1:
    #        day = "0" + day
    #    return str(year) + str(month) + str(day)
    
    # Working - Martin's format
    #    today = datetime.date.today()
    #    year = str(today.year)
    #    month = str(today.month)
    #    day = str(today.day)
    #    if len(month) == 1:
    #        month = "0" + month
    #    if len(day) == 1:
    #        day = "0" + day
    #    return str(year) + str(month) + str(day)


def levenshtein(a,b):
    "Calculates the Levenshtein distance between a and b."
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a,b = b,a
        n,m = m,n
        
    current = list(range(n+1))
    for i in range(1,m+1):
        previous, current = current, [i]+[0]*n
        for j in range(1,n+1):
            add, delete = previous[j]+1, current[j-1]+1
            change = previous[j-1]
            if a[j-1] != b[i-1]:
                change = change + 1
            current[j] = min(add, delete, change)
            
    return current[n]


############################# ADJACENT THINGS -- PROBABLY SHOULD BE HERE!!! Until I think things through and try diff options ###########

@wrappers.check_args_not_none
def compare_strings(str1, str2):
    ''' Compares two strings and returns True if they are identical, False if not.'''
    return str1 == str2
    
    
def compare_strings_ignore_case(str1, str2):
    ''' Compares two strings ignoring the case. Returns True if they match, False if not.'''
    return compare_strings(str1.lower(), str2.lower())


def get_key_counts(tuples_list):
    ''' 
        This function calculates the number of occurences of
        each key in the list of tuples received as parameter.
        Returns a dict containing: key - occurances.
    '''
    key_freq_dict = defaultdict(int)
    for item in tuples_list:
        key_freq_dict[item[0]] += 1
    return key_freq_dict


    
    
    
