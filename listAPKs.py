import os
import errno
def getLogdir(filename,dirName):
    log = "F:\\Projects\\Frida\\amdlogs\\"
    logdir = log + filename.replace(dirName,"")
    return logdir
def main():
    dirName = 'F:\\Projects\\Frida\\amd_data\\'
    # Get the list of all files in directory tree at given path
    listOfFiles = list()
    for (dirpath, dirnames, filenames) in os.walk(dirName):
        listOfFiles += [os.path.join(dirpath, file) for file in filenames]
    # # Print the files    
    for elem in listOfFiles:
        # print(elem+","+getLogdir(elem,dirName))
        filename = getLogdir(elem,dirName)
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        with open(filename, "w") as f:
            f.write("FOOBAR")
 
        
        
        
        
if __name__ == '__main__':
    main()