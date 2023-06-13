def errorno(code):
    if code == -1:
        print("System was not mounted")
        exit()
    if code == -2:
        print("File does not exist")
        exit()
    if code == -3:
        print("")
    if code == -4:
        print("Filename is of improper format")
        exit()
    if code == -5:
        print("Reached end of file while parsing")
        exit()
    if code == -6:
        print("Disk has already been mounted to TinyFS")
        exit()
    if code == -7:
        print("Disk has been mounted to a different FS")
        exit()
    if code == -8:
        print("Disk has not been mounted")
        exit()
    if code == -9:
        print("Disk has not been mounted or is mounted under a different format")
        exit()
    if code == -10:
        print("Root inode is full - too many files")
        exit()