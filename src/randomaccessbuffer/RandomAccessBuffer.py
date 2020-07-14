"""

    TODO:
    - zlib provides a way to stream compress/decompress for buffer that don't fit in memory
"""

import os
import zlib
import shutil
import json
import yaml
import numpy as np
import copy
import struct
from randomaccessbuffer import Tools
from randomaccessbuffer.Dotdict import Dotdict
from randomaccessbuffer.__version__ import __version__

MAGIC_NUMBER = "rab"

TYPES = Dotdict({
    "BUFFER": "bytes",
    "OBJECT": "object",
    "TEXT": "text",
    "NUMERICALS": [
        "bool",
        "int8",
        "uint8",
        "int16",
        "uint16",
        "int32",
        "uint32",
        "int64",
        "uint64",
        "float16",
        "float32",
        "float64",
        "complex64",
        "complex128"
    ]
})



# BUFFER_TYPE = "bytes"
# OBJECT_TYPE = "object"
# TEXT_TYPE = "text"
#
# NUMERICAL_TYPES = [
#     "bool",
#     "int8",
#     "uint8",
#     "int16",
#     "uint16",
#     "int32",
#     "uint32",
#     "int64",
#     "uint64",
#     "float16",
#     "float32",
#     "float64",
#     "complex64",
#     "complex128"
# ]

SHORT_NUMERICAL_TYPES = {
    "bool": "b",
    "int8": "i1",
    "uint8": "u1",
    "int16": "i2",
    "uint16": "u2",
    "int32": "i4",
    "uint32" : "u4",
    "int64": "i8",
    "uint64": "u8",
    "float16": "f2",
    "float32": "f4",
    "float64": "f8",
    "complex64": "c8",
    "complex128": "c16"
}

UNPACK_TYPES = {
    "bool": "?",
    "int8": "b",
    "uint8": "B",
    "int16": "h",
    "uint16": "H",
    "int32": "i",
    "uint32" : "I",
    "int64": "q",
    "uint64": "Q",
    "float16": "XXXXXXX", # not existing
    "float32": "f",
    "float64": "d",
    "complex64": "XXXXXXX", # should be dealt with 2 float32 (TODO)
    "complex128": "XXXXXXX" # should be dealt with 2 double (TODO)
}

SHORT_ENDIANNESS = {
    "little": "<",
    "big": ">",
    "na": "<" # this is used for int8 and uint8
}

