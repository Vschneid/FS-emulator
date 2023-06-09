from libDisk import openDisk, writeBlock, readBlock, closeDisk
from libDisk import *
import datetime
import sys

BLOCKSIZE = 256
DEFAULT_DISK_SIZE = 10240
DEFAULT_DISK_NAME = "tinyFSDisk"
mounted = 0
fileDescriptor = 0

inode_blocks = 0

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
        self.file_name = ""
        self.time = ""
        #self.block_index = 0
        # Add data block indexing mechanism

def Inode2Hex(file_name, FD, start, blocks, time):
    # alloting 10 bytes for name of file
    if len(file_name) <= 8:
        byteName = bytes(file_name, encoding="utf8")
    else:
        print("something went wrong")

    byteName = byteName + bytes([0x00] * (8 - len(byteName)))
    byteFD = FD.to_bytes()
    byteBlocks = blocks.to_bytes()
    byteStart = start.to_bytes()
    timeStamp = bytes(time, encoding="utf8")
    inodeBytes = byteName + byteFD + byteStart + byteBlocks + timeStamp
    #print(inodeBytes)
    #print(inodeBytes[10]) #index of fd is 10
    return inodeBytes

def getName(inodeBytes):
    name = inodeBytes[:10].decode()
    returnString = ""
    i = 0
    while i < 8:
        if name[i] != 0x00:
            returnString += name[i]
        i += 1
    #print(returnString)
    return returnString

getName(Inode2Hex("test", 2, 3, 0, datetime.datetime.now().strftime("%a %H:%M")))

class DirectoryEntry:
    def __init__(self, name, inode_block):
        self.name = name
        self.inode_block = inode_block

class OpenFile:
    def __init__(self, pointer, name, start, blocks):
        self.pointer = pointer
        self.name = name
        self.start = start # the block you are currently at
        self.blocks = blocks # numBlocks

initBlock = bytes([0x00] * 256)
diskTable = {}
InodeBlock = [Inode] * 256
block = "./block.bin"
open_files = []
inode_pos = 0

def block_buff():
    global block
    #print(block)
    with open(block, "r+b") as pointer:
        data = pointer.read()
    return bytearray(data)

'''Makes an empty TinyFS file system of size nBytes on the 
file specified by ‘filename’. This function should use the 
emulated disk library to open the specified file, and upon
success, format the file to be mountable. This includes 
initializing all data to 0x00, setting magic numbers, 
initializing and writing the superblock and other metadata,
etc. Must return a specified success/error code.'''

def tfs_mkfs(filename=DEFAULT_DISK_NAME, nBytes=DEFAULT_DISK_SIZE):
    global inode_blocks
    #status, diskNum = openDisk(filename, nBytes)
    openDisk(filename, nBytes)
    #diskTable[diskNum] = filename

    superblock = [0x5A, 0x01, 0x02]
    for _ in range(3, 256):
        superblock.append(0x00)

    writeBlock(0, SUPERBLOCK, superblock)
    readBlock(0,0,block)
    inode = []

    for _ in range(256):
        inode.append(0x00)

    writeBlock(0, INODEBLOCK, inode)
    inode_blocks += 1
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
        #print("this should be mounted")
        mounted = 1
        return
    else:
        raise Exception("Disk mounted to another file system")
    
def tfs_unmount():
    closeDisk(0)
    pass

# returns the index of the next free block in the special inode
def findFree(data):
    #print(data[0:1])
    for i in range(0, 256, 9):
        #print(data[i:i+1])
        if data[i:i+1] == b'\x00':
            return i

'''Opens a file for reading and writing on the currently 
mounted file system. Creates a dynamic resource table entry 
for the file (the structure that tracks open files, the 
internal file pointer, etc.), and returns a file descriptor 
(integer) that can be used to reference this file while the 
filesystem is mounted.'''
def tfs_open(name):
    global open_files, block, inode_pos
    readBlock(0, SUPERBLOCK, block)
    data = block_buff()
    inode_pos = data[2]
    #inode_blocks, inode_curr
    #found = False
    FD = len(open_files)
    file_entry = OpenFile(0, name, None, None)
    open_files.append(file_entry)

    readBlock(0, INODEBLOCK, block)
    data = block_buff()
    pair_idx = findFree(data)
    
    data = data[:pair_idx] + format_name(name) + inode_pos.to_bytes() + data[pair_idx+10:]

    writeBlock(0, INODEBLOCK, data)

    inode_nopad = Inode2Hex(name, FD, 1, 0, datetime.datetime.now().strftime("%a %H:%M"))
    inode_pad = inode_nopad + bytes([0x00]*(256-len(inode_nopad)))

    writeBlock(0, inode_pos, inode_pad)
    readBlock(0, SUPERBLOCK, block)
    data = block_buff()
    data[2] += 1
    writeBlock(0, SUPERBLOCK, bytes(data))
    #readBlock(0, SUPERBLOCK, block)
    #data = block_buff()
    #print("new_data : ", data)
    return FD


