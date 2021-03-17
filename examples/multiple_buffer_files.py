"""
This may appear similar to multiple_file.py but the main differentce is that
RandomAccessBuffer.addBuffer() will create a temporary file to be read when the
method RandomAccessBuffer.write() is called, while RandomAccessBuffer.addFile()
will not create any temp file and will simply leverage the original file
when RandomAccessBuffer.write() is called.
For this reason, RandomAccessBuffer.addFile() will have better performance.
"""

import numpy as np
import randomaccessbuffer as rab


def create(filepath):
    print("creating...")
    # create a RandomAccessBuffer instance
    rabuff = rab.RandomAccessBuffer()

    # Add a file to rabuff
    rabuff.addDataset("Dürer's Rhino",
        data=open("./input_files/rhinoceros.jpg", "rb").read(),
        metadata={
            "year": 1515,
            "artist": "Albrecht Dürer",
            "title": "Rhinoceros",
            "wikipedia link": "https://en.wikipedia.org/wiki/D%C3%BCrer%27s_Rhinoceros",
            "originalFileName": "rhinoceros.jpg"
        })

    # Add a file to rabuff
    rabuff.addDataset("Dürer's Young Hare",
        data=open("./input_files/young_hare.jpg", "rb").read(),
        metadata={
            "year": 1502,
            "artist": "Albrecht Dürer",
            "title": "Young Hare",
            "wikipedia link": "https://en.wikipedia.org/wiki/Young_Hare",
            "originalFileName": "young_hare.jpg"
        })

    # Add a file to rabuff
    rabuff.addDataset("Landseer's Stag",
        data=open("./input_files/monarch_of_the_glen.png", "rb").read(),
        metadata={
            "year": 1851,
            "artist": "Sir Edwin Landseer",
            "title": "Monarch of the Glen",
            "wikipedia link": "https://en.wikipedia.org/wiki/The_Monarch_of_the_Glen_(painting)",
            "originalFileName": "monarch_of_the_glen.png"
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

    for id in dataset_ids:
        print("------------ {} ---------------".format(id))
        # get data and metadata in one go!
        data, meta = rabuff.getDataset(id)
        print("data byteLength", len(data))
        print("meta", meta)

        # writing image on disk
        f = open("./data/{}".format(meta["originalFileName"]), "wb")
        f.write(data)
        f.close()



if __name__ == "__main__":
    filepath = "./data/multiple_buffer_file.rab"
    create(filepath)
    read(filepath)
