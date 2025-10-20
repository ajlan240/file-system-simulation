import unittest
from src.common.inode_table import InodeTable

class TestInodeTable(unittest.TestCase):
    def test_inode_allocation_and_free(self):
        table = InodeTable(max_inodes=2)

        # Allocate first inode
        inode1 = table.allocate_inode("file1.txt")
        self.assertTrue(inode1.is_allocated)
        self.assertEqual(inode1.file_name, "file1.txt")

        # Allocate second inode
        inode2 = table.allocate_inode("file2.txt")
        self.assertTrue(inode2.is_allocated)

        # No more free inodes -> should raise exception
        with self.assertRaises(Exception):
            table.allocate_inode("file3.txt")

        # Free first inode
        table.free_inode(inode1.inode_number)
        self.assertFalse(table.get_inode(inode1.inode_number).is_allocated)

if __name__ == "__main__":
    unittest.main()
