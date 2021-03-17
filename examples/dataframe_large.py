import numpy as np
import pandas as pd
import string
import random
import time
import randomaccessbuffer as rab

ID = "some small dataframe"

def create(filepath):
    row = 1000
    print("creating...")
    # create a RandomAccessBuffer instance
    rabuff = rab.RandomAccessBuffer()

    # read the small csv file
    the_booleans = [True, False]
    ALPHABET = np.array(list(string.punctuation + string.digits + string.ascii_letters + ' '))
    print("Generating data...")
    df_columns = {
        "some_uint8": (np.random.rand(row) * 255).astype(np.uint8),
        "some_float64": (np.random.rand(row) * 255).astype(np.float64),
        "some_float32": (np.random.rand(row) * 255).astype(np.float32),
        "some_int32": (np.random.rand(row) * 1000000 - 500000).astype(np.int32),
        "some_bool":  np.random.choice(the_booleans, size=row),
    }

    # Adding strings to the dataframe (takes much longer to encode)
    list_of_rand_str = []
    for i in range(0, row):
        # s = np.random.choice(ALPHABET, size = int(1 + np.random.rand(1)[0] * 99))
        s = ''.join(random.choice(ALPHABET) for i in range(int(1 + np.random.rand(1)[0] * 99)))
        list_of_rand_str.append(s)
    
    df_columns["some_str"] = list_of_rand_str
    # print(df_columns)

    print("Creating Pandas DF...")
    df = pd.DataFrame(df_columns)

    print(df)
    print("-------------------------------------------------------------")

    # Add the dataset to rabuff
    rabuff.addDataset(
        ID, 
        data=df, 
        metadata = {"description": "This data is random"},
        # compress="gzip"
    )
    
    # write rabuff on disk
    rabuff.write(filepath)


def read(filepath):
    print("reading...")
    # create a RandomAccessBuffer instance
    rabuff = rab.RandomAccessBuffer()

    # read an existing RandomAccessBuffer file
    rabuff.read(filepath)

    # get data and metadata in one go!
    df, meta = rabuff.getDataset(ID)
    print("data:\n", df)
    print("meta:\n", meta)




if __name__ == "__main__":
    filepath = "./data/dataframe_large.rab"
    create(filepath)
    read(filepath)
