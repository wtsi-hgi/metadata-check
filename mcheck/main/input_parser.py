import json
from typing import List

from baton._baton.json import DataObjectJSONDecoder
from baton.models import DataObject

from mcheck.metadata.irods_metadata.file_metadata import IrodsSeqFileMetadata

IRODS_METADATA_LEGACY_LIBRARY_ID_PROPERTY = "library"
IRODS_METADATA_LIBRARY_ID_PROPERTY = "library_id"
IRODS_METADATA_REFERENCE_PROPERTY = "reference"
IRODS_METADATA_TARGET_PROPERTY = "target"
IRODS_ORIGINAL_REPLICA_NUMBER = 0


def convert_json_to_baton_objs(data_objects_as_json_string: str) -> List[IrodsSeqFileMetadata]:
    decoded = json.loads(data_objects_as_json_string, cls=DataObjectJSONDecoder)
    if isinstance(decoded, DataObject):
        decoded = [decoded]
    return decoded

def parse_data_objects(data_objects_as_json_string: str) -> List[IrodsSeqFileMetadata]:
    """
    Parses the given data object(s) in the JSON serialised form, defined by baton, into representations that are used
    internally.
    :param data_objects_as_json_string: the data object(s) as a JSON string
    :return: the internal representation of the data objects
    """
    decoded = json.loads(data_objects_as_json_string, cls=DataObjectJSONDecoder)
    if isinstance(decoded, DataObject):
        decoded = [decoded]
    return [convert_data_object(data_object) for data_object in decoded]


def convert_data_object(data_object: DataObject) -> IrodsSeqFileMetadata:
    """
    Parses the given data object from iRODS into the representation used internally.
    :param data_object: data object from iRODS, retrieved via baton wrapper
    :return: internal representation of iRODS metadata
    """
    path = data_object.path

    if data_object.replicas is not None:
        # Assuming that replica number `IRODS_REPLICA_FIRST_NUMBER` is the first replica that is created
        original_replica = data_object.replicas.get_by_number(IRODS_ORIGINAL_REPLICA_NUMBER)
        checksum_at_upload = original_replica.checksum if original_replica is not None else None
    else:
        checksum_at_upload = None

    metadata = data_object.metadata
    if metadata is None:
        return IrodsSeqFileMetadata(path, checksum_at_upload=checksum_at_upload)

    references = metadata.get(IRODS_METADATA_REFERENCE_PROPERTY)
    target = list(metadata.get(IRODS_METADATA_TARGET_PROPERTY, default={None}))[0]
    # TODO: Add other conversions

    if IRODS_METADATA_LIBRARY_ID_PROPERTY in metadata:
        libraries = metadata[IRODS_METADATA_LIBRARY_ID_PROPERTY]
    elif IRODS_METADATA_LEGACY_LIBRARY_ID_PROPERTY in metadata:
        libraries = metadata[IRODS_METADATA_LEGACY_LIBRARY_ID_PROPERTY]
    else:
        libraries = None

    return IrodsSeqFileMetadata(path, references=references, libraries=libraries, checksum_at_upload=checksum_at_upload,
                                target=target)
