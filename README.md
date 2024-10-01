# Random Access Buffer
This repository contains the Python codec for RandomAccessBuffer (RAB) file format.  

# What's RAB?
RAB is a container format, rather generic but originally thought for containing scientific datasets where precision and integrity matters. It is close to HDF5 and yet very far. It can handle multiple datasets with their metadata but contrary to HDF5 it is very easy to decode or write a parser for, even from within a web browser in native JS.

# Features
- multi-dataset, multi modality
- Each dataset is identified by a string of the user's choice. This name or id is unique in a RAB file
- Optimised for numerical typed datasets (single numbers and arrays or numbers, multidimensional, any type from uint8 to float64)
- Datasets can be objects (utf-8 YAML, binary encoded, optionally compressed)
- Datasets can be text (utf-8, binary encoded, optionally compressed)
- Datasets can be blobs/bytes/files, just like an archive (optionally compressed)
- Datasets can be spreadsheet data (i.g. Pandas Dataframe from a CSV file) with columns of various types (optionally compressed)
- Each dataset can be linked to as many metadata as necessary (utf-8 YAML, with arrays, complex objects, numbers and strings)
- Fast random access to any dataset: no need to read/parse the whole file to access a specific dataset
- Deep random access within numerical datasets: can pick a single value within a numerical dataset, given its N-dimensional position, without having to load the whole dataset in memory (good for lookups)
- Self-describing, schemaless
- Compression (gzip) can be enabled for each dataset individually
- Provide a human-readable header with an index of all the buffers (convenient to quickly check in a terminal with less/more command)
- Easy to write a parser for

One of the reason we do not want to include more complex features (such as more advanced compression algorithms) is to provide the same set of features across different languages and platforms. For example, gzip compression is very easy on pure Javascript (client side) with Pako but other compression methods are difficult to find for this language.

# What it can be used for
Practically anything, but here are some ideas:
- scientific file format to handle numerical data of various types
- 3D datasets with loads of metadata
- EEG timeseries records over multiple channels
- archive with multiple files/buffers inside
- all of the above together!

Then, RAB is a container format, it does not have to have the .rab extension, you can base your own file format on RAB, apply a structure very specific to your usage and call it anything you want!

# Format description
## Overview
The RAB format is structured as follows:

- **Magic number**: to quickly identify the file as a RAB file (ASCII, 3 bytes: "rab")
- **Header byte size**: the size of the YAML encoded header that comes just after, to easily grab it in a single take (uint32, 4 bytes)
- **Header**: YAML payload because it's more human-readable than JSON. Act as an index to locate the datasets and store additional user metadata per dataset (utf-8, variable byte length, see above)
- **First dataset**: the first dataset buffer (array of numbers, text, serialized object, file)
- **Second dataset**: the second dataset buffer (array of numbers, text, serialized object, file)
- the other datasets...


## Header
The header is YAML encoded for human-readability. Imagine typing `$ less my_file.rab` in
a terminal and know the content of the rab file directly. The header contains multiple 
kinds of informations per dataset and the datasets are organized as a top level 
structure into an array. For each dataset of the array, there is a:

The following example is the header of a dataset that contains images, a bit like a 
regular archive would, but with extra metadata:

```yaml
- codecMeta:
    byteLength: 626248
    byteOffset: 0
    compression: null
    type: bytes
  metadata:
    artist: Albrecht Dürer
    originalFileName: rhinoceros.jpg
    title: Rhinoceros
    wikipedia link: https://en.wikipedia.org/wiki/D%C3%BCrer%27s_Rhinoceros
    year: 1515
  name: Dürer's Rhino
- codecMeta:
    byteLength: 938686
    byteOffset: 626248
    compression: null
    type: bytes
  metadata:
    artist: Albrecht Dürer
    originalFileName: young_hare.jpg
    title: Young Hare
    wikipedia link: https://en.wikipedia.org/wiki/Young_Hare
    year: 1502
  name: Dürer's Young Hare
- codecMeta:
    byteLength: 4879645
    byteOffset: 1564934
    compression: null
    type: bytes
  metadata:
    artist: Sir Edwin Landseer
    originalFileName: monarch_of_the_glen.png
    title: Monarch of the Glen
    wikipedia link: https://en.wikipedia.org/wiki/The_Monarch_of_the_Glen_(painting)
    year: 1851
  name: Landseer's Stag
```

