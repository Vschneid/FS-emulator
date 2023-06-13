from libDisk import openDisk, writeBlock, readBlock, closeDisk
from libDisk import *
from errors import *

import datetime

BLOCKSIZE = 256
DEFAULT_DISK_SIZE = 10240
DEFAULT_DISK_NAME = "tinyFSDisk"
mounted = 0
fileDescriptor = 0
inode_blocks = 0
SUPERBLOCK = 0
ROOTINODE = 1
initBlock = bytes([0x00] * 256)
diskTable = {}
block = "./block.bin"
open_files = []
inode_pos = 0
buffer = ""

def Inode2Hex(file_name, FD, start, blocks, time):
    if len(file_name) <= 8:
        byteName = bytes(file_name, encoding="utf8")
    else:
        print("something went wrong")
    byteName = byteName + bytes([0x00] * (8 - len(byteName)))
    byteFD = FD.to_bytes(1,byteorder='big')
    byteBlocks = blocks.to_bytes(1,byteorder='big')
    byteStart = start.to_bytes(1,byteorder='big')
    timeStamp = bytes(time, encoding="utf8")
    inodeBytes = byteName + byteFD + byteStart + byteBlocks + timeStamp
    return inodeBytes

def getName(inodeBytes):
    name = inodeBytes[:10].decode()
    returnString = ""
    i = 0
    while i < 8:
        if name[i] != 0x00:
            returnString += name[i]
        i += 1
    return returnString

class OpenFile:
    def __init__(self, pointer, name):
        self.pointer = pointer
        self.name = name

def block_buff():
    global block
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

    openDisk(filename, nBytes)
    superblock = [0x5A, 0x01, 0x02]
    for _ in range(3, 256):
        superblock.append(0x00)

    writeBlock(0, SUPERBLOCK, superblock)
    readBlock(0,0,block)
        
    inode = []

    for _ in range(256):
        inode.append(0x00)

    writeBlock(0, ROOTINODE, inode)

    inode_blocks += 1
    blocks = nBytes // BLOCKSIZE
    for bNum in range(3, blocks):
            writeBlock(0, bNum, initBlock)
    readBlock(0, 3, block)

    readBlock(0, SUPERBLOCK, block)
    data = block_buff()
    if hex(data[0]) == '\x00':
        code = 1
    else:
        code = 0
        
    return code
    

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
        errorno(-6)
    readBlock(0, 0, block)
    data = block_buff()

    # if magic number present (verify format of file)
    if hex(data[0]) == '0x5a':
        mounted = 1
        return
    else:
        errorno(-7)
    
def tfs_unmount():
    global mounted
    if mounted:
        closeDisk(0)
        mounted = 0
    else:
        errorno(-8)


# returns the index of the next free block in the special inode
def findFree(data):
    for i in range(0, 243, 9):
        if data[i:i+1] == b'\x00':
            return i
    errorno(-10)
    

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
    if hex(data[0]) != '0x5a':
        errorno(-9)
    inode_pos = data[2]

    FD = len(open_files)
    file_entry = OpenFile(0, name)
    open_files.append(file_entry)

    readBlock(0, ROOTINODE, block)
    data = block_buff()
    pair_idx = findFree(data)
    
    data = data[:pair_idx] + format_name(name) + inode_pos.to_bytes(1, byteorder='big') + data[pair_idx+11:]

    writeBlock(0, ROOTINODE, data)

    inode_nopad = Inode2Hex(name, FD, 0, 0, datetime.datetime.now().strftime("%a %H:%M"))
    inode_pad = inode_nopad + bytes([0x00]*(256-len(inode_nopad)))

    writeBlock(0, inode_pos, inode_pad)
    readBlock(0, SUPERBLOCK, block)
    data = block_buff()
    data[2] += 1
    writeBlock(0, SUPERBLOCK, bytes(data))
    return FD


def format_name(file_name):
    if len(file_name) <= 8:
        byteName = bytes(file_name, encoding="utf8")
    else:
        errorno(-4)
    byteName = byteName + bytes([0x00] * (8 - len(byteName)))
    return byteName

'''Closes the file and removes dynamic resource table entry'''
def tfs_close(FD):
    global open_files
    if len(open_files):
        open_files[FD] = 0
    else:
        raise Exception("No open files to close")

