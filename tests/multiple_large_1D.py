import numpy as np
import randomaccessbuffer as rab


def create(filepath):
    print("creating...")
    # create a RandomAccessBuffer instance
    rabuff = rab.RandomAccessBuffer()

    # Add a second dataset
    rabuff.addDataset("From 0 to 10000",
        data=np.linspace(0, 10000, num=10001, dtype="float32"),
        metadata={
            "description": "this is encoded as uncompressed float32"
        })

    # Add a second dataset
    rabuff.addDataset("From 0 to 100000",
        data=np.linspace(0, 100000, num=100001, dtype="uint32"),
        metadata={
            "description": "this is encoded as uncompressed uint32"
        })

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
    print("all datasets:", dataset_ids)

    for id in dataset_ids:
        # get data and metadata in one go!
        data, meta = rabuff.getDataset(id)
        print("------------ {} ---------------".format(id))
        print("data", data)
        print("meta", meta)


if __name__ == "__main__":
    filepath = "./data/multiple_large_1D.rab"
    create(filepath)
    read(filepath)
