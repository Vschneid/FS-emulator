

BLOCKSIZE = 256
SIZEERROR = -1
FILENOTFOUNDERROR = -2
READERROR = -3
FILECLOSEDERROR = -4

diskTable = {}
diskNum = 0

'''This function opens a regular UNIX file and designates 
the first nBytes of it as space for the emulated disk. nBytes 
should be a number that is evenly divisible by the block size. 
If nBytes > 0 and there is already a file by the given 
filename, that disk is resized to nBytes, and that file’s 
contents may be overwritten. If nBytes is 0, an existing disk 
is opened, and should not be overwritten. There is no 
requirement to maintain integrity of any content beyond 
nBytes. Errors must be returned for any other failures, as 
defined by your own error code system.'''
def openDisk(filename, nBytes):
    global diskNum
    #print(filename)
    #print(diskNum)
    if nBytes % BLOCKSIZE:
        #print("hello")
        return SIZEERROR
    try:
        if nBytes > 0:
            disk = open(filename, 'r+b')
            disk.truncate(nBytes)
            #print(diskNum)
            diskTable[diskNum] = disk
            diskNum += 1
        else:
            disk = open(filename, 'r+b')
            #print(diskNum)
            diskTable[diskNum] = disk
            diskNum += 1
        return 0
    except:
        #print("hello")
        return FILENOTFOUNDERROR
    pass

'''readBlock() reads an entire block of BLOCKSIZE bytes from 
the open disk (identified by ‘disk’) and copies the result 
into a local buffer (must be at least of BLOCKSIZE bytes). 
The bNum is a logical block number, which must be translated 
into a byte offset within the disk. The translation from 
logical to physical block is straightforward: bNum=0 is the 
very first byte of the file. bNum=1 is BLOCKSIZE bytes into 
the disk, bNum=n is n*BLOCKSIZE bytes into the disk. On 
success, it returns 0. Errors must be returned if ‘disk’ is 
not available (i.e. hasn’t been opened) or for any other 
failures, as defined by your own error code system.'''
def readBlock(disk, bNum, block):
    #print("SEEKSTUFF")
    #print(diskTable[disk].seek(bNum * BLOCKSIZE))
    #diskTable[disk].seek(bNum * BLOCKSIZE)
    #data = diskTable[disk].read(BLOCKSIZE)
    #print(data)
    #print()
    #print(len(data))
    #print(block)
    if disk in diskTable:
        if diskTable[disk].closed:
            return FILECLOSEDERROR
        else:
            diskTable[disk].seek(bNum * BLOCKSIZE)
            data = diskTable[disk].read(BLOCKSIZE)
            if len(data) == BLOCKSIZE:
                #print(block)
                with open(block, "r+b") as block:
                    block.write(data)
                #block[:BLOCKSIZE] = data
                #print(block)
                return 0
            else:
                return READERROR
    else:
        return FILENOTFOUNDERROR
    pass

'''writeBlock() takes disk number ‘disk’ and logical block 
number ‘bNum’ and writes the content of the buffer ‘block’ 
to that location. BLOCKSIZE bytes will be written from 
‘block’ regardless of its actual size. The disk must be 
open. Just as in readBlock(), writeBlock() must translate 
the logical block bNum to the correct byte position in the 
file. On success, it returns 0. Errors must be returned if 
‘disk’ is not available (i.e. hasn’t been opened) or for any 
other failures, as defined by your own error code system.'''
def writeBlock(disk, bNum, block):
    if disk in diskTable:
        if diskTable[disk].closed:
            return FILECLOSEDERROR
        else:
            diskTable[disk].seek(bNum * BLOCKSIZE)
            #print(block[:BLOCKSIZE])
            diskTable[disk].write(bytes(block[:BLOCKSIZE]))
            return 0
    else:
        return FILENOTFOUNDERROR        
    pass

'''closeDisk() takes a disk number ‘disk’ and makes the disk 
closed to further I/O; i.e. any subsequent reads or writes 
to a closed disk should return an error. Closing a disk 
should also close the underlying file, committing any writes 
being buffered by the real OS.'''
def closeDisk(disk):
    if disk in diskTable:
        if diskTable[disk].closed:
            return FILECLOSEDERROR
        else:
            diskTable[disk].close()
    else:
        return FILENOTFOUNDERROR
    
    pass

