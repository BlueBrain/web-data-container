import numpy as np
import pandas as pd
import randomaccessbuffer as rab

ID = "some small dataframe"

def create(filepath):
    print("creating...")
    # create a RandomAccessBuffer instance
    rabuff = rab.RandomAccessBuffer()

    # read the small csv file
    input_filepath = './input_files/small.csv'
    df = pd.read_csv(input_filepath, delim_whitespace=True)

    print(df)
    print("-------------------------------------------------------------")

    # Add the dataset to rabuff
    rabuff.addDataset(ID, data=df, metadata = {"description": "This data comes from a CSV file."}, compress="gzip")
    
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
    filepath = "./data/dataframe_small.rab"
    create(filepath)
    read(filepath)
