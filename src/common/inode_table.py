class Inode:
    def __init__(self, inode_number, file_name="", size=0, block_pointers=None, is_allocated=False):
        self.inode_number = inode_number
        self.file_name = file_name
        self.size = size
        self.block_pointers = block_pointers or []
        self.is_allocated = is_allocated

    def __repr__(self):
        return f"<Inode {self.inode_number}: {self.file_name}, size={self.size}, allocated={self.is_allocated}>"


class InodeTable:
    def __init__(self, max_inodes=16):
        self.max_inodes = max_inodes
        self.inodes = [Inode(i) for i in range(max_inodes)]

    def allocate_inode(self, file_name):
        for inode in self.inodes:
            if not inode.is_allocated:
                inode.is_allocated = True
                inode.file_name = file_name
                inode.size = 0
                inode.block_pointers = []
                return inode
        raise Exception("No free inodes available!")

    def free_inode(self, inode_number):
        if 0 <= inode_number < self.max_inodes:
            inode = self.inodes[inode_number]
            inode.is_allocated = False
            inode.file_name = ""
            inode.size = 0
            inode.block_pointers = []
        else:
            raise IndexError("Invalid inode number!")

    def get_inode(self, inode_number):
        if 0 <= inode_number < self.max_inodes:
            return self.inodes[inode_number]
        else:
            raise IndexError("Invalid inode number!")

