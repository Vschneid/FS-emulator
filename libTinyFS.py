from libDisk import *

BLOCKSIZE = 256
DEFAULT_DISK_SIZE = 10240
DEFAULT_DISK_NAME = "tinyFSDisk"
fileDescriptor = 0

SUPERBLOCK = 0
INODEBLOCK = 1
#DATABLOCK = 2
#BLOCKFREE = 3

# Define data structures for Superblock, Inode, and Directory Entry
class Superblock:
    def __init__(self):
        self.magic_num = 0x5A
        self.root_inode = None
        # Add free block management mechanism

class Inode:
    def __init__(self):
        self.file_size = 0
        # Add data block indexing mechanism

class DirectoryEntry:
    def __init__(self, name, inode_block):
        self.name = name
        self.inode_block = inode_block

initBlock = bytes([0x00] * 256)

'''Makes an empty TinyFS file system of size nBytes on the 
file specified by ‘filename’. This function should use the 
emulated disk library to open the specified file, and upon
success, format the file to be mountable. This includes 
initializing all data to 0x00, setting magic numbers, 
initializing and writing the superblock and other metadata,
etc. Must return a specified success/error code.'''
def tfs_mkfs(filename, nBytes):
    if openDisk(filename, nBytes):
        
        super = Superblock() #should superblock be a whole block size (rn its just a silly data strucure)
        super.root_inode = INODEBLOCK #check this
        writeBlock(filename, SUPERBLOCK, super)

        inode = Inode() #and this, should inode come after super for whole file system, I thought innode was for files added
        writeBlock(filename, INODEBLOCK, inode)

        blocks = nBytes // BLOCKSIZE
        for bNum in range(2, blocks):
            writeBlock(filename, bNum, initBlock)
        

    pass

'''tfs_mount(char *filename) “mounts” a TinyFS file system
located within ‘filename’. tfs_unmount(void) “unmounts” 
the currently mounted file system. As part of the mount 
operation, tfs_mount should verify the file system is the 
correct type. Only one file system may be mounted at a time.
Use tfs_unmount to cleanly unmount the currently mounted 
file system. Must return a specified success/error code.'''
def tfs_mount(filename):
    pass

def tfs_unmount():
    pass

'''Opens a file for reading and writing on the currently 
mounted file system. Creates a dynamic resource table entry 
for the file (the structure that tracks open files, the 
internal file pointer, etc.), and returns a file descriptor 
(integer) that can be used to reference this file while the 
filesystem is mounted.'''
def tfs_open(name):
    pass

'''Closes the file and removes dynamic resource table entry'''
def tfs_close(FD):
    pass

'''Writes buffer ‘buffer’ of size ‘size’, which represents 
an entire file’s contents, to the file described by ‘FD’. 
Sets the file pointer to 0 (the start of file) when done. 
Returns success/error codes.'''
def tfs_write(FD, buffer, size):
    pass

'''Deletes a file and marks its blocks as free on disk.'''
def tfs_delete(FD):
    pass

'''Reads one byte from the file and copies it to ‘buffer’, 
using the current file pointer location and incrementing it 
by one upon success. If the file pointer is already at the 
end of the file then tfs_readByte() should return an error 
and not increment the file pointer.'''
def tfs_readByte(FD, offset):
    pass

'''Change the file pointer location to offset (absolute).
Returns success/error codes.'''
def tfs_seek(FD, offset):
    pass



