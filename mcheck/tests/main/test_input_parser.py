import unittest

from baton.models import DataObject, DataObjectReplica

from mcheck.main.input_parser import convert_data_object
from mcheck.metadata.irods_metadata.file_metadata import IrodsSeqFileMetadata


class TestConvertDataObject(unittest.TestCase):
    """
    Tests for `convert_data_object`.
    """
    def setUp(self):
        self.path = "/path"
        self.data_object = DataObject(self.path)

    def test_convert_if_no_metadata(self):
        converted = convert_data_object(self.data_object)
        self.assertEqual(converted.fpath, self.path)

    def test_convert_when_replica_0(self):
        checksum = "1a2b3"
        self.data_object.replicas.add(DataObjectReplica(0, checksum))
        converted = convert_data_object(self.data_object)
        self.assertEqual(converted.checksum_at_upload, checksum)


if __name__ == "__main__":
    unittest.main()
