import unittest
from src.fileio.write import write_to_file, read_from_file

class TestWrite(unittest.TestCase):
    def test_write(self):
        with open('testfile.bin', 'wb') as f:
            f.write(b'Hello World')
        write_to_file('testfile.bin', 6, b'Python')
        with open('testfile.bin', 'rb') as f:
            data = f.read()
        self.assertEqual(data, b'Hello Python')
