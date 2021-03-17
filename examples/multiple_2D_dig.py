import time
import numpy as np
import randomaccessbuffer as rab


def create(filepath):
    print("creating...")
    # create a RandomAccessBuffer instance
    rabuff = rab.RandomAccessBuffer()

    arr = np.array([[100, 101, 102],
                    [103, 104, 105],
                    [106, 107, 108],
                    [109, 110, 111],
                    [112, 113, 114]], dtype="int32")
    # print(">>> arr stride as declared: ", arr.strides)

    # Add a second dataset
    rabuff.addDataset("my first array",
        data=arr,
        metadata={
            "description": "this is just the first dataset"
        })

    arr2 = np.array([[1000, 1001, 1002],
                    [1003, 1004, 1005],
                    [1006, 1007, 1008],
                    [1009, 1010, 1011],
                    [1012, 1013, 1014]], dtype="float64")
    # print(">>> arr stride as declared: ", arr.strides)


    # Add a second dataset
    rabuff.addDataset("my second array",
        data=arr2,
        metadata={
            "description": "this is just the second dataset"
        })

    arr3 = np.array([[[0, 1, 2],
                      [3, 4, 5]],

                     [[6, 7, 8],
                      [9, 10, 11]]])


    rabuff.addDataset("my third array",
        data=arr3,
        metadata={
            "description": "this is just the third dataset"
        })

    


    arr4 = np.linspace(0, 10000, num=(100*200*300), dtype="float32")
    arr4.shape = (100, 200, 300)

    print(arr4[60, 130, 234])

    print('strides', arr4.strides)


    rabuff.addDataset("my fourth array",
        data=arr4,
        metadata={
            "description": "this is just the fourth dataset"
        })


    rabuff.write(filepath)


def read(filepath):
    print("reading...")
    # create a RandomAccessBuffer instance
    t0 = time.perf_counter()
    rabuff = rab.RandomAccessBuffer()
    t1 = time.perf_counter()
    print("Reading file: ", (t1 - t0) * 1000, "ms")

    # read an existing RandomAccessBuffer file
    rabuff.read(filepath)

    index = [60, 130, 234]
    t0 = time.perf_counter()
    value = rabuff.digNumericalDataset("my fourth array", index)
    t1 = time.perf_counter()
    print("Digging: ", (t1 - t0) * 1000, "ms")
    print("index:", index, " value:", value)


if __name__ == "__main__":
    filepath = "./data/multiple_2D_dig.rab"
    create(filepath)
    read(filepath)
