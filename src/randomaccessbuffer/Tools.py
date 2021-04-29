"""
    The Tool module is composed of system functions that should only be used by
    the main RandomAccessBuffer module and not externaly. Please ginore this module.
"""

import sys
import random
import string
import tempfile
import os
import hashlib
import json
import numpy as np


def randomString(stringLength=10):
    """
    Generate a random string of fixed length containing only ascii lowercase characters.

    Args:
        stringLength (int): the length of the random string to generate
    """
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(stringLength))


def createWorkingDir():
    """
    Create a working directory in what is flagged as the temp dir by the system.
    """
    work_dir_path = os.path.join(tempfile.gettempdir(), "_RAB_" + randomString())
    os.makedirs(work_dir_path)
    return work_dir_path


def isValidDatasetName(name):
    """
    Checks if the given dataset name is valid.
    A valid dataset name contains only ASCII lowercase, ASCII uppercase !@#$%^&()_-=+[]{},. and whitespaces.

    Args:
        name (string): the dataset name to be checked

    Returns:
        bool: True for a valid name, False for invalid
    """
    allowed = set(
        string.ascii_uppercase
        + string.ascii_lowercase
        + string.digits
        + "!@#$%^&()_-=+[]{},. "
    )
    return set(name) <= allowed


def hashText(text):
    """
    Hashes a text with md5.

    Args:
        text (string): a string to hash.

    Returns:
        string
    """
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


class CustomJsonEncoder(json.JSONEncoder):
    """
    This JSON encoder replaces the Numpy arrays by Python lists.
    It is used only in the context of encoding metadata, not data.
    """

    def default(self, obj):
        """
        Overload of the default interface to swap every np.ndarray with their list counterpart.
        """
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


# A safe object is an object that would serialize into safe yaml or safe json,
# and deserialize properly in Python or Javascript.
# This means turning numpy arrays into list, or simply crashing when safe is
# not achievable.
def make_safe_object(obj):
    json_serialized = json.dumps(obj, ensure_ascii=False, cls=CustomJsonEncoder)
    safe_dict = json.loads(json_serialized)
    return safe_dict


def get_smallest_integer_dtype(arr):
    # All the dtypes we want to check, order matters
    integer_dtypes = [
        np.uint8,
        np.int8,
        np.uint16,
        np.int16,
        np.uint32,
        np.int32,
        np.uint64,
        np.int64,
    ]

    for dtype in integer_dtypes:
        info = np.iinfo(dtype)
        if np.amin(arr) >= info.min and np.amax(arr) <= info.max:
            return dtype

    # Worst case scenario, just stay as it already is
    return arr.dtype
