import sys
import random
import string
import tempfile
import os
import hashlib

def randomString(stringLength=10):
    """
    Generate a random string of fixed length
    """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


def createWorkingDir():
    """
    Create a working directory in what is flagged as the temp dir by the system
    """
    work_dir_path = os.path.join(tempfile.gettempdir(), "_RAB_" + randomString())
    os.makedirs(work_dir_path)    
    return work_dir_path


def isValidDatasetName(name):
    allowed = set(string.ascii_uppercase + string.ascii_lowercase + string.digits + '!@#$%^&()_-=+[]{},. ')
    return set(name) <= allowed


def hashText(text):
    result = hashlib.md5(str(text).encode())
    return result.hexdigest()


def getNumpyArrayEndianness(arr):
    if arr.dtype.byteorder == "=":
        return sys.byteorder
    elif arr.dtype.byteorder == "<":
        return "little"
    elif arr.dtype.byteorder == ">":
        return "big"
    else:
        return "na"
