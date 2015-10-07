Metadata-check
==============

Metadata-check is a tool for checking that the metadata in a BAM/CRAM file is consistent with the metadata in iRODS and with Sequencescape DB. In addition to this it also:
- checks that the metadata of a file in iRODS is complete in the sense that it verifies that the metadata AVUs appear with the frequency mentioned in a config file given as parameter
- checks that the md5 in the iRODS metadata AVU has the same value with the value calculated by iRODS on the server side after the upload(the result of ichksum)
- checks that a lanelet's file name is consistent with the run_id and lane fields in the iRODS metadata
- checks that the reference in the metadata AVU is what the user gives as "desired reference" parameter
- can output a file's metadata as extracted from different sources (independent of what tests are being run)

This is a tool of to be used mainly within Sanger Institute as the setup assumed involves the presence of iRODS and SequencescapeDB and a files hierarchy typical for iRODS sequencing zone (within Sanger Institute).

Technical details
=================
Input: 
- a list of file paths in iRODS or 
- a study name (so that all the files associated with it are being checked)
Output:
- a report containing the problems found with each file
- (optional) a list of metadata attributes gathered from different sources
Metadata check fetches the metadata from iRODS using either the icommands or baton (invoked as subprocesses from within Python), streams the file header from iRODS using samtools and queries SequencescapeDB for the attributes found within the iRODS metadata. It compares the metadata from these three sources (or a combination of them if not ran with the default parameters) and outputs the problems found to the report file. Optionally, it can also output the metadata found to one/more files. In addition to this, it also outputs the file count of each type (useful when analysing files found via querying iRODS by study).

This program runs on a single machine. 
