from libDisk import openDisk, writeBlock, readBlock, closeDisk
from libDisk import *
import sys

BLOCKSIZE = 256
DEFAULT_DISK_SIZE = 10240
DEFAULT_DISK_NAME = "tinyFSDisk"
Mounted = 0
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
        #self.file_name = ""
        #self.block_index = 0
        # Add data block indexing mechanism

class DirectoryEntry:
    def __init__(self, name, inode_block):
        self.name = name
        self.inode_block = inode_block

initBlock = bytes([0x00] * 256)
diskTable = {}
InodeBlock = [Inode] * 256
block = "block.bin"

'''Makes an empty TinyFS file system of size nBytes on the 
file specified by ‘filename’. This function should use the 
emulated disk library to open the specified file, and upon
success, format the file to be mountable. This includes 
initializing all data to 0x00, setting magic numbers, 
initializing and writing the superblock and other metadata,
etc. Must return a specified success/error code.'''
def tfs_mkfs(filename=DEFAULT_DISK_NAME, nBytes=DEFAULT_DISK_SIZE):
    #status, diskNum = openDisk(filename, nBytes)
    openDisk(filename, nBytes)
    #diskTable[diskNum] = filename

    superblock = [0x5A, 0x01, 0x02]
    for _ in range(3, 256):
        superblock.append(0x00)
    #print(superblock)
    #print()
    #print(bytes(superblock).hex())

    writeBlock(0, SUPERBLOCK, superblock)
    readBlock(0,0,block)

    inode = []

    for _ in range(256):
        inode.append(0x00)
    
    writeBlock(0, INODEBLOCK, inode)

    blocks = nBytes // BLOCKSIZE
    for bNum in range(3, blocks):
        writeBlock(0, bNum, initBlock)
    #block = [0 * 2560]
    readBlock(0, 3, block)
    #closeDisk(filename)

    
'''
        super = Superblock() #should superblock be a whole block size (rn its just a silly data strucure)
        super.root_inode = INODEBLOCK #check this
        writeBlock(filename, SUPERBLOCK, super)

        inode = Inode() #and this, should inode come after super for whole file system, I thought innode was for files added
        writeBlock(filename, INODEBLOCK, inode)

        blocks = nBytes // BLOCKSIZE
        for bNum in range(2, blocks):
            writeBlock(filename, bNum, initBlock)'''

'''tfs_mount(char *filename) “mounts” a TinyFS file system
located within ‘filename’. tfs_unmount(void) “unmounts” 
the currently mounted file system. As part of the mount 
operation, tfs_mount should verify the file system is the 
correct type. Only one file system may be mounted at a time.
Use tfs_unmount to cleanly unmount the currently mounted 
file system. Must return a specified success/error code.'''
def tfs_mount(filename=DEFAULT_DISK_NAME):
    global block, Mounted
    if Mounted: 
        raise Exception("Currently have a disk mounted")
    
    readBlock(0, 0, block)
    with open(block, "r+b") as block:
        data = block.read()
    #print(hex(data[0]))
    # if magic number present (verify format of file)
    if hex(data[0]) == '0x5a':
        print("this should be mounted")
        return
    
def tfs_unmount():
    closeDisk(0)
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

tfs_mkfs("./newfile.bin", 2560)
tfs_mount("./newfile.bin")