The **name** (string): the name of the dataset, must be unique in the file because it 
will act as an ID on decode/query time  

The **metadata** objects are a regular YAML objects and can be empty if a user does 
provide only data without metadata. It will be empty but it will still be present as 
`{}` for consistency.

The **codecMeta** is controlled by the RAB codec and is not exposed to the user, except if the file is open in text mode. Depending on the type of dataset, **codecMeta** will contain different properties, though, some are always present:

Then, inside the **codecMeta** you can fine...   

- **type** (string): defines the type of data encoded in the dataset. Can be "text", "bytes", "object" or one the numerical types ("bool", "int8", "uint8", "int16", "uint16", "int32", "uint32", "int64", "uint64", "float16", "float32", "float64", "complex64", "complex128")
- **byteOffset** (int): the offset in byte, where this dataset begins, starting from the first byte following the end of the index
- **byteLength** (int): the size of the dataset in number of bytes

*Note:* if the numerical type is chosen, it is usually for encoding more than a single 
number. In python, this is used to serialize entire numpy *ndarray*s (multidimensional arrays) such as time series, images data, volume, volume + t, etc. In JavaScript, those will be backed by [TypedArrays](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Typed_arrays).

Other **codecMeta** properties for each type:

- **type** *"text"*
  - **compression** (string|null): can be None or "gzip" , tell if the creator of the file asked for their dataset to be compressed or not
- **type** *"bytes"*
  - **compression** (string|null): can be None or "gzip" , tell if the creator of the file asked for their dataset to be compressed or not
- **type** *"object"*
  - **compression** (string|null): can be None or "gzip" , tell if the creator of the 
  file asked for the dataset to be compressed or not
- **type** *numerical*
  - **shape** (array): number of elements in each dimension (from the slowest varying to the fastest)
  - **strides** (array): number of elements to jump for each dimension, from the slowest varying to the fastest.
  - **byteOrder** (string): can be "C" or "F", irrelevant for 1D array (read more about it here)
  - **endianness** (string): can be "little" or "big" (read more about it here)
  - **compression** (string|null): can be None or "gzip" , tell if the creator of the file asked for their dataset to be compressed or not

The **stride** information of numerical datasets is complementary to the **shape** 
information and could be generated at read time, but we chose to have it part of the 
metadata to make it faster. If **strides** happen to be missing for a multidimensional 
dataset, they will be computed.

