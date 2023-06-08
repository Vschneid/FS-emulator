from libDisk import openDisk, writeBlock, readBlock, closeDisk
from libDisk import *
import sys

BLOCKSIZE = 256
DEFAULT_DISK_SIZE = 10240
DEFAULT_DISK_NAME = "tinyFSDisk"
mounted = 0
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

class OpenFile:
    def __init__(self, pointer, name, start, blocks):
        self.pointer = pointer
        self.name = name
        self.start = start
        self.blocks = blocks

initBlock = bytes([0x00] * 256)
diskTable = {}
InodeBlock = [Inode] * 256
block = "block.bin"
open_files = []

def block_buff():
    global block
    with open(block, "r+b") as block:
        data = block.read()
    return data

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
    global block, mounted
    if mounted: 
        raise Exception("Currently have a disk mounted")
    readBlock(0, 0, block)
    data = block_buff()
    #print(hex(data[0]))
    # if magic number present (verify format of file)
    if hex(data[0]) == '0x5a':
        print("this should be mounted")
        mounted = 1
        return
    else:
        raise Exception("Disk mounted to another file system")
    
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
    global open_files
    FD = len(open_files)
    file_entry = OpenFile(0, name, None, None)
    open_files.append(file_entry)
    return FD
    pass

'''Closes the file and removes dynamic resource table entry'''
def tfs_close(FD):
    global open_files
    if len(open_files):
        open_files[FD] = 0
    else:
        raise Exception("No open files to close")
    #pass

'''Writes buffer ‘buffer’ of size ‘size’, which represents 
an entire file’s contents, to the file described by ‘FD’. 
Sets the file pointer to 0 (the start of file) when done. 
Returns success/error codes.'''
def tfs_write(FD, buffer, size):
    global open_files
    readBlock(0, SUPERBLOCK, block)
    data = block_buff()
    start = data[2]
    blocks_written = 0
    content_blocks = size // BLOCKSIZE
    for buff in range(0, content_blocks):
        writeBlock(0, start + buff, buffer[:buff*BLOCKSIZE])
        blocks_written += 1
    if size % BLOCKSIZE:
        writeBlock(0, start + blocks_written, buffer[blocks_written*BLOCKSIZE:])
        blocks_written += 1
    
    superblock = [0x5A, 0x01, start + blocks_written]
    for _ in range(3, 256):
        superblock.append(0x00)

    writeBlock(0, SUPERBLOCK, superblock)

    open_files[FD].start = start
    open_files[FD].blocks = blocks_written
    open_files[FD].pointer = 0
    return 0

    pass

'''Deletes a file and marks its blocks as free on disk.'''
def tfs_delete(FD):
    global open_files
    readBlock(0, SUPERBLOCK, block)
    data = block_buff()
    start_free = data[2]
    start_shift = open_files[FD].start 
    blocks_2_shift = open_files[FD].blocks
    for i in range((start_shift + blocks_2_shift), start_free):
        readBlock(0, i, block)
        data = block()
        writeBlock(0, i - blocks_2_shift, data)

    for file in open_files:
        if file.start > start_shift:
            file.start = file.start - blocks_2_shift

    superblock = [0x5A, 0x01, start_free - blocks_2_shift]
    for _ in range(3, 256):
        superblock.append(0x00)
    writeBlock(0, SUPERBLOCK, superblock)

    open_files[FD] = 0

    pass

'''Reads one byte from the file and copies it to ‘buffer’, 
using the current file pointer location and incrementing it 
by one upon success. If the file pointer is already at the 
end of the file then tfs_readByte() should return an error 
and not increment the file pointer.'''
def tfs_readByte(FD, offset):
    global buffer, open_files
    file = open_files[FD]
    save = -1
    for block in range(file.start, file.start+file.blocks):
        if file.pointer < block * BLOCKSIZE:
            save = block
    
    if save == -1:
        raise Exception("End of file")
    
    readBlock(0, save, block)
    data = block_buff()
    a_byte = file.pointer
    buffer = data[a_byte:a_byte+1]
    open_files[FD].pointer += 1

    return "SHIMMY SHIMMY YA"
    pass

'''Change the file pointer location to offset (absolute).
Returns success/error codes.'''
def tfs_seek(FD, offset):
    global open_files
    open_files[FD].pointer = offset
    pass

tfs_mkfs("./newfile.bin", 2560)
tfs_mount("./newfile.bin")

