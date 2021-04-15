import numpy as np
import randomaccessbuffer as rab
import pytest

INDEX = 3
DATASET_NAME = "my wee array"


def create(filepath):
    print("creating...")
    # create a RandomAccessBuffer instance
    rabuff = rab.RandomAccessBuffer()

    data = np.array([10, 11, 12, 13, 14, 15, 16, 17], dtype="int32")

    # Add the dataset to rabuff
    rabuff.addDataset(DATASET_NAME,
        data=data)

    # write rabuff on disk
    rabuff.write(filepath)

    return data[INDEX]


def read(filepath):
    print("reading...")
    # create a RandomAccessBuffer instance
    rabuff = rab.RandomAccessBuffer()

    # read an existing RandomAccessBuffer file
    rabuff.read(filepath)

    # digging into a buffer to get a specific value
    value = rabuff.digNumericalDataset(DATASET_NAME, INDEX)
    print("index:", INDEX, " value:", value)
    return value

    # digging into a buffer to get a specific value
    index = 300
    value = rabuff.digNumericalDataset("my larger array", index)
    print("index:", index, " value:", value)


def test_1D_dig():
    filepath = "./tests/temp/1D_dig.rab"
    value_in = create(filepath)
    value_out = read(filepath)
    assert value_in == value_out





if __name__ == "__main__":
    test_1D_dig()