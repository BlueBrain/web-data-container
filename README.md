# Random Access Buffer
This repository contains the Python codec for RandomAccessBuffer (RAB) file format.  

# What's RAB?
RAB is a container format, rather generic but originally thought for containing scientific datasets where precision and integrity matters. It is close to HDF5 and yet very far. It can handle multiple datasets with their metadata ubt contrary to HDF5 it is very easy to decode, even from within a web browser in JS.

# Features
- multi-dataset, multi modality
- Each dataset is identified by a string of the user's choice. This name or id is unique in a RAB file
- Optimised for numerical typed datasets (single numbers and arrays or numbers, multidimensional, any type from uint8 to float64)
- Datasets can be objects (utf-8 JSON, binary encoded, optionally compressed)
- Datasets can be text (utf-8, binary encoded, optionally compressed)
- Datasets can be blobs/bytes/files, just like an archive (optionally compressed)
- Datasets can be tablar data (i.g. Pandas Dataframe fonr a CSV file) with columns of viarious types (optionally compressed)
- Each dataset can be linked to as many metadata as necessary (utf-8 JSON, with arrays, complex objects, numbers and strings)
- Fast random access to any dataset: no need to read/parse the whole file to access a specific dataset
- Deep random access within numerical datasets: can pick a single value within a numerical dataset, given its N-dimensional position, without having to load the whole dataset in memory (good for lookups)
- Self-describing, schemaless
- Compression (gzip) can be enabled for each dataset individually
- Provide an human readable header with an index of all the buffers (convenient to quickly check in a terminal with less/more command)
- Easy to write a parser for

One of the reason we do not want to include more complex features (such as more advanced compression algorithms) is to provide the same set of features across different languages and platforms. For example, gzip compression is very easy on pure Javascript (client side) with Pako but other compression methods are difficult to find for this language.

# What it can be used for
Pratically anything, but here are some ideas:
- scientific file format to handle numerical data of various types
- 3D datasets with loads of metadata
- EEG timeseries records over multiple chanels
- archive with multiple files/buffers inside
- all of the above together!

Then, RAB is a container format, it does not have to have the .rab extension, you can base your own file format on RAB, apply a structure very specific to your usage and call it anything you want!

# Install
TODO

# Usage
TODO

# Format description
## Overview
The RAB format is structured as follow:

- **Magic number**: to quickly identify the file as a RAB file (ASCII, 3 bytes: "rab")
- **Header byte size**: the size of the JSON encoded header that comes just after, to easily grab it in a single take (uint32, 4 bytes)
- **Header**: JSON with indentation, human readable. Act as an index to locate the datasets and store additional user metadata per dataset (utf-8, variable byte length, see above)
- **First dataset**: the first dataset buffer (array of numbers, text, serialized object, file)
- **Second dataset**: the second dataset buffer (array of numbers, text, serialized object, file)
- the other datasets...


## Header
The header is JSON encoded for human-readability. Imagine typing `$ less my_file.rab` in a terminal and know the content of the rab file directly. The header contains multiple kinds of informations per dataset and the datasets are organized a a top lovel structure into an array. For each dataset of the array, there is a:

- **name** (string):  the name of the dataset, must be unique in the file
- **codecMeta** (object): an index of each datasets, where to find them in the file and how long they are, etc. This is controlled by the codec, a user cannot modify it.
- **metadata** (object): an additional metadata a user may want to attach to a given dataset

The following example is the header of a dataset that contains images, a bit like a regular archive would, but with extra metadata:

```json
[
  {
    "name": "Dürer's Rhino",
    "metadata": {
      "year": 1515,
      "artist": "Albrecht Dürer",
      "title": "Rhinoceros",
      "wikipedia link": "https://en.wikipedia.org/wiki/D%C3%BCrer%27s_Rhinoceros",
      "originalFileName": "rhinoceros.jpg"
    },
    "codecMeta": {
      "byteOffset": 0,
      "byteLength": 626248,
      "type": "bytes"
    }
  },
  {
    "name": "Dürer's Young Hare",
    "metadata": {
      "year": 1502,
      "artist": "Albrecht Dürer",
      "title": "Young Hare",
      "wikipedia link": "https://en.wikipedia.org/wiki/Young_Hare",
      "originalFileName": "young_hare.jpg"
    },
    "codecMeta": {
      "byteOffset": 626248,
      "byteLength": 938686,
      "type": "bytes"
    }
  },
  {
    "name": "Landseer's Stag",
    "metadata": {
      "year": 1851,
      "artist": "Sir Edwin Landseer",
      "title": "Monarch of the Glen",
      "wikipedia link": "https://en.wikipedia.org/wiki/The_Monarch_of_the_Glen_(painting)",
      "originalFileName": "monarch_of_the_glen.png"
    },
    "codecMeta": {
      "byteOffset": 1564934,
      "byteLength": 4879645,
      "type": "bytes"
    }
  }
]
```

