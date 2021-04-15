import numpy as np
import randomaccessbuffer as rab
import json


def create(filepath):
    print("creating...")
    # create a RandomAccessBuffer instance
    rabuff = rab.RandomAccessBuffer()

    data_0 = "hello there"
    meta_0 = {
        "description": "this is just the first text"
    }

    # Add a second dataset
    rabuff.addDataset("my first array",
        data=data_0,
        metadata=meta_0
    )

    data_1 = "Some lorem ipsum"
    meta_1 = {
        "description": "this is just the another text"
    }
    # Add a second dataset
    rabuff.addDataset("my second array",
        data=data_1,
        metadata=meta_1)

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

    # get all available
    dataset_ids = rabuff.listDatasets()
    print("all datasets:", dataset_ids)

    data_all = []
    meta_all = []

    for id in dataset_ids:
        # get data and metadata in one go!
        data, meta = rabuff.getDataset(id)
        print("------------ {} ---------------".format(id))
        print("data", data)
        print("meta", meta)
        data_all.append(data)
        meta_all.append(meta)

    return (data_all, meta_all)



def test_text():
    filepath = "./tests/temp/multiple_text.rab"
    (data_in, meta_in) = create(filepath)
    (data_out, meta_out) = read(filepath)

    print(data_in)
    print(data_out)

    assert data_in[0] == data_out[0]
    assert data_in[1] == data_out[1]

    assert json.dumps(meta_in[0], sort_keys=True) == json.dumps(meta_out[0], sort_keys=True)
    assert json.dumps(meta_in[1], sort_keys=True) == json.dumps(meta_out[1], sort_keys=True)

if __name__ == "__main__":
    test_text()