def format_name(file_name):
    if len(file_name) <= 8:
        byteName = bytes(file_name, encoding="utf8")
    else:
        print("something went wrong")

    byteName = byteName + bytes([0x00] * (8 - len(byteName)))
    return byteName

    #will have to make the inode and do timestamp here
    '''
    for inodeB in range(1, inode_blocks+1):
        readBlock(0, inodeB, block)
        data = block_buff()
        #print(data)
        for inode in range(0, len(data), 32):
            if name == getName(inode):
                found = inode
            break #do we have to reset its FD
        
    if found:
        pass
    else:
        Inode2Hex(name, FD, 0, 0)
        writeBlock(0, inode_blocks)

    data.decode()
    '''
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
    global open_files, block
    #print(block)
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
    inode_block = find_inode(open_files[FD].name)
    write_inode(inode_block, start, blocks_written)
    #open_files[FD].start = start
    #open_files[FD].blocks = blocks_written
    open_files[FD].pointer = 0
    return 0

    pass

def find_inode(name):
    global block
    readBlock(0, INODEBLOCK, block)
    data = block_buff()
    for i in range(0, len(data)-9):
        if data[i:i+8] == name:
            inode = i + 9
    return inode

def write_inode(inode_block, start, blocks_written):
    global block
    readBlock(0, inode_block, block)
    data = block_buff()
    data[8:9] = start
    data[9:10] = blocks_written
    writeBlock(0, inode_block,bytes(data))
 
def read_inode(inode_block):
    global block
    readBlock(0, inode_block, block)
    data = block_buff()
    #more probably
    for inodeB in range(1, inode_blocks+1):
        readBlock(0, inodeB, block)
        data = block_buff()
        #print(data)
        for inode in range(0, len(data), 32):
            if name == getName(inode):
                found = inode

'''Deletes a file and marks its blocks as free on disk.'''
def tfs_delete(FD):
    global open_files, block
    readBlock(0, SUPERBLOCK, block)
    data = block_buff()
    start_free = data[2]
    start_shift = open_files[FD].start 
    blocks_2_shift = open_files[FD].blocks
    for i in range((start_shift + blocks_2_shift), start_free):
        readBlock(0, i, block)
        data = block_buff()
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
    global buffer, open_files, block
    file = open_files[FD]
    save = -1
    for blockNum in range(file.start, file.start+file.blocks+1):
        print(file.start)
        print(file.blocks+file.start)
        print(file.pointer + file.start*BLOCKSIZE)
        print(blockNum * BLOCKSIZE)
        if (file.pointer + file.start*BLOCKSIZE) < blockNum * BLOCKSIZE:
            print("block to be saved: " + str(block))
            save = blockNum - 1
    
    if save == -1:
        raise Exception("End of file")
    
    readBlock(0, save, block)
    data = block_buff()
    a_byte = file.pointer
    buffer = data[a_byte:a_byte+1]
    print(data[a_byte:a_byte+1])
    open_files[FD].pointer += 1

'''Change the file pointer location to offset (absolute).
Returns success/error codes.'''
def tfs_seek(FD, offset):
    global open_files
    open_files[FD].pointer = offset

tfs_mkfs("./newfile.bin", 2560)
tfs_mount("./newfile.bin")

# helper to find fd assosciated with filename
# string -> int
def findFD(filename):
    for i in range(len(open_files)):
        if open_files[i].name == filename:
            return i

tfs_open("testfile")

'''
print(findFD("testfile"))
tfs_write(findFD("testfile"), [0xFE], len([0xFE]))
print(open_files[findFD("testfile")].pointer)
tfs_readByte(findFD("testfile"), 1)

#print(DirectoryEntry("testing", ))
print(bytes("filenamey", encoding="utf8").decode())
print(datetime.datetime.now().strftime("%a %H:%M"))
print(datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S"))
#DirectoryEntry = 
'''
