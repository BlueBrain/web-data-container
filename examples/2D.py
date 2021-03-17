import numpy as np
import randomaccessbuffer as rab


def create(filepath):
    print("creating...")
    # create a RandomAccessBuffer instance
    rabuff = rab.RandomAccessBuffer()

    # build a wee array
    data = np.array([[0, 1, 2, 3, 4, 5, 6, 7],[8, 9, 10, 11, 12, 13, 14, 15]], dtype="int32")

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
    filepath = "./data/2D.rab"
    create(filepath)
    read(filepath)
