import json
import unittest

from baton._baton.json import DataObjectJSONEncoder, DataObjectJSONDecoder
from baton.collections import IrodsMetadata
from baton.models import DataObject, DataObjectReplica
from mcheck.main.input_parser import convert_data_object, IRODS_METADATA_LIBRARY_ID_PROPERTY, \
    IRODS_METADATA_LEGACY_LIBRARY_ID_PROPERTY, IRODS_METADATA_TARGET_PROPERTY, IRODS_METADATA_REFERENCE_PROPERTY, \
    parse_data_objects


class ParseDataObjects(unittest.TestCase):
    """
    Tests for `parse_data_objects`.
    """
    _DATA_OBJECT_JSON_ENCODER = DataObjectJSONEncoder()
    _DATA_OBJECT_JSON_DECODER = DataObjectJSONDecoder()

    def setUp(self):
        self.data_objects = [
            DataObject("/path_1"),
            DataObject("/path_2"),
            DataObject("/path_3")
        ]

    def test_parse_single_data_object(self):
        data_object_as_json_string = json.dumps(self.data_objects[0], cls=DataObjectJSONEncoder)
        assert isinstance(data_object_as_json_string, str)
        assert data_object_as_json_string.startswith("{")
        internal_representations = parse_data_objects(data_object_as_json_string)
        self.assertEqual(len(internal_representations), 1)
        self.assertEqual(internal_representations[0].fpath, self.data_objects[0].path)

    def test_parse_data_objects(self):
        data_objects_as_json_string = json.dumps(self.data_objects, cls=DataObjectJSONEncoder)
        assert isinstance(data_objects_as_json_string, str)
        assert data_objects_as_json_string.startswith("[")
        internal_representations = parse_data_objects(data_objects_as_json_string)
        self.assertEqual(len(internal_representations), len(self.data_objects))
        for i in range(len(internal_representations)):
            self.assertEqual(internal_representations[i].fpath, self.data_objects[i].path)


class TestConvertDataObject(unittest.TestCase):
    """
    Tests for `convert_data_object`.
    """
    def setUp(self):
        self.path = "/path"
        self.data_object = DataObject(self.path, metadata=IrodsMetadata(), replicas={})

    def test_convert_if_no_metadata(self):
        converted = convert_data_object(DataObject(self.path))
        self.assertEqual(converted.fpath, self.path)

    def test_convert_when_checksum_at_upload(self):
        checksum = "1a2b3"
        self.data_object.replicas.add(DataObjectReplica(0, checksum))
        converted = convert_data_object(self.data_object)
        self.assertEqual(converted.checksum_at_upload, checksum)

    def test_convert_when_references(self):
        references = {"/reference_1", "/reference_2"}
        self.data_object.metadata[IRODS_METADATA_REFERENCE_PROPERTY] = references
        converted = convert_data_object(self.data_object)
        # Internal access to references only
        self.assertCountEqual(converted._reference_paths, references)

    def test_convert_when_target(self):
        target = "target"
        self.data_object.metadata[IRODS_METADATA_TARGET_PROPERTY] = {target}
        converted = convert_data_object(self.data_object)
        # Internal access to targets only
        self.assertCountEqual(converted._target_values, [target])

    def test_convert_when_libraries_set_through_legacy_property(self):
        libraries = {"library_1", "library_2"}
        self.data_object.metadata[IRODS_METADATA_LEGACY_LIBRARY_ID_PROPERTY] = libraries
        converted = convert_data_object(self.data_object)
        self.assertCountEqual(converted.libraries, libraries)

    def test_convert_when_libraries_set_through_library_id_property(self):
        libraries = {"library_1", "library_2"}
        self.data_object.metadata[IRODS_METADATA_LIBRARY_ID_PROPERTY] = libraries
        converted = convert_data_object(self.data_object)
        self.assertCountEqual(converted.libraries, libraries)


if __name__ == "__main__":
    unittest.main()
