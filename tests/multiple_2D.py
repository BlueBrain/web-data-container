import numpy as np
import randomaccessbuffer as rab


def create(filepath):
    print("creating...")
    # create a RandomAccessBuffer instance
    rabuff = rab.RandomAccessBuffer()

    # Add a second dataset
    rabuff.addDataset("my first array",
        data=np.array([100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 1010, 1011, 1012, 1013, 1014, 1015], dtype="int32"),
        metadata={
            "description": "this is just the first dataset"
        })

    # Add a second dataset
    rabuff.addDataset("my second array",
        data=np.array([[10, 11, 12, 13, 14, 15, 16, 17],[18, 19, 110, 111, 112, 113, 114, 115]], dtype="int32"),
        metadata={
            "description": "this is just the another dataset"
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
    filepath = "./data/multiple_2D.rab"
    create(filepath)
    read(filepath)
