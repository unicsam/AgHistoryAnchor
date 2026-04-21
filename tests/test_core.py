import sys
import os
import unittest

# Add parent directory to path so we can import ag_history
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ag_history.core.protobuf import ProtobufEncoder
from ag_history.core.utils import normalize_uri, uri_to_path

class TestAgHistoryCore(unittest.TestCase):
    def test_varint_encoding(self):
        # Test basic varint
        self.assertEqual(ProtobufEncoder.write_varint(150), b"\x96\x01")
        
    def test_uri_normalization(self):
        # Windows style
        uri = "file:///C%3a/Users/Sam/Project"
        norm = normalize_uri(uri)
        self.assertEqual(norm, "file:///c:/Users/Sam/Project")
        
        # Slashes and casing
        uri2 = "file:///d:/work/code\\"
        norm2 = normalize_uri(uri2)
        self.assertEqual(norm2, "file:///d:/work/code")

    def test_uri_to_path(self):
        if sys.platform == "win32":
            uri = "file:///c:/users/sam/app"
            path = uri_to_path(uri)
            self.assertEqual(path, "c:\\users\\sam\\app")
        else:
            uri = "file:///home/sam/app"
            path = uri_to_path(uri)
            self.assertEqual(path, "/home/sam/app")

    def test_protobuf_strip_field(self):
        # Build a blob with field 1 (title) and field 4 (uid)
        blob = ProtobufEncoder.write_string_field(1, "Old Title") + \
               ProtobufEncoder.write_string_field(4, "uuid-123")
        
        # Strip field 1
        stripped = ProtobufEncoder.strip_field(blob, 1)
        
        # Verify field 1 is gone but field 4 remains
        self.assertNotIn(b"Old Title", stripped)
        self.assertIn(b"uuid-123", stripped)
        
if __name__ == "__main__":
    unittest.main()
