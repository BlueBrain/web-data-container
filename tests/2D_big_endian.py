import numpy as np
import randomaccessbuffer as rab


def create(filepath):
    print("creating...")
    # create a RandomAccessBuffer instance
    rabuff = rab.RandomAccessBuffer()

    # build a wee array
    data = np.array([[1000, 1001, 1002, 1003, 1004, 1005, 1006, 1007],[1008, 1009, 1010, 1011, 1012, 1013, 1014, 1015]], dtype=">i4")

    meta = {
        "description": "This is a test array with 2 dimensions"
    }

    print("data", data)
    print("meta", meta)

    # Add the dataset to rabuff
    rabuff.addDataset("my wee array", data=data, metadata=meta)

    # write rabuff on disk
    rabuff.write(filepath)


def read(filepath):
    print("reading...")
    # create a RandomAccessBuffer instance
    rabuff = rab.RandomAccessBuffer()

    # read an existing RandomAccessBuffer file
    rabuff.read(filepath)

    # get all available
    dataset_ids = rabuff.listDatasets()

    # get the metadata for the first dataset of the list
    dataset_name = dataset_ids[0]
    metadata = rabuff.getMetadata(dataset_name)
    # print(metadata)

    # get data and metadata in one go!
    data, meta = rabuff.getDataset(dataset_name)
    print("data", data)
    print("meta", meta)


if __name__ == "__main__":
    filepath = "./data/2D_big_endian.rab"
    create(filepath)
    read(filepath)
