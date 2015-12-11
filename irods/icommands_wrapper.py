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


This file has been created on Oct 27, 2014
"""



import os
import subprocess
from . import exceptions

from com import wrappers, utils
from irods import data_types as irods_types

from . import constants
######################## UTILS ##########################################

def assemble_new_irods_fpath(fpath, irods_coll):
    ''' 
        This function puts together the new file path of a file which has been moved
        or copied from fpath to an irods collection, where fpath is a non-irods storage resource
        (e.g. lustre).
    '''
    fname = utils.extract_fname(fpath)
    return os.path.join(irods_coll, fname)
# 
# def assemble_irods_username(username, zone):
#     return username+"#"+zone
# 
# def assemble_irods_sanger_username(username):
#     return assemble_irods_username(username, constants.IRODS_SANGER_ZONE)
# 
# def assemble_irods_humgen_username(username):
#     return assemble_irods_username(username, constants.IRODS_HUMGEN_ZONE)

######################## ICOMMANDS CALLING FUNCTIONS #####################

class iRODSOperations(object):
    '''
        This is an abstract class, parent of all the classes implementing 
        wrappers around the icommands.
    '''
    @classmethod
    def _build_icmd_args(cls, cmd_name, args_list, options=[]):
        cmd_list = [cmd_name]
        cmd_list.extend(options)
        cmd_list.extend(args_list)
        return cmd_list

    @classmethod
    def _run_icmd(cls, cmd_args):
        child_proc = subprocess.Popen(cmd_args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        (out, err) = child_proc.communicate()
        if err:
            print("ERROR running icommand!!!! ")
            raise exceptions.iRODSException(err, out, cmd=str(cmd_args))
        return out
    
    @classmethod
    def _process_icmd_output(cls, output):
        raise NotImplementedError
    

class iRODSListOperations(iRODSOperations):
    

    @classmethod
    @wrappers.check_args_not_none
    def _run_ils_long(cls, path):
        ''' This function runs ils -l command on a file path and returns a list of lines
            received as result, which correspond each to a file replica:
            e.g.
             '  serapis           1 irods-ddn-rd10a-4           14344 2014-03-11.18:43   md5-check.out'
                serapis           2 irods-ddn-gg07-2           217896 2014-03-12.11:42 & md5-check.out'
             
        '''
        cmd_args = cls._build_icmd_args('ils', [path], ['-l'])
        try:
            return cls._run_icmd(cmd_args)
        except exceptions.iRODSException as e:
            raise exceptions.iLSException(err=e.error, output=e.output, cmd=e.cmd)
        
    
    @classmethod
    @wrappers.check_args_not_none
    def _process_file_line(cls, file_line):
            items = file_line.split()
            if len(items) < 6 or len(items) > 8:
                raise exceptions.UnexpectedIRODSiCommandOutputException(file_line)
            if len(items) == 7:
                is_paired = True
                file_name = items[6]
            else:
                is_paired = False
                file_name = items[5]
            return irods_types.FileLine(owner=items[0], replica_id=items[1], resc_name=items[2], size=items[3], timestamp=items[4], is_paired=is_paired, fname=file_name)
    
    
    @classmethod
    @wrappers.check_args_not_none
    def _process_coll_line(cls, coll_line):
        if coll_line.split()[0] != 'C-':
            raise exceptions.UnexpectedIRODSiCommandOutputException(coll_line)
        return irods_types.CollLine(coll_name=coll_line.split()[1])
    

    @classmethod
    @wrappers.check_args_not_none
    def _process_icmd_output(cls, output):
        ''' This function returns a CollListing object, which contains a list of FileLine and a list of CollLine.
            Parameters
            ----------
            ils -l output, which looks like this:
                "    /Sanger1/home/ic4:\n  ic4               0 wtsiusers                 8265360 2014-03-05.13:24 & egpg5306007.bam.bai\n  ic4               0 wtsiusers                    5371 2013-07-25.11:40 & imp-cluster2.txt\n  ic4               0 wtsiusers                    3696 2014-02-05.11:46 & users.txt\n  C- /Sanger1/home/ic4/test-dir\n "
            Returns
            -------
            list of CollListing 
                consisting of a list of FileLine and a list of strings corresponding to 
            Throws
            ------
            iLSException
                if the collection doesn't exist or the user is not allowed to ils it
            UnexpectedIRODSiCommandOutputException
                if there is something unusual about the ils output.
        '''
        out_lines = output.split('\n')[1:]
        clean_lines = [f.strip() for f in out_lines]
        clean_lines = [_f for _f in clean_lines if _f]

        files_list = [cls._process_file_line(f) for f in clean_lines if f.split()[0] != 'C-']
        colls_list = [cls._process_coll_line(c) for c in clean_lines if c.split()[0] == 'C-']
        
        return irods_types.CollListing(coll_list=colls_list, files_list=files_list)


    @classmethod
    @wrappers.check_args_not_none
    def list_files_in_coll(cls, path):
        ''' 
            This method lists all the files and collections in the collection given as parameter.
            Returns
            -------
            irods_types.CollListinglist 
                A list of irods_types.FileLine and a list of irods_types.CollLine
        '''
        output = cls._run_ils_long(path)
        print("OUTPUT from list_files_in_coll: "+str(output))
        return cls._process_icmd_output(output)
    
    
    @classmethod    
    @wrappers.check_args_not_none
    def list_files_full_path_in_coll(cls, path):
        ''' 
            This function returns a list of files' full path of all
            the files in the collection provided as parameter.
        '''
        file_lines = cls.list_files_in_coll(path).file_lines
        file_names = [f.fname for f in file_lines]
        return [os.path.join(path, fname) for fname in file_names]
    
    
    @classmethod
    @wrappers.check_args_not_none
    def list_all_file_replicas(cls, path):
        ''' 
            Lists all file replicas of the file given by its path.
            Returns
            -------
            list of irods_types.FileLine - each corresponding to a file replica 
            
        '''
        #output = cls._get_ilsl_output(path)
        output = cls._run_ils_long(path)
        files_and_colls = cls._process_icmd_output(output)
        return files_and_colls.files_list
    


################# ICHKSUM ICOMMAND #########################################

class iRODSChecksumOperations(iRODSOperations):
    
    @classmethod
    def _run_ichksum(cls, path, options=[]):
        ''' 
            This function gets the checksum of a file.
            If the checksum doesn't exist in iCAT, it returns None.
            This function can be run by users with READ access over this file.
        '''
        cmd_args = cls._build_icmd_args('ichksum', [path], options)
        try:
            return cls._run_icmd(cmd_args)
        except exceptions.iRODSException as e:
            raise exceptions.iChksumException(error=e.error, output=e.output, cmd=e.cmd)
        

    @classmethod
    def _process_icmd_output(cls, output):
        ''' 
            This function processes the ichcksum result
            by extracting the md5 from it and returning it.
            Params:
                - the output of ichksum command:
                e.g.     file.txt    c780edc691b70a04085713d3e7a73848
                    Total checksum performed = 1, Failed checksum = 0
            Returns:
                - a ChecksumResult
        '''
        tokens = output.split()
        if len(tokens) <= 1:
            raise exceptions.UnexpectedIRODSiCommandOutputException(output)
        md5 = tokens[1]
#        return irods_types.ChecksumResult(md5=md5)
        return md5

 
    @classmethod
    def get_checksum(cls, path):
        ''' 
            Retrieves the md5 from iCAT and returns it. If there is no checksum in iCAT, returns None.
        '''
        output = cls._run_ichksum(path)
        return cls._process_icmd_output(output)
        
    @classmethod
    def run_file_checksum(cls, path):
        ''' 
            This function gets the checksum of a file or calculates it if 
            the md5 doesn't exist in iCAT.
            Throws an error if the user running it doesn't have OWN permission
            over the file he/she wants to ichksum and there is no checksum stored in iCAT,
            because it attempts to write the checksum to iCAT after checksumming the file.
        '''
        output = cls._run_ichksum(path, options=['-K'])
        return cls._process_icmd_output(output)
    
    @classmethod
    def run_file_checksum_across_all_replicas(cls, path):
        ''' This checksums all the replicas by actually calculating the md5 of each replica.
            Hence it takes a very long time to run.
            Runs ichksum -a -K =>   this icommand calculates the md5 of the file in irods 
                                    (across all replicas) and compares it against the stored md5
            Params:
                the path of the file in irods
            Returns: 
                the md5 of the file, if all is ok
            Throws an exception if not.
        '''
        output = cls._run_ichksum(path, ['-a', '-K'])
        return cls._process_icmd_output(output)
    


#################### FILE METADATA FROM IRODS ##############################

class iRODSMetaQueryOperations(iRODSOperations):
    
    @classmethod
    def _run_imeta_qu(cls, avu_dict, zone=constants.IRODS_ZONES.SEQ, operator='='):
        """
            Queries iRODS for all the data objects matching the avus given as parameter.
            WARNING! The default operator for all avus is "=". TO be changed, if not sufficient.
        """
        if not avu_dict:
            return ''
        cmd_args = []
        cmd_args.extend(["imeta", "qu", "-z", zone])
        cmd_args.append("-d")
        for attribute, value in avu_dict.items():
            cmd_args.append(str(attribute))
            cmd_args.append(str(operator))
            cmd_args.append(str(value))
            cmd_args.append('and')
        cmd_args = cmd_args[:len(cmd_args)-1]
        try:
            return cls._run_icmd(cmd_args)
        except exceptions.iRODSException as e:
            raise exceptions.iMetaException(error=e.error, output=e.output, cmd=e.cmd)


    @classmethod
    @wrappers.check_args_not_none
    def _process_icmd_output(cls, output):
        """ This method converts an output like: collection: /seq/123\n, dataObj: 123.bam to
            a list of irods files paths.
            Returns the list of file paths from the output.
        """
        file_paths = []
        lines = output.split('\n')
        if lines[0].find('No rows found') != -1:
            return file_paths
        lines_iter = iter(lines)
        for line in lines_iter:
            if line.startswith('collection'):
                coll = line.split(" ")[1]                   # splitting this: collection: /seq/13240
                fname = next(lines_iter).split(" ")[1]      # splitting this: dataObj: 13173_1#0.bam
                _ = next(lines_iter)    # skipping the --- line
                file_paths.append(os.path.join(coll, fname))
        return file_paths


    @classmethod
    def filter_out_bam_phix_files(cls, file_paths):
        """
            This method is filtering the list of file paths by eliminating the phix data and #0 files.
        """
        return [fpath for fpath in file_paths if fpath.find("#0.bam") == -1 and fpath.find("phix.bam") == -1]

    @classmethod
    def filter_out_cram_phix_files(cls, file_paths):
        """
            This method is filtering the list of file paths by eliminating the phix data and #0 files.
        """
        return [fpath for fpath in file_paths if fpath.find("#0.cram") == -1 and fpath.find("phix.cram") == -1]

    @classmethod
    def filter_out_phix(cls, file_paths):
        """
            This method is filtering the list of file paths by eliminating the phix data and #0 files.
        """
        return [fpath for fpath in file_paths if fpath.find("#0.cram") == -1 and fpath.find("phix.") == -1]


    @classmethod
    def query_by_metadata(cls, avu_dict, zone=constants.IRODS_ZONES.SEQ, operator='='):
        """
            Queries iRODS by metadata and returns a list of full paths of the files
            matching the metadata querying criteria.
            Parameters
            ----------
            avu_dict : dict
                A dict of attribute - values to be queried iRODS on
            zone : str
                The iRODS zone to be queried
            operator : str
                Operator that links the attributes and values. It is = for most of the cases,
                so at the moment there is only 1 operator applied for all the avus. Normally
                each avu should have its own operator, but for our needs "=" on all avus is enough.
            Returns
            -------
            list of str
                List of file paths corresponding to the data objects
                that have as metadata the avus given as parameter
        """
        output = cls._run_imeta_qu(avu_dict, zone, operator)
        output = output.decode("utf-8")
        return cls._process_icmd_output(output)
    

class iRODSMetaListOperations(iRODSOperations):
    
    @classmethod
    def _run_imeta_ls(cls, path, attribute=''):
        cmd_args = ["imeta", "ls", "-d", path, attribute]
        try:
            return cls._run_icmd(cmd_args)
        except exceptions.iRODSException as e:
            raise exceptions.iMetaException(error=e.error, output=e.output, cmd=e.cmd)


    @classmethod
    @wrappers.check_args_not_none
    def _extract_attribute_from_line(cls, line):
        ''' This is a utility method, which extracts the attribute name from a line like:
            attribute: SEQCAP_STUDY NAME
            where attribute name is considered everything that follows: `attribute: `
            Returns the name of the attribute (string).
        '''
        
        if not line.startswith('attribute: '):
            raise ValueError('Wrong input string. The line parameter should start with `attribute` string.')
        index = len('attribute: ')
        return line[index:].strip()

    @classmethod
    @wrappers.check_args_not_none
    def _extract_value_from_line(cls, line):
        ''' This is a utility method, which extracts the value string from a line like: 
            value: testVal
            where the value is considered anything that follows `value: `
            Returns the value as a string.
        '''
        if not line.startswith('value: '):
            raise ValueError('Wrong input string. The line parameter should start with `value: ')
        index = len('value: ')
        return line[index:].strip()
                
    @classmethod
    @wrappers.check_args_not_none
    def _process_icmd_output(cls, output):
        ''' This method takes the output of imeta command and converts it to a MetaAVU.'''
        avus_list = []
        if output.find('No rows found')!= -1:
            return avus_list
        lines = output.split('\n')
        attr_name, attr_val = None, None
        for line in lines:
            if line.startswith('attribute: '):
                attr_name = cls._extract_attribute_from_line(line)
            elif line.startswith('value: '):
                attr_val = cls._extract_value_from_line(line)
                if not attr_val:
                    raise ValueError("Attribute: "+attr_name+" has a None value!")
            
            if attr_name and attr_val:
                avus_list.append(irods_types.MetaAVU(attr_name, attr_val))
                attr_name, attr_val = None, None
        return avus_list


    @classmethod
    def get_metadata(cls, path, attribute=''):
        """
            This function extracts the metadata for a file from irods
            and returns it as a list of tuples (key, value).
        """
        output = cls._run_imeta_ls(path, attribute)
        return cls._process_icmd_output(output)
        
