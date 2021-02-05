import numpy as np
import randomaccessbuffer as rab


def create(filepath):
    print("creating...")
    # create a RandomAccessBuffer instance
    rabuff = rab.RandomAccessBuffer()

    # build a wee array
    data = np.array([0, 1, 2, 3, 4, 5, 6, 7], dtype="int32")

    meta = {
        "description": "This array is a test array é ï",
        "someObjectWIthNpArray": {
            "array": np.array([0, 1, 2, 3], dtype="int32")
        }
    }

    print("data", data)
    print("meta", meta)

    # Add the dataset to rabuff
    rabuff.addDataset("my wee array", data=data, metadata=meta)

    data2 = {"someDictWithNpArray": np.array([0.5, 1.5, 2.5, 3.5], dtype="float32")}
    meta2 = None

    print(data2)
    print(meta2)

    rabuff.addDataset("my other array", data=data2, metadata = meta2)

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


     # get the metadata for the first dataset of the list
    dataset_name = dataset_ids[1]
    metadata = rabuff.getMetadata(dataset_name)
    # print(metadata)

    # get data and metadata in one go!
    data, meta = rabuff.getDataset(dataset_name)
    print("data", data)
    print("meta", meta)




if __name__ == "__main__":
    filepath = "./data/1D_np_obj_and_meta.rab"
    create(filepath)
    read(filepath)
