[![Build Status](https://travis-ci.org/wtsi-hgi/metadata-check.svg)](https://travis-ci.org/wtsi-hgi/metadata-check)
[![codecov.io](https://codecov.io/github/wtsi-hgi/metadata-check/coverage.svg?branch=master)](https://codecov.io/github/wtsi-hgi/metadata-check?branch=master)

Metadata-check
==============

The DNA sequencing data that is sequenced within Sanger Institute is released in the form of CRAM or BAM file format and it is deposited in iRODS(http://irods.org/) together with some metadata related to each file (study name, sample id, library id, number of reads, etc). However there is also some metadata within the BAM/CRAM file header itself, which is sometimes out of date, though it should be the same as the iRODS metadata. In addition to this, each sample that arrives at Sanger Institute for sequencing is also registered upon arrival in an internal database called Sequencescape - which is considered the authoritative source of information among the three. The flow of information is: from Sequencescape to iRODS to the file header, which means that most of the inconsistencies are at the level of the file header.

In this context, Metadata-check is a tool for verifying that the metadata associated with a BAM/CRAM file is consistent across all these 3 sources of information. In order to do so, Metadata-check checks a file/list of files by comparing the metadata across the 3 different sources of information mentioned above: iRODS, file header and SequencescapeDB.

# to be changed -- this part doesn't apply any more!
fetching the metadata from iRODS for each individual file using baton(https://github.com/wtsi-npg/baton), streams the BAM/CRAM file header from the file stored in iRODS using samtools (http://samtools.sourceforge.net/) and queries SequencescapeDB for the attributes found within the iRODS metadata. The metadata is compared across these three sources (or a combination of them if not ran with the default parameters) and the output is a list of inconsistencies found between the 3 sources of metadata. The tool does not correct the metadata, it simply reports the inconsistency.

In addition to the checks mentioned above, Metadata-check can also:
- check that the iRODS metadata of each input file is complete in the sense that it checks if each attribute appears in the file's iRODS metadata at least a given number of times (given as parameter within a config file)
- check that the md5 in the iRODS metadata attributes has the same value with the value calculated by iRODS on the server side during the file upload(the result of ichksum)
- check that a lanelet's file name is consistent with the run_id and lane fields in the iRODS metadata
- check that the reference in the metadata attributes is what the user gives as "desired reference" parameter
- check that the same set of files is retrieved when querying by study id and study name and study accession number
- can output a file's metadata as extracted from different sources (independent of what tests are being run)

This is a tool of to be used within Sanger Institute for the sequencing data in iRODS seq zone. The setup involves the presence of iRODS and SequencescapeDB and a specific set of metadata attributes some of them specific to the sequencing metadata others specific to the sequencing platform within Sanger Institute.

Technical details
=================
Input: 
- a file/list of file paths in iRODS or 
- a study name/study accession number (so that all the files associated with it are being checked)

Output:
- a report containing the problems found with each file
- (optional) a list of metadata attributes gathered from different sources
- (optional) number of files of each type (CRAM/BAM) (useful when analysing files for a whole study).

This program runs on a single machine.