'''Writes buffer ‘buffer’ of size ‘size’, which represents 
an entire file’s contents, to the file described by ‘FD’. 
Sets the file pointer to 0 (the start of file) when done. 
Returns success/error codes.'''
def tfs_write(FD, buffer, size):
    global open_files, block
    blocks_written = 0

    inode_block = find_inode(open_files[FD].name)
    readBlock(0, inode_block, block)
    data = block_buff()

    #if file already written to
    if data[9]:
        start = data[9]
    #else start pointer at next free block
    else:
        readBlock(0, SUPERBLOCK, block)
        data = block_buff()
        start = data[2]
    
    content_blocks = (size // BLOCKSIZE)
    blocks_written = 0
    
    for buff in range(0, content_blocks):
        writeBlock(0, start + buff, buffer[:(buff)*BLOCKSIZE])
        blocks_written += 1

    if size % BLOCKSIZE:
        writeBlock(0, start + blocks_written, buffer[blocks_written*BLOCKSIZE:])
        blocks_written += 1
    
    superblock = [0x5A, 0x01, start + blocks_written]
    for _ in range(3, 256):
        superblock.append(0x00)

    writeBlock(0, SUPERBLOCK, superblock)
    inode_block = find_inode(open_files[FD].name)
    write_inode(inode_block, start, blocks_written, datetime.datetime.now().strftime("%a %H:%M"))
    return 0

def find_inode(name):
    global block
    readBlock(0, ROOTINODE, block)
    data = block_buff()
    inode = -1
    for i in range(0, 243, 9):
        if data[i:i+8] == format_name(name):
            inode = data[i + 8]
    if inode == -1:
        errorno(-2)
    return inode

def write_inode(inode_block, start, blocks_written, time):
    global block
    readBlock(0, inode_block, block)
    data = block_buff()
    data[9] = start
    data[10] = blocks_written
    data[20:28] = bytes(time, encoding="utf8")
    writeBlock(0, inode_block, bytes(data))

'''Deletes a file and marks its blocks as free on disk.'''
def tfs_delete(FD):
    global open_files, block
    readBlock(0, SUPERBLOCK, block)
    data = block_buff()
    start_free = data[2]

    inode_block = find_inode(open_files[FD].name)
    readBlock(0, inode_block, block)
    data = block_buff()

    start_shift = data[9]
    blocks_2_shift = data[10] 

    blocks_shifted = 0
    for i in range(2):
        if i == 0:
            inode_block = find_inode(open_files[FD].name)
            readBlock(0, inode_block, block)
            data = block_buff()

            start_shift = data[9] 
            blocks_2_shift = data[10]

        if i == 1:
            start_shift = find_inode(open_files[FD].name)
            blocks_2_shift = 1

        readBlock(0, ROOTINODE, block)
        data = block_buff()
        for pair in range(0, 243, 9):
            inode_pos = data[pair+8]
            if inode_pos:
                readBlock(0, data[pair+8], block)
                data = block_buff()
                if data[9] > start_shift:
                    data[9] = data[9] - blocks_2_shift
                    writeBlock(0, inode_pos, bytes(data))
                readBlock(0, ROOTINODE, block)
                data = block_buff()
                inode_pos = data[pair+8]
                if inode_pos > start_shift:
                    data[pair+8] = data[pair+8] - blocks_2_shift
                    writeBlock(0, ROOTINODE, bytes(data))

        for i in range((start_shift + blocks_2_shift), start_free):
            readBlock(0, i, block) 
            data = block_buff()
            writeBlock(0, i - blocks_2_shift, data)

        start_free = start_free - blocks_2_shift
        blocks_shifted += blocks_2_shift

    readBlock(0, ROOTINODE, block)
    data = block_buff()
    for i in range(0, 243, 9):
        if data[i:i+8] == bytes(open_files[FD].name, encoding="utf8"):
            data[i:i+9] = bytearray([0x00]*9)

    writeBlock(0, ROOTINODE, bytes(data))

    superblock = [0x5A, 0x01, start_free]
    for _ in range(3, 256):
        superblock.append(0x00)
    writeBlock(0, SUPERBLOCK, superblock)

    for i in range(start_free, start_free+blocks_shifted):
        writeBlock(0, i, bytes([0x00] * 256))
        
    open_files[FD] = 0

'''Reads one byte from the file and copies it to ‘buffer’, 
using the current file pointer location and incrementing it 
by one upon success. If the file pointer is already at the 
end of the file then tfs_readByte() should return an error 
and not increment the file pointer.'''
def tfs_readByte(FD):
    global buffer, open_files, block
    file = open_files[FD]
    inode_block = find_inode(file.name)
    readBlock(0, inode_block, block)
    data = block_buff()

    data[29:38] = bytes(datetime.datetime.now().strftime("%a %H:%M"), encoding="utf8")
    writeBlock(0, inode_block, bytes(data))

    start = data[9]
    blocks = data[10]
    save = -1
    for blockNum in range(start, start+blocks+1):
        if (file.pointer + start*BLOCKSIZE) < blockNum * BLOCKSIZE:
            save = blockNum - 1
    
    if save == -1:
        errorno(-5)
    
    readBlock(0, save, block)
    data = block_buff()
    a_byte = file.pointer

    buffer = bytes(data[a_byte:a_byte+1])
    open_files[FD].pointer += 1

'''Change the file pointer location to offset (absolute).
Returns success/error codes.'''
def tfs_seek(FD, offset):
    global open_files
    if FD > open_files or open_files[FD] == None:
        errorno(-2)
    open_files[FD].pointer = offset

tfs_mkfs("./newfile.bin", 2560)
tfs_mount("./newfile.bin")

# helper to find fd assosciated with filename
# string -> int
def findFD(filename):
    for i in range(len(open_files)):
        if open_files[i].name == filename:
            return i
    errorno(-2)
    
        
def tfs_stat(FD):
    if FD >= len(open_files):
        errorno(-2)
    name = open_files[FD].name
    index = find_inode(name)
    readBlock(0, index, block)
    data = block_buff()
    
    created  = data[11:20]
    if data[20] == b'\x00':
        modified = " N/A"
    else:
        modified = data[20:29].decode()

    if data[29] == b'\x00':
        accessed = data[29:38].decode()
    else:
        accessed = "never accessed"
    return {"Name" : name, "Created" : created.decode(), "Modified" : modified, "Accessed" : accessed}

# caller passes in new file name a
def tfs_rename(oldName, newName):
    global open_files
    index = find_inode(oldName)
    readBlock(0, index, block)
    data = block_buff()

    # rename in index node
    formatted_name = format_name(newName)
    data[:8] = formatted_name
    writeBlock(0, index, bytes(data))

    # rename in open_files 
    for i in range(len(open_files)):
        if open_files[i].name == oldName:
            open_files[i].name = newName
            break

    # rename root inode
    readBlock(0, ROOTINODE, block)
    data = block_buff()
    for i in range(0, 243, 9):
        if data[i : i + 8] == format_name(oldName):
            data[i : i +8] = formatted_name
    writeBlock(0, ROOTINODE, bytes(data))

    
tfs_open("testing1")
tfs_write(0, bytes("hello", encoding="utf8"), len("hello"))
tfs_open("testing2")
tfs_open("testing3")
tfs_write(2, bytes("motherfucker", encoding="utf8"), len("motherfucker"))

test = tfs_stat(0)

tfs_rename("testing1", "FUCKU")

test = tfs_stat(0)
print(test["Name"])
print("hello")

tfs_stat(1)
tfs_stat(2)
tfs_stat(3)

#readBlock(0, 3, block)
#tfs_readByte(0)
#tfs_readByte(0)
#tfs_readByte(0)
#tfs_readByte(0)

#readBlock(0, 2, block)
#print(block_buff())

#print(block_buff())
tfs_write(1, bytes("there", encoding="utf8"), len("there"))

tfs_delete(0)

for i in range(0,11):
    readBlock(0, i, block)
    data = block_buff()
    print("BLOCK " + str(i) + ":", bytes(data[:32]))
    print("\n")
    #print(data)


#readBlock(0, 3, block)
#print(block_buff())
#readBlock(0, 2, block)
#print(block_buff())
#readBlock(0, SUPERBLOCK, block)
#print(block_buff())
#readBlock(0, ROOTINODE, block)
#print(block_buff())
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
