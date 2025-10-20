import unittest
from src.common.directory import Directory

class TestDirectory(unittest.TestCase):
    def test_add_and_remove_entries(self):
        dir = Directory()
        dir.add_entry("file1.txt", 1)
        dir.add_entry("file2.txt", 2)

        entries = dict(dir.list_entries())
        self.assertEqual(entries["file1.txt"], 1)
        self.assertEqual(entries["file2.txt"], 2)

        # Remove one file
        dir.remove_entry("file1.txt")
        entries = dict(dir.list_entries())
        self.assertNotIn("file1.txt", entries)

    def test_duplicate_file_error(self):
        dir = Directory()
        dir.add_entry("file.txt", 1)
        with self.assertRaises(Exception):
            dir.add_entry("file.txt", 2)

if __name__ == "__main__":
    unittest.main()
