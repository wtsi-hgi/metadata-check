[![Build Status](https://travis-ci.org/wtsi-hgi/metadata-check.svg)](https://travis-ci.org/wtsi-hgi/metadata-check)
[![codecov.io](https://codecov.io/github/wtsi-hgi/metadata-check/coverage.svg?branch=master)](https://codecov.io/github/wtsi-hgi/metadata-check?branch=master)

Metadata-check
==============

The DNA sequencing data that is sequenced within Sanger Institute is released in the form of CRAM or BAM file format and it is deposited in iRODS(http://irods.org/) together with some metadata related to each file (study name, sample id, library id, number of reads, etc). However there is also some metadata within the BAM/CRAM file header itself, which is sometimes out of date, though it should be the same as the iRODS metadata. In addition to this, each sample that arrives at Sanger Institute for sequencing is also registered upon arrival in an internal database called Sequencescape - which is considered the authoritative source of information among the three. The flow of information is: from Sequencescape to iRODS to the file header, which means that most of the inconsistencies are at the level of the file header.

In this context, Metadata-check is a tool for verifying that the metadata associated with a BAM/CRAM file is consistent across all these 3 sources of information. In order to do so, Metadata-check checks a file/list of files by comparing the metadata across the 3 different sources of information mentioned above: iRODS, file header and SequencescapeDB.

Since Metadata-check has as aim to check (only) data in iRODS, the tool has been built around the 3 different modes in which iRODS metadata can be fetched from iRODS:
1. metadata fetched by to tool itself, given one or more file paths as parameter
2. metadata fetched by metacheck, given some metadata to query by iRODS
3. metadata given by the user as a stream of json data.

In the first and second cases ((1) and (2)) fetching the metadata from iRODS for each individual file is done by using baton(https://github.com/wtsi-npg/baton).
In all the cases, the BAM/CRAM file header is obtained by streaming it using samtools (http://samtools.sourceforge.net/) and queries SequencescapeDB are done based on the metadata that has been taken from iRODS. Further, the metadata is compared across these three sources and the output is a list of CheckResults that show which tests have been run on the data and what was the result of each test. Please note that the tool does not correct the metadata, it simply reports the inconsistency.

In addition to the checks mentioned above, Metadata-check does also:
- check that the iRODS metadata of each input file is complete in the sense that it checks if each attribute appears in the file's iRODS metadata at least a given number of times (these numbers are given as parameters within a config file)
- check that the md5 in the iRODS metadata attributes has the same value with the value calculated by iRODS on the server side during the file upload(the result of ichksum)
- check that a lanelet's file name is consistent with the run_id and lane fields in the iRODS metadata
- check that the reference in the metadata attributes is what the user gives as "desired reference" parameter

This is a tool of to be used within Sanger Institute for the sequencing data in iRODS seq zone. The setup involves the presence of iRODS and SequencescapeDB and it expects specific set of metadata attributes some of them specific to the sequencing metadata others specific to the sequencing platform within Sanger Institute.

Prerequisits
============

- python >= 3.5
- baton >= 0.16.3
- samtools >= 1.3 in the path

Installation
============

pip install git+https://github.com/wtsi-hgi/metadata-check.git@<commit_id_or_branch_or_tag>#egg=metadata-check

Usage
=====
It can be either be run as a command line tool, or called from within python code as an API.
For the command line tool, there are 3 subcommands:
```python
    fetch_by_path       Fetch the metadata of one or more files by irods
                        filepath
    given_at_stdin      The metadata is given as baton output via stdin and
                        should be a list of data objects with metadata.
    fetch_by_metadata   Fetch the files that match the metadata attributes
                        given

```
each with its own parameters.

Example of usage for each:
Fetching metadata by file path:
```bash
python mcheck/main/run_checks.py fetch_by_path <file_path>
```

Fetching metadata by metadata attributes:
In this case there is one mandatory parameter - which is --irods_zone, which tells baton in which iRODS zone to search for the data given your search criteria.
Regarding the query criteria itself, there is a small selection of attributes that one can query by, as I have picked the most popular ones:
- study_name
- study_id
- study_acc_nr (study EGA accession number)

And another set of attributes used for filtering your data:
- filter_npq_qc (filter the data by the NPG QC status, which can be either 1 (pass) or 0 (QC fail)
- filter_target (filter the data by the target field, which can be: 0 (this is usually data that is not of interest), 1 - data of interest released as lanelets, library - data of interest released as library-level CRAMs.
- file_type - can be either BAM or CRAM, depending on what type file format you are looking for. Currently the new data is released as CRAM only, so you might want to use this option in order to filter out BAMs for older data dating from the times when the data was being released both as BAMs and CRAMs (same data, 2 different formats).

Example of usage:
```bash
python mcheck/main/run_checks.py fetch_by_metadata --study_name <study_name> --irods_zone seq --filter_target 1 --filter_npg_qc 1
```

Using metadata given by the user at stdin:
Using this option the tool expects a json formatted string which follows the rules of the baton output in terms of attribute names and values.

Example of usage:
```bash
cat cffdna.json | python mcheck/main/run_checks.py given_at_stdin
```

which will print to stdout the results.

By default, the tool will output to stdout the CheckResults as tsv. However, there is also the option of getting the output as json by running it with --output_as_json parameter.
There is also an option for testing that your data is aligned to a specific reference (that you have to give from the command line as --reference).

This program runs on a single machine. However, it can be parallelized by submitting a job on the cluster for each file intended to be checked using the fetch_by_path mode.
Note: if the metadata is fetched_by_metadata, then the metadata itself can be huge, if there is a large number of files within that study, so the tool will need memory proportional with that.