class RandomAccessBuffer:
    def __init__(self):
        # print("version", __version__)
        self._working_dir = Tools.createWorkingDir()
        # print("working dir", self._working_dir)
        self._rab_index = []
        self._data_byte_offset = None
        self._filepath = None # for reading
        self._onDone = None


    def onDone(self, fn):
        self._onDone = fn


    def __del__(self):
        """
        When the destructor is called, we delete the working dir and its content
        """
        self.clean()

        if self._onDone:
            self._onDone()


    def listDatasets(self):
        names = []
        for entry in self._rab_index:
            names.append(entry["name"])
        return names


    def _getDatasetAsByte(self, codec_meta):
        """
        Extract a dataset buffer (bytes) in an agnostic way, returns it.
        """
        byte_offset = self._data_byte_offset + codec_meta["byteOffset"]
        f = open(self._filepath, "rb")
        f.seek(byte_offset)
        buffer = f.read(codec_meta["byteLength"])
        f.close()

        # decompress the buffer if necessary
        if "compression" in codec_meta and codec_meta["compression"] == "gzip":
            buffer = zlib.decompress(buffer)
        return buffer


    def _getNumericalDataset(self, codec_meta):
        buffer = self._getDatasetAsByte(codec_meta)
        # The short type can be prepended with a < or > to add endianness info
        short_type = SHORT_ENDIANNESS[codec_meta["endianness"]] + SHORT_NUMERICAL_TYPES[codec_meta["type"]]
        arr = np.frombuffer(buffer, dtype=short_type)
        arr.shape = codec_meta["shape"]
        return arr


    def _getText(self, codec_meta):
        buffer = self._getDatasetAsByte(codec_meta)
        text = buffer.decode("utf-8", "strict")
        return text


    def _getObject(self, codec_meta):
        buffer = self._getDatasetAsByte(codec_meta)
        object_str = buffer.decode("utf-8", "strict")

        # Try load it with YAML then if fails, try with json
        # Note: YAML 1.2 is a superset of JSON except it does not like tabs
        object = None
        try:
            object = yaml.load(object_str, Loader=yaml.Loader)
        except yaml.scanner.ScannerError as e:
            object = json.loads(object_str)
        return object


    def getDataset(self, dataset_name):
        entry = self._getEntry(dataset_name)
        if not entry:
            print("No dataset with name {}".format(dataset_name))
            return None

        codec_meta = entry["codecMeta"]
        data = None
        if codec_meta["type"] in TYPES.NUMERICALS:
            data = self._getNumericalDataset(codec_meta)
        elif codec_meta["type"] == TYPES.BUFFER:
            data = self._getDatasetAsByte(codec_meta)
        elif codec_meta["type"] == TYPES.TEXT:
            data = self._getText(codec_meta)
        elif codec_meta["type"] == TYPES.OBJECT:
            data = self._getObject(codec_meta)

        return (data, entry["metadata"])


    def _getEntry(self, dataset_name):
        """
        Get the entry for a given dataset. Including metadata and codecMeta
        """
        for entry in self._rab_index:
            if entry["name"] == dataset_name:
                return entry
        return None


    def getMetadata(self, dataset_name):
        """
        Get the metadata (provided by the user) of a given dataset
        """
        entry = self._getEntry(dataset_name)
        if entry:
            return entry["metadata"]
        return None



    def getTotalByteSize(self):
        """
        Get the total byte size based on the metadata
        """
        total = 0
        for entry in self._rab_index:
            total += entry["codecMeta"]["byteLength"]

        return total


    def deleteDataset(self, dataset_name):
        pass


    def getDatasetType(self, dataset_name):
        if not self.hasDataset(dataset_name):
            raise Exception("The dataset {} does not exists.".format(dataset_name))

        entry = self._getEntry(dataset_name)
        return entry["codecMeta"]["type"]


    def addObject(self, dataset_name, data, metadata={}, compress=None):
        """
        Add an object, that must be a dictionnary
        """
        if self.hasDataset(dataset_name):
            raise Exception("The dataset {} already exists.".format(dataset_name))

        if metadata and not type(metadata) is dict:
            raise Exception("Metadata are optional but must be a dictionnary when provided.")

        if not type(data) is dict:
            raise Exception("The dataset must be a dictionnary.")

        # check that we will be able to write the metadata as yaml,
        # this prevents things such as circular reference but still
        # allocating space for dataset.
        try:
            yaml.dump(metadata, Dumper=yaml.Dumper, allow_unicode=True)
        except Exception as e:
            raise e

        yaml_encoded = yaml.dump(data, Dumper=yaml.Dumper, allow_unicode=True)
        bytes = yaml_encoded.encode("utf-8", "strict")

        # create a hash name for this array and a path on disk to write it temporarily
        hashedName = Tools.hashText(dataset_name)
        file_path = os.path.join(self._working_dir, hashedName)

        # If compressing is enabled, we must do it before metadata because we need
        # bytelength of the compressed buffer
        byte_length = len(bytes)
        if compress == "gzip":
            bytes = zlib.compress(bytes)
            byte_length = len(bytes)

        # Create the metadata entry
        dataset_meta = {
            "name": dataset_name,
            "filePath": file_path,
            "metadata": metadata,
            "codecMeta": {
                "byteOffset": None, # computed at write time
                "byteLength": byte_length,
                "type": TYPES.OBJECT,
                "compression": compress,
            }
        }

        self._rab_index.append(dataset_meta)

        # write the file in the temps dir.
        # We'll fetch this one when we write the whole file
        f = open(file_path, "w+b")
        f.write(bytes)
        f.close()


    def addFile(self, dataset_name, filepath, metadata={}):
        """
        Adds a file
        """
        if self.hasDataset(dataset_name):
            raise Exception("The dataset {} already exists.".format(dataset_name))

        if metadata and not type(metadata) is dict:
            raise Exception("Metadata are optional but must be a dictionnary when provided.")

        # check that we will be able to write the metadata as yaml,
        # this prevents things such as circular reference but still
        # allocating space for dataset.
        try:
            yaml.dump(metadata, Dumper=yaml.Dumper, allow_unicode=True)
        except Exception as e:
            raise e

        if not os.path.exists(filepath):
            raise Exception("The file {} does not exist.".format(filepath))

        # Create the metadata entry
        dataset_meta = {
            "name": dataset_name,
            "filePath": filepath,
            "metadata": metadata,
            "codecMeta": {
                "byteOffset": None, # computed at write time
                "byteLength": os.path.getsize(filepath),
                "type": TYPES.BUFFER
            }
        }
        self._rab_index.append(dataset_meta)


    def addNumericalDataset(self, dataset_name, data, metadata={}, compress=None, order="C"):
        """
        Add a Numpy array/ndarray
        """
        if self.hasDataset(dataset_name):
            raise Exception("The dataset {} already exists.".format(dataset_name))

        if metadata and not type(metadata) is dict:
            raise Exception("Metadata are optional but must be a dictionnary when provided.")

        # check that we will be able to write the metadata as yaml,
        # this prevents things such as circular reference but still
        # allocating space for dataset.
        try:
            yaml.dump(metadata, Dumper = yaml.Dumper, allow_unicode=True)
        except Exception as e:
            raise e

        # create a hash name for this array and a path on disk to write it temporarily
        hashedName = Tools.hashText(dataset_name)
        file_path = os.path.join(self._working_dir, hashedName)

        # If compressing is enabled, we must do it before metadata because we need
        # bytelength of the compressed buffer
        byte_length = data.nbytes
        bytes = data.tobytes(order=order)
        if compress == "gzip":
            bytes = zlib.compress(bytes)
            byte_length = len(bytes)

        # the strides could be computed but it's more efficient to have it
        # rather than re-computing it at every dig.
        # Note: Numpy gives the strides in bytes but here we want the strides in
        # number or elements because it's jsut more convenient for want we do here.
        strides = [int(i / data.dtype.itemsize) for i in data.strides]

        # Create the metadata entry
        dataset_meta = {
            "name": dataset_name,
            "filePath": file_path,
            "metadata": metadata,
            "codecMeta": {
                "shape": list(data.shape), # rather than using dimension. Even with array 1D, shape is a list (eg. [2, 2], or [12], etc.)
                "strides": strides,
                "byteOrder": order, # not relevant if "dimensions" is 1
                "byteOffset": None, # computed at write time
                "byteLength": byte_length,
                "type": data.dtype.name,
                "endianness":Tools.getNumpyArrayEndianness(data),
                "compression": compress,
            }
        }

        self._rab_index.append(dataset_meta)

        # write the file in the temps dir.
        # We'll fetch this one when we write the whole file
        f = open(file_path, "w+b")
        f.write(bytes)
        f.close()


    def addBuffer(self, dataset_name, data, metadata={}, compress=None):
        """
        Add a generic buffer (bytes)
        """
        if self.hasDataset(dataset_name):
            raise Exception("The dataset {} already exists.".format(dataset_name))

        if metadata and not type(metadata) is dict:
            raise Exception("Metadata are optional but must be a dictionnary when provided.")

        # check that we will be able to write the metadata as yaml,
        # this prevents things such as circular reference but still
        # allocating space for dataset.
        try:
            yaml.dump(metadata, Dumper = yaml.Dumper, allow_unicode=True)
        except Exception as e:
            raise e

        # create a hash name for this array and a path on disk to write it temporarily
        hashedName = Tools.hashText(dataset_name)
        file_path = os.path.join(self._working_dir, hashedName)

        # If compressing is enabled, we must do it before metadata because we need
        # bytelength of the compressed buffer
        byte_length = len(data)
        bytes = data
        if compress == "gzip":
            bytes = zlib.compress(bytes)
            byte_length = len(bytes)

        # Create the metadata entry
        dataset_meta = {
            "name": dataset_name,
            "filePath": file_path,
            "metadata": metadata,
            "codecMeta": {
                "byteOffset": None, # computed at write time
                "byteLength": byte_length,
                "type": TYPES.BUFFER,
                "compression": compress,
            }
        }

        self._rab_index.append(dataset_meta)

        # write the file in the temps dir.
        # We'll fetch this one when we write the whole file
        f = open(file_path, "w+b")
        f.write(bytes)
        f.close()


    def addText(self, dataset_name, data, metadata={}, compress=None):
        if self.hasDataset(dataset_name):
            raise Exception("The dataset {} already exists.".format(dataset_name))

        if metadata and not type(metadata) is dict:
            raise Exception("Metadata are optional but must be a dictionnary when provided.")

        if not isinstance(data, str):
            raise Exception("The dataset must be a string.")

        # check that we will be able to write the metadata as yaml,
        # this prevents things such as circular reference but still
        # allocating space for dataset.
        try:
            yaml.dump(metadata, Dumper=yaml.Dumper, allow_unicode=True)
        except Exception as e:
            raise e

        # create a hash name for this array and a path on disk to write it temporarily
        hashedName = Tools.hashText(dataset_name)
        file_path = os.path.join(self._working_dir, hashedName)

        # converting into a binary string
        bytes = data.encode("utf-8", "strict")

        # If compressing is enabled, we must do it before metadata because we need
        # bytelength of the compressed buffer
        byte_length = len(bytes)
        if compress == "gzip":
            bytes = zlib.compress(bytes)
            byte_length = len(bytes)

        # Create the metadata entry
        dataset_meta = {
            "name": dataset_name,
            "filePath": file_path,
            "metadata": metadata,
            "codecMeta": {
                "byteOffset": None, # computed at write time
                "byteLength": byte_length,
                "type": TYPES.TEXT,
                "compression": compress,
            }
        }

        self._rab_index.append(dataset_meta)

        # write the file in the temps dir.
        # We'll fetch this one when we write the whole file
        f = open(file_path, "w+b")
        f.write(bytes)
        f.close()


    def addDataset(self, dataset_name, data=None, metadata=None, filepath=None, compress=None, order="C"):
        """
        One add method to rule them all.
        Things happen in the following order:
        - If 'data' is a Numpy Array, it routes the method to addNumericalDataset
        - If 'data' is a text, it routes the method to addText
        - If 'data' is some bytes, it routes the method to addBuffer
        - If 'data' is an object, it routes the method to addObject
        - If 'data' is None and filepath is an existing file, it routes the method to addFile
        """

        if type(data) == np.ndarray:
            return self.addNumericalDataset(dataset_name=dataset_name, data=data, metadata=metadata, compress=compress, order=order)
        elif isinstance(data, str):
            return self.addText(dataset_name=dataset_name, data=data, metadata=metadata, compress=compress)
        elif type(data) == bytes:
            return self.addBuffer(dataset_name=dataset_name, data=data, metadata=metadata, compress=compress)
        elif type(data) is dict:
            return self.addObject(dataset_name=dataset_name, data=data, metadata=metadata, compress=compress)
        elif data == None and isinstance(filepath, str):
            return self.addFile(dataset_name=dataset_name, filepath=filepath, metadata=metadata)
        else:
            raise Exception("The type of dataset could not be determined.")



    def digNumericalDataset(self, dataset_name, position):
        """
        Dig into a numerical dataset to find a single value in a random access fashion,
        without
        """
        entry = self._getEntry(dataset_name)

        if not entry:
            raise Exception("The dataset {} does not exist.".format(dataset_name))

        codec_meta = entry["codecMeta"]

        if codec_meta["type"] not in TYPES.NUMERICALS:
            raise Exception("Only numerical datasets can be dug in.")

        if "compression" in codec_meta and codec_meta["compression"] != None:
            raise Exception("The dataset is compressed, digging is not possible. You can use .getDataset() and then use it as Numpy array.")

        # transform position into a list for consistency
        if type(position) == int or type(position) == float:
            position = [position]

        # computing strides in case they were missing
        if "strides" not in codec_meta:
            codec_meta["strides"] = self._computeStrides(codec_meta)

        print('computed strides', self._computeStrides(codec_meta))

        strides = codec_meta["strides"]
        shape = codec_meta["shape"]
        nb_dimensions = len(shape)
        if len(position) != nb_dimensions:
            raise Exception("The dataset is {}-dimensional, the position must also have {} dimensions.".format(nb_dimensions, nb_dimensions))

        bytes_per_elem = np.dtype(codec_meta["type"]).itemsize
        elements_to_jump = 0

        for d in range(0, nb_dimensions):
            if position[d] < 0 or position[d] >= shape[d]:
                raise Exception("The position {} is out of range. This axis range is [0, {}]".format(position[d], shape[d]-1))
            elements_to_jump += strides[d] * position[d]

        byte_offset_from_dataset_start = int(bytes_per_elem) * elements_to_jump
        byte_offset = self._data_byte_offset + codec_meta["byteOffset"] + byte_offset_from_dataset_start

        f = open(self._filepath, "rb")
        f.seek(byte_offset)
        buffer = f.read(bytes_per_elem)
        f.close()

        unpack_seq = SHORT_ENDIANNESS[codec_meta["endianness"]] + UNPACK_TYPES[codec_meta["type"]]

        value = struct.unpack(unpack_seq, buffer)
        # if codec_meta["byteOrder"] == 'C'

        return value[0]



    def digInBuffer(self, dataset_name, byte_offset, byte_length):
        """
        There is no restriction of the type of dataset that it originally is,
        hence any dataset (buffer, but also object, text and numerical) can be dug this
        way. It's to the discretion of the user to know if it makes sense.
        position is in number of byte from the begining of the {dataset_name} dataset
        """
        entry = self._getEntry(dataset_name)

        if not entry:
            raise Exception("The dataset {} does not exist.".format(dataset_name))

        codec_meta = entry["codecMeta"]

        if byte_offset < 0 or (byte_offset + byte_length) > codec_meta["byteLength"]:
            raise Exception("The byte offset and byte length are out of range")

        total_byte_offset = self._data_byte_offset + codec_meta["byteOffset"] + byte_offset

        f = open(self._filepath, "rb")
        f.seek(total_byte_offset)
        buffer = f.read(byte_length)
        f.close()

        return buffer






    def _computeStrides(self, codec_meta):
        """
        Computes the strides if by any encoding mistake they were not part of the
        metadata.
        """
        shape = codec_meta["shape"]
        nb_dimensions = len(shape)
        strides = [1]

        # compute the strides
        for d in range(1, nb_dimensions):
            strides.append(strides[-1] * shape[-d])

        strides.reverse() # the strides are now in the same order as the shape
        return strides


    def hasDataset(self, dataset_name):
        """
        Check if a dataset exists in the index
        """
        for entry in self._rab_index:
            if entry["name"] == dataset_name:
                return True
        return False


    def read(self, filepath):
        """
        Read from a file
        """
        f = open(filepath, "rb")
        self._filepath = filepath
        magic = f.read(3).decode()

        if magic != MAGIC_NUMBER:
            raise Exception("The file is not a RandomAccessBuffer.")

        # reading the index
        header_bytelength = struct.unpack('I', f.read(4))[0]

        # Try decoding in yaml, if fails, back to json (as the spec of RAB was originally using json)
        header_str = f.read(header_bytelength).decode("utf-8", "strict")
        try:
            self._rab_index = yaml.load(header_str, Loader=yaml.Loader)
        except yaml.scanner.ScannerError as e:
            self._rab_index = json.loads(header_str)

        # the byte offset of the very first dataset
        self._data_byte_offset = 7 + header_bytelength

        f.close()


    def _updateOffsets(self):
        """
        Updates the offsets based on the order of the datasets
        """
        offset = 0
        for entry in self._rab_index:
            entry["codecMeta"]["byteOffset"] = offset
            offset += entry["codecMeta"]["byteLength"]


    def write(self, filepath):
        self._updateOffsets()

        index_copy = copy.deepcopy(self._rab_index)

        # gather all files to write
        metadata_tmp_file = os.path.join(self._working_dir, "metadata")
        files_to_add = [metadata_tmp_file]

        # the filePath prop was just a temporary thing to help
        # but we dont want it for the production file
        for entry in index_copy:
            files_to_add.append(entry["filePath"])
            del entry["filePath"]

        # Create a binary version of the yaml header.
        # Note: the header is padded with a new line and a new line char is also
        # added at the end (before encoding) to ensure better readability of the
        # header with CLIs such as less/more
        byte_metadata = ("\n" + yaml.dump(index_copy, Dumper=yaml.Dumper, allow_unicode=True) + "\n").encode("utf-8", "strict")
        metadata_byte_length = len(byte_metadata)

        # write the metadata file
        meta_file = open(metadata_tmp_file, "w+b")
        meta_file.write(byte_metadata)
        meta_file.close()

        # initialise the final file with the magic number and the metadata byte length
        # out_file = open(filepath, "w+b")
        # out_file.write(MAGIC_NUMBER.encode())
        # out_file.write(struct.pack('I', metadata_byte_length))
        #
        # # writing all the files by block
        # for tempfile_path in files_to_add:
        #     tempfile = open(tempfile_path, "rb")
        #     while True:
        #         data = tempfile.read(65536)
        #         if data:
        #             out_file.write(data)
        #         else:
        #             break
        #
        # out_file.close()


        with open(filepath, "w+b") as out_file:
            out_file.write(MAGIC_NUMBER.encode())
            out_file.write(struct.pack('I', metadata_byte_length))

            # writing all the files by block
            for tempfile_path in files_to_add:
                tempfile = open(tempfile_path, "rb")
                while True:
                    data = tempfile.read(65536)
                    if data:
                        out_file.write(data)
                    else:
                        break


    def clean(self):
        """
        Clean all the temporary files
        """
        shutil.rmtree(self._working_dir, ignore_errors=True)

"""
Write piece by piece: https://stackoverflow.com/questions/5509872/python-append-multiple-files-in-given-order-to-one-big-file/18277956

# for text file
# tempfiles is an ordered list of temp files (open for reading)
f = open("bigfile.txt", "w")
for tempfile in tempfiles:
    while True:
        data = tempfile.read(65536)
        if data:
            f.write(data)
        else:
            break
"""