# Install
First, the Python package 'randomaccessbuffer' must be installed from [this repository](https://bbpgitlab.epfl.ch/dke/randomaccessbufferpy):

```bash
pip install .
```

# Examples

**Create a RAB file with a Numpy array inside**
```python
import numpy as np
from randomaccessbuffer import RandomAccessBuffer
 
# create a RandomAccessBuffer instance
my_rab = RandomAccessBuffer()
 
# build a simple array
data = np.array([0, 1, 2, 3, 4, 5, 6, 7], dtype="int32")
 
# You can add some metadata to go with the dataset (optional)
metadata = {
    "description": "This array is a test array é ï"
}
 
# Add the dataset to my_rab
my_rab.addDataset("my wee array", data=data, metadata=metadata)
 
# write my_rab on disk
my_rab.write("./some_file.rab")
```

**Create a RandomAccessBuffer with multiple things inside**
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
 
my_rab.write("./some_file.rab")
```

**Read a RandomAccessBuffer file**
```python
import randomaccessbuffer as rab 
 
# Create a RandomAccessBuffer instance
my_rab = rab.RandomAccessBuffer()
 
# Reading a RAB file from a path
# This will just parse the header that acts as an index, so most likely only a few hundred bytes.
my_rab.read("./some_file.rab")
 
 
# List all the dataset IDs available (this is a list of strings)
dataset_ids = my_rab.listDatasets()
 
for d_id in dataset_ids:
    # get data and metadata in one go!
    data, meta = my_rab.getDataset(id)
    print("------------ {} ---------------".format(id))
    print(meta) # this is a dict
     
    if my_rab.getDatasetType(d_id) == rab.TYPES.TEXT:
        # data is a text of type <str>, do something with it ...
     
    elif my_rab.getDatasetType(d_id) == rab.TYPES.BUFFER:
        # data is a buffer of type <bytes>, do something with it ...
 
    elif my_rab.getDatasetType(d_id) == rab.TYPES.OBJECT:
        # data is an object of type <dict>, do something with it ...
 
 
    elif my_rab.getDatasetType(d_id) in rab.TYPES.NUMERICALS:
        # data is an array of type <numpy.ndarray>, do something with it ...
```

More examples can be found in the `examples` and `tests` directories of this repository.
Some are using data generated from the source itself, some others are using input files.


# Comparison
Before even having the intention to create the RandomAccessBuffer format, we looked what
was available, but it turns out none of the format below was capable to handle what we 
needed. The main feature we were looking for were:
- fast/random access to data
- multi-modality
- metadata support
- n-dimensional raster/scientific data
- schemaless
- Easy to write a parser for the web (JS client side) as well as Python

Here is the list of candidates we considered:

- [HDF5](https://www.hdfgroup.org/solutions/hdf5/)
  - complex hierarchical structure
  - inconvenient metadata format
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

This comparison is of course not complete and most often stops at the first missing feature found.

# Future
Things to improve:
- in order to create files that are not limited by amount of RAM, this codec writes 
files down to disk in temps files (those are deleted afterward by the codec). In order 
to identify the temps buffers, their temps file names is an urlencoded version of the ID
of the dataset. This works fine as long as not multiple RAB files are being encoded at 
the same time that would contain dataset with the same ID. This design must be improved, 
maybe using a top folder with uuid v4 names where to put all the temp datasets for a 
single instance of RAB.

- The YAML encoding of object that can potentially contain elements that do not play 
well with other serialization languages (i.e. Numpy arrays) is an issue addressed in the
`Tool.make_safe_object()` function. Yet, this requires an intermediate step where data 
are safely converted to JSON, then back to a Python dictionary and eventually to YAML. 
Even though this produces the expected result, it would be better/faster to extend the 
YAML encoder directly.

- It would be nice that the `codeMeta` object of each dataset contains a checksum of the
binary-encoded/compressed version of the dataset's buffer. This could be sha-256 or an 
alternative, as long as every platform/language we want to use RAB on has an equivalent 
method to do the job. It's probably not an issue to find a Python package to create a 
sha-256 hash and for JS [this](https://developer.mozilla.org/en-US/docs/Web/API/SubtleCrypto/digest) seems to be an option. Then, RAB codec would have a 
built-in integrity check. In the meantime, this can still be performed "manually" and 
the hash be stored in the **dataset** object that goes in pair with each **dataset**. 
Less convenient tho!

- Object encoding for actual object payloads (and not metadata) could leverage a more 
performant type-preserving serialization. This could be a binary object serialization 
rather than a text-based one, but those usually work in pair with schemas, which we want
to avoid here (a user should not be required to provide a schemas to encode its objects).
Alternatively, the "type-preserving" part could be achieved by a specific YAML encoding 
but not sure this task is easy, especially with a multiplatform constraint. The Pickle 
encoder for dictionary could a nice inspiration.

# Funding & Acknowledgment
The development of this software was supported by funding to the Blue Brain Project, a 
research center of the École polytechnique fédérale de Lausanne (EPFL), from the Swiss 
government’s ETH Board of the Swiss Federal Institutes of Technology.

Copyright © 2020-2024 Blue Brain Project/EPFL
