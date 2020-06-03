import numpy as np
import randomaccessbuffer as rab


def create(filepath):
    print("creating...")
    # create a RandomAccessBuffer instance
    rabuff = rab.RandomAccessBuffer()

    # Add a second dataset
    rabuff.addDataset("my first array",
        data="hello there",
        metadata={
            "description": "this is just the first text"
        })

    # Add a second dataset
    rabuff.addDataset("my second array",
        data="Some lorem ipsum",
        metadata={
            "description": "this is just the another text"
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
    filepath = "./data/multiple_text.rab"
    create(filepath)
    read(filepath)
