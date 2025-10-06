import unittest
from src.fileio.offset_mapper import logical_to_block_offset

class TestOffsetMapper(unittest.TestCase):
    def test_offset(self):
        self.assertEqual(logical_to_block_offset(1024, 512), 2)
