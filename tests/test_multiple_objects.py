import json
import numpy as np
import randomaccessbuffer as rab

FIRST_DATASET_NAME = "my first object"
SECOND_DATASET_NAME = "my second object"

def create(filepath):
    print("creating...")
    # create a RandomAccessBuffer instance
    rabuff = rab.RandomAccessBuffer()

    data_0 = {"firstname": "Johnny", "lastname": "Bravo", "address": {"country": "USA", "state": "NY"}}
    meta_0 = {"description": "this is just the first object"}

    # Add a second dataset
    rabuff.addDataset(FIRST_DATASET_NAME,
        data=data_0,
        metadata=meta_0,
        compress="gzip")

    data_1 = {"firstname": "Jonathan", "lastname": "Lurie", "address": {"country": "Switzerland", "state": "VD"}}
    meta_1 = {"description": "this is just the another object"}

    # Add a second dataset
    rabuff.addDataset(SECOND_DATASET_NAME,
        data=data_1,
        metadata=meta_1,
        compress="gzip")

    # write rabuff on disk
    rabuff.write(filepath)

    return (
        [data_0, data_1],
        [meta_0, meta_1]
    )


def read(filepath):
    print("reading...")
    # create a RandomAccessBuffer instance
    rabuff = rab.RandomAccessBuffer()

    # read an existing RandomAccessBuffer file
    rabuff.read(filepath)

    data_0, meta_0 = rabuff.getDataset(FIRST_DATASET_NAME)
    data_1, meta_1 = rabuff.getDataset(SECOND_DATASET_NAME)

    return (
        [data_0, data_1],
        [meta_0, meta_1]
    )


def test():
    filepath = "./tests/temp/multiple_objects.rab"
    
    (data_in, meta_in) = create(filepath)
    (data_out, meta_out) = read(filepath)

    assert data_in[0] == data_out[0]
    assert data_in[1] == data_out[1]

    assert json.dumps(meta_in[0], sort_keys=True) == json.dumps(meta_out[0], sort_keys=True)
    assert json.dumps(meta_in[1], sort_keys=True) == json.dumps(meta_out[1], sort_keys=True)


if __name__ == "__main__":
    test()