The **metadata** objects are a regular JSON objects and can be empty if a user does provide only data without metadata. It will be empty but it will style be present as `{}` for consistency.

The **codecMeta** is controlled by the RAB codec and is not exposed to the user, except if the file is open in text mode. Depending on the type of dataset, **codecMeta** will contain different properties, though, some are always present:

- **type** (string): defines the type of data encoded in the dataset. Can be "text", "bytes", "object" or one the numerical types ("bool", "int8", "uint8", "int16", "uint16", "int32", "uint32", "int64", "uint64", "float16", "float32", "float64", "complex64", "complex128")
- **byteOffset** (int): the offset in byte, where this dataset begins, starting from the first byte following the end of the index
- **byteLength** (int): the size of the dataset in number of bytes

*Note:* if the numerical type is chosen, it is usually for encoding more than a single number. In python, this is used to serialize entire numpy *ndarrays* (multi-dimensional arrays) such as time series, images data, volume, volume + t, etc.

Other codecMeta properties for each type:

- **type** *"text"*
  - **compression** (string|null): can be None or "gzip" , tell if the creator of the file asked for their dataset to be compressed or not
- **type** *"bytes"*
  - **compression** (string|null): can be None or "gzip" , tell if the creator of the file asked for their dataset to be compressed or not
- **type** *"object"*
  - **compression** (string|null): can be None or "gzip" , tell if the creator of the file asked for their dataset to be compressed or not
- **type** *numerical*
  - **shape** (array): number of elements in each dimensions (from the slowest varying to the fastest)
  - **strides** (array): number of elements to jump for each dimension, from the slowest varying to the fastest.
  - **byteOrder** (string): can be "C" or "F", irrelevant for 1D array (read more about it here)
  - **endianness** (string): can be "little" or "big" (read more about it here)
  - **compression** (string|null): can be None or "gzip" , tell if the creator of the file asked for their dataset to be compressed or not

The **stride** information of numerical datasets is complementary to the **shape** information and could be generated at read time but we chose to have it part of the metadata to make it faster. If **strides** happens to be missing for a multidimensional dataset, it will be computed.

# Python Code Sample
First, the Python package randomaccessbuffer must be installed from [this repository](https://bbpcode.epfl.ch/code/#/admin/projects/dke/randomaccessbufferpy):

```bash
git clone https://lurie@bbpcode.epfl.ch/code/a/dke/randomaccessbufferpy
cd randomaccessbufferpy
pip install .
```

Then in a Python file or notebook:

**Create a RAB file with a Numpy array inside**
```python
import numpy as np
from randomaccessbuffer import RandomAccessBuffer
 
 
# create a RandomAccessBuffer instance
my_rab = RandomAccessBuffer()
 
# build a simple array
data = np.array([0, 1, 2, 3, 4, 5, 6, 7], dtype="int32")
 
metadata = {
    "description": "This array is a test array é ï"
}
 
# Add the dataset to my_rab
my_rab.addDataset("my wee array", data=data, metadata=meta)
 
# write rabuff on disk
my_rab.write("./some_file.rab")
```

**Create a RandomAccessBuffer with various things inside**
```python
import numpy as np
import randomaccessbuffer as rab
 
# create a RandomAccessBuffer instance
my_rab = rab.RandomAccessBuffer()
 
 
# Add a 2D Numpy array with type int32 and enable compression
my_rab.addDataset("my first array",
    data=np.array([[100, 101, 102],
                   [103, 104, 105],
                   [106, 107, 108],
                   [109, 110, 111],
                   [112, 113, 114]], dtype="int32"),
    metadata={
        "description": "this is just the first dataset"
    },
    compress="gzip")
 
 
# Add a second 2D Numpy Array, with type float64
my_rab.addDataset("my second array",
    data=np.array([[1000, 1001, 1002],
                   [1003, 1004, 1005],
                   [1006, 1007, 1008],
                   [1009, 1010, 1011],
                   [1012, 1013, 1014]], dtype="float64"),
    metadata={
        "description": "this is just the second dataset"
    })
 
 
# Add a int32 big-endian 2D array as a dataset
my_rab.addDataset("my second array",
    data=np.array([[1000, 1001, 1002, 1003, 1004, 1005, 1006, 1007],
                   [1008, 1009, 1010, 1011, 1012, 1013, 1014, 1015]], dtype=">i4"),
    metadata={
        "description": "this is just a big endian array"
    })
 
 
# Add a small piece of text, and enable compression
my_rab.addDataset("Some text",
    data="hello there, this is a very short text but this is just an example after all",
    metadata={
        "author": "Johnny Bravo"
    })
 
 
# Add jpeg file as a dataset, and add some metadata about this painting.
# Note the argument name is no longer "data" but "filepath" !
my_rab.addDataset("Dürer's Young Hare",
    filepath="./young_hare.jpg",
    metadata={
        "year": 1502,
            "artist": "Albrecht Dürer",
            "title": "Young Hare",
            "wikipedia link": "https://en.wikipedia.org/wiki/Young_Hare",
            "originalFileName": "young_hare.jpg"
        })
 
 
# Add a buffer (type bytes, in Python) that comes from the same file as above.
# Note the argument name is back to "data"!
my_rab.addDataset("Dürer's Young Hare",
    data=open("./young_hare.jpg", "rb").read(),
    metadata={
        "year": 1502,
            "artist": "Albrecht Dürer",
            "title": "Young Hare",
            "wikipedia link": "https://en.wikipedia.org/wiki/Young_Hare",
            "originalFileName": "young_hare.jpg"
        })
 
rabuff.write("./some_file.rab")
```

**Read a RandomAccessBuffer file**
```python
import numpy as np
import randomaccessbuffer as rab
 
 
# Create a RandomAccessBuffer instance
my_rab = rab.RandomAccessBuffer()
 
 
# Reading a RAB file from a path,
# This will just parse the header that acts as an index, so most likely
# only a few hundred bytes.
my_rab.read("./some_file.rab")
 
 
# List all the dataset IDs available
# (This is a list of strings)
dataset_ids = my_rab.listDatasets()
 
for id in dataset_ids:
    # get data and metadata in one go!
    data, meta = rabuff.getDataset(id)
    print("------------ {} ---------------".format(id))
    print(meta) # this is a dict
     
    if my_rab.getDatasetType(id) == rab.TYPES.TEXT:
        # data is a text of type <str>, do something with it ...
     
    elif my_rab.getDatasetType(id) == rab.TYPES.BUFFER:
        # data is a buffer of type <bytes>, do something with it ...
 
    elif my_rab.getDatasetType(id) == rab.TYPES.OBJECT:
        # data is an object of type <dict>, do something with it ...
 
 
    elif my_rab.getDatasetType(id) in rab.TYPES.NUMERICALS:
        # data is a array of type <numpy.ndarray>, do something with it ...
```

More examples can be found in the **tests** directory of this repository.

# Examples
As a reference, many examples can be found in the `examples` folder. Some are using data generated from the source itself, some others are using input files.

# Comparison
Before even having the intention to create the RandomAccessBuffer format, we looked what was available, but it turns out none of the format below was capable to handle what we needed. The main feature we were looking for were:
- fast/random access to data
- multimodality
- metadata support
- n-dimensional raster/scientific data
- schemaless
- Easy to write a parser for the web (JS client side) as well as Python

Here is the list of candidates we considered:

- [HDF5](https://www.hdfgroup.org/solutions/hdf5/)
  - complex hierarchical structure
  - unconvenient metadata format
  - hardly possible to parse when no using the official hdf5 lib

- [FlatBuffers](https://google.github.io/flatbuffers/) (Google)
  - requires a schema

- [Protocol Buffers](https://developers.google.com/protocol-buffers/) (Google)
  - requires a schema

- [Parquet](https://parquet.apache.org/) (Apache)
  - requires a schema

- [Avro](https://avro.apache.org/) (Apache)
  - requires a schema

- [Ion](https://amzn.github.io/ion-docs/) (Amazon)
  - requires a schema

- [BSON](http://bsonspec.org/) (MongoDB)
  - does not support arrays of typed numerical values (only untyped binary buffers)
  - no random access

- [UBJSON](http://ubjson.org/)
  - no random access

- [MessagePack](https://msgpack.org/)
  - No random access

This comparison is of course not complete and most often stops at the first missing feature found