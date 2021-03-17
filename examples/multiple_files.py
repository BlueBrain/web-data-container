import numpy as np
import randomaccessbuffer as rab


def create(filepath):
    print("creating...")
    # create a RandomAccessBuffer instance
    rabuff = rab.RandomAccessBuffer()

    # Add a file to rabuff
    rabuff.addDataset("Dürer's Rhino",
        filepath="./input_files/rhinoceros.jpg",
        metadata={
            "year": 1515,
            "artist": "Albrecht Dürer",
            "title": "Rhinoceros",
            "wikipedia link": "https://en.wikipedia.org/wiki/D%C3%BCrer%27s_Rhinoceros",
            "originalFileName": "rhinoceros.jpg"
        })

    # Add a file to rabuff
    rabuff.addDataset("Dürer's Young Hare",
        filepath="./input_files/young_hare.jpg",
        metadata={
            "year": 1502,
            "artist": "Albrecht Dürer",
            "title": "Young Hare",
            "wikipedia link": "https://en.wikipedia.org/wiki/Young_Hare",
            "originalFileName": "young_hare.jpg"
        })

    # Add a file to rabuff
    rabuff.addDataset("Landseer's Stag",
        filepath="./input_files/monarch_of_the_glen.png",
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
    filepath = "./data/multiple_file.rab"
    create(filepath)
    read(filepath)
