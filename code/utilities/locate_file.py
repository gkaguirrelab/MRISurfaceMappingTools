import os

'''
This function finds a file or multiple files in the path specified. File(s) can
be located in nested directories. If you need to find files with common
prefixes, enter the common part as the name input. Outputs a python list.
'''

def locate_file(name, path):
    result = []
    for root, dirs, files in os.walk(path):
        for i in files:
            if name in i:
                result.append(os.path.join(root, i))
    return result