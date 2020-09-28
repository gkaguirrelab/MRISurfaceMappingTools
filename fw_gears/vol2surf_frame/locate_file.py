import os

def locate_file(name, path):
    result = []
    for root, dirs, files in os.walk(path):
        for i in files:
            if name in i:
                result.append(os.path.join(root, i))
    return result