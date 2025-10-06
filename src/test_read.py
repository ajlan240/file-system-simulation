import unittest
from src.fileio.read import read_from_file

class TestRead(unittest.TestCase):
    def test_read(self):
        with open('testfile.bin', 'wb') as f:
            f.write(b'Hello World')
        result = read_from_file('testfile.bin', 6, 5)
        self.assertEqual(result, b'World')
