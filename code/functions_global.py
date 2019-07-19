#!/usr/bin/python
# Filename: functions_global.py
import os, logging, sys


def chk_is_empty(variable):
    try:
        value = float(variable)
    except ValueError:
        value = variable
        pass
    try:
        value = str(variable)
    except ValueError:
        pass
    return bool(value)

def chk_dir(directory):
    if not(os.path.exists(directory)):
            os.makedirs(directory)

def chk_folder_structure(foldername):
    ScriptDir = os.path.dirname(os.path.abspath(__file__))  # get base working directory of script
    if not (os.path.exists(ScriptDir+'\\'+foldername)):
            os.mkdir(ScriptDir+'\\'+foldername)


def clean_dir(directory):
    # Delete everything reachable IN the directory named in 'directory',
    # assuming there are no symbolic links.
    # CAUTION:  This is dangerous!  For example, if directory == '/', it
    # could delete all your disk files.
    for root, dirs, files in os.walk(directory, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))

def initialize_logger(output_dir, app_name, feature_list):
    ## BETTER: launch the logger directly in the main funtion for handling (closing) logfile after processing
    logger = logging.getLogger(app_name)
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to info
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # create error file handler and set level to error
    err_handler = logging.FileHandler(os.path.join(output_dir, "error.log"), "w", encoding=None, delay="true")
    err_handler.setLevel(logging.ERROR)
    err_formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
    err_handler.setFormatter(err_formatter)
    logger.addHandler(err_handler)

    # create debug file handler and set level to debug
    debug_handler = logging.FileHandler(os.path.join(output_dir, "logfile.log"), "w")
    debug_handler.setLevel(logging.DEBUG)
    debug_formatter = logging.Formatter("%(asctime)s - %(message)s")
    debug_handler.setFormatter(debug_formatter)
    logger.addHandler(debug_handler)

    logger.info("Raster_creator.map_maker initiated with feature list = " + str(feature_list))

def open_folder(directory):
    try:
        import subprocess
        ## other python versions than 2.7: import subprocess32
        my_platform = sys.platform
        if my_platform[0:3].lower() == "win":
            ## print("Hello Windows!")
            call_target = "explorer " + directory
            subprocess.call(call_target, shell=True)
            print("Found subprocess --> opening target folder.")
        if my_platform[0:3].lower() == "lin":
            ## print("Hello Linux!")
            subprocess.check_call(['xdg-open', '--', directory])
            print("Found subprocess --> opening target folder.")
        if my_platform[0:3].lower() == "dar":
            ## print("Hello Mac OS!")
            subprocess.check_call(['open', '--', directory])
            print("Found subprocess --> opening target folder.")
            try:
                os.system("start \"\" https://en.wikipedia.org/wiki/Criticism_of_Apple_Inc.")
            except:
                pass


        # Alternative:
        # subprocess.Popen(r'explorer /select,"C:\path\of\folder\file"')
    except:
        pass


def rm_dir(directory):
    # Delete everything reachable from the directory named in 'directory', and the directory itself
    # assuming there are no symbolic links.
    # CAUTION:  This is dangerous!  For example, if directory == '/', it
    # could delete all your disk files.
    for root, dirs, files in os.walk(directory, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(directory)

def rm_file(directory):
    # Delete everything reachable from the directory named in 'directory', and the directory itself
    # assuming there are no symbolic links.
    # CAUTION:  This is dangerous!  For example, if directory == '/', it
    # could delete all your disk files.
    for root, dirs, files in os.walk(directory, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(directory)

def str2frac(arg):
    arg = arg.split('/')
    return(int(arg[0])/int(arg[1]))

def str2num(arg,SEP):
    # function converts string of type 'X[SEP]Y' to number
    # SEP is either ',' or '.'
    # e.g. '2,30' is converted with SEP = ',' to 2.3
    _num = arg.split(SEP)
    _a = int(_num[0])
    _b = int(_num[1])
    _num = _a+_b*10**(-1*len(str(_b)))
    return(_num)

def str2tuple(arg):
    try:
        arg = arg.split(',')
    except ValueError:
        print('Bad assignment of separator.\nSeparator must be [,].')
    tup = (int(arg[0]),int(arg[1]))
    return(tup)

def tuple2num(arg):
    # function converts float number with ',' separator for digits to '.' separator
    # type(arg) = tuple with two entries, e.g. (2,40)
    # call: tuple2num((2,3))
    new =  arg[0]+arg[1]*10**(-1*len(str(arg[1])))
    return(new)

def write_data(folderDir,fileName,data):
    ScriptDir = os.path.dirname(os.path.abspath(__file__))
    if not (os.path.exists(folderDir)):
            os.mkdir(folderDir)
    os.chdir(folderDir)

    f = open(fileName+'.txt','w')
    for i in data:
         line = str(i)+'\n'
         f.write(line)
    #data=np.array(data)
    #np.savetxt(fileName, data)
    os.chdir(ScriptDir)
    print('Data written to: \n'+folderDir+'\\'+str(fileName)+'.csv')

