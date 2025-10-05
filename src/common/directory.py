class Directory:
    def __init__(self):
        self.entries = {}

    def add_entry(self, filename, inode_number):
        if filename in self.entries:
            raise Exception("File already exists!")
        self.entries[filename] = inode_number

    def remove_entry(self, filename):
        if filename in self.entries:
            del self.entries[filename]
        else:
            raise Exception("File not found!")

    def list_entries(self):
        return list(self.entries.items())

