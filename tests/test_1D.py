import json
import numpy as np
import randomaccessbuffer as rab



def test_1D():
    filepath = "./tests/temp/1D.rab"

    # print("creating...")
    # create a RandomAccessBuffer instance
    rabuff = rab.RandomAccessBuffer()

    # build a wee array
    data = np.array([0, 1, 2, 3, 4, 5, 6, 7], dtype="int32")

    meta = {
        "description": "This array is a test array é ï"
    }

    # print("data", data)
    # print("meta", meta)

    # Add the dataset to rabuff
    rabuff.addDataset("my wee array", data=data, metadata=meta)

    # write rabuff on disk
    rabuff.write(filepath)


    # print("reading...")
    # create a RandomAccessBuffer instance
    rabuff_out = rab.RandomAccessBuffer()

    # read an existing RandomAccessBuffer file
    rabuff_out.read(filepath)

    # get all available
    dataset_ids = rabuff_out.listDatasets()

    # get the metadata for the first dataset of the list
    dataset_name = dataset_ids[0]
    metadata = rabuff_out.getMetadata(dataset_name)
    # print(metadata)

    # get data and metadata in one go!
    data_out, meta_out = rabuff_out.getDataset(dataset_name)
    # print("data", data_out)
    # print("meta", meta_out)

    json_meta_in = json.dumps(meta, sort_keys=True)
    json_meta_out = json.dumps(meta_out, sort_keys=True)

    assert json_meta_in == json_meta_out
    assert (data_out==data).all()

if __name__ == "__main__":
    test_1D()