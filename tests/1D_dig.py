import numpy as np
import randomaccessbuffer as rab


def create(filepath):
    print("creating...")
    # create a RandomAccessBuffer instance
    rabuff = rab.RandomAccessBuffer()

    # Add the dataset to rabuff
    rabuff.addDataset("my wee array",
        data=np.array([10, 11, 12, 13, 14, 15, 16, 17], dtype="int32"))

    rabuff.addDataset("my larger array",
        data=np.linspace(0, 10000, num=10001, dtype="float32"))

    # write rabuff on disk
    rabuff.write(filepath)


def read(filepath):
    print("reading...")
    # create a RandomAccessBuffer instance
    rabuff = rab.RandomAccessBuffer()

    # read an existing RandomAccessBuffer file
    rabuff.read(filepath)

    # digging into a buffer to get a specific value
    index = 3
    value = rabuff.digNumericalDataset("my wee array", index)
    print("index:", index, " value:", value)

    # digging into a buffer to get a specific value
    index = 300
    value = rabuff.digNumericalDataset("my larger array", index)
    print("index:", index, " value:", value)


if __name__ == "__main__":
    filepath = "./data/1D_dig.rab"
    create(filepath)
    read(filepath)
