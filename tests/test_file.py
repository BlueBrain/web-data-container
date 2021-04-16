"""
This may appear similar to multiple_file.py but the main differentce is that
RandomAccessBuffer.addBuffer() will create a temporary file to be read when the
method RandomAccessBuffer.write() is called, while RandomAccessBuffer.addFile()
will not create any temp file and will simply leverage the original file
when RandomAccessBuffer.write() is called.
For this reason, RandomAccessBuffer.addFile() will have better performance.
"""
import json
import hashlib
import numpy as np
import randomaccessbuffer as rab


def test():
    filepath = "./tests/temp/multiple_buffer_file.rab"
    image_path_in = "./tests/input_files/rhinoceros.jpg"

    print("creating...")
    # create a RandomAccessBuffer instance
    rabuff_in = rab.RandomAccessBuffer()

    DURERS_RHINO = "Dürer's Rhino"
    
    meta_in = {
            "year": 1515,
            "artist": "Albrecht Dürer",
            "title": "Rhinoceros",
            "wikipedia link": "https://en.wikipedia.org/wiki/D%C3%BCrer%27s_Rhinoceros",
            "originalFileName": "rhinoceros.jpg"
        }

    # Add a file to rabuff
    rabuff_in.addDataset(DURERS_RHINO,
        filepath=image_path_in,
        metadata=meta_in)


    # write rabuff on disk
    rabuff_in.write(filepath)

    # --------------------- READING -------------------

    # create a RandomAccessBuffer instance
    rabuff_out = rab.RandomAccessBuffer()

    # read an existing RandomAccessBuffer file
    rabuff_out.read(filepath)

    data_out, meta_out = rabuff_out.getDataset(DURERS_RHINO)
    
    assert json.dumps(meta_in, sort_keys=True) == json.dumps(meta_out, sort_keys=True)
    assert hashlib.md5(open(image_path_in, "rb").read()).hexdigest() == hashlib.md5(data_out).hexdigest()


if __name__ == "__main__":
    test()
