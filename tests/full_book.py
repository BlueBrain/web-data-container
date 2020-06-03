"""
Split the Mark Twain book into chapters and store each chapter as an independant entry
in a RAB file
"""

import numpy as np
import randomaccessbuffer as rab

def create(filepath):
    # create a RandomAccessBuffer instance
    rabuff = rab.RandomAccessBuffer()
    print("creating...")

    rabuff.addDataset("details", data={
        "title": "The Adventures of Tom Sawyer",
        "author": "Mark Twain",
        "releaseDate": 1876,
        "plot": """
Tom Sawyer is a kid who is up to no good. One day, he eats jam when he’s not supposed to, skips school, and gets in a fight. Sid spills the beans about Tom’s behavior and his Aunt gets pissed. As punishment, she makes him paint her fence white. But because Tom is such a scammer, he tricks his friends into painting the fence by pretending that it is a fun thing to do. Then he goes and plays with his friends.

He sees this hot babe named Becky Thatcher. Tom really likes her. Then he goes home and Aunt Polly yells at him because she thinks he broke the sugar bowl. It was Sid who broke the bowl. Tom sees his pal Huckleberry Finn. They plan to get together at midnight for something. Tom goes to school and sees Becky again. He asks her to marry him (not really, but like kids do, ya know?). She says no because she finds out that he was once married to some other girl in the class. Tom is mad that he got shafted, so he skips school and plays with a friend.

When Tom and Huck meet at midnight, they go to the graveyard. At the graveyard, they see some dudes robbing a grave. The guys are Muff Potter, Injun Joe, and Dr Robinson. Potter and Injun Joe were hired by Robinson to rob some grave, but they refuse to do it unless he pays them more money. Robinson takes a swing at Potter, and then Injun Joe kills Robinson. Injun Joe convinces Potter that he killed Robinson. Tom and Huck see this whole thing, but don’t tell anyone because they’re scared to death of Injun Joe. Potter is arrested for the murder, and the boys take food and cigarettes to him in jail.

The next day at school Becky dumps on Tom even more. Tom is pissed, so he wants to run away. Tom, Huck, and their friend Joe decide to become pirates and sail down the river. So they steal a raft and leave. They go to Jackson’s Island (near their town). All the people in Tom’s town think the boys are dead, so they have a funeral. The boys walk in during the middle of it and shock the hell out of everyone.

Back at school, Tom takes the heat for something bad that Becky did, and she starts to like him. Then summer comes. Becky leaves town. Tom gets sick with the measles. Then Tom still feels bad about the graveyard incident and he tells the truth at Muff Potter’s trial. Injun Joe escapes. Tom is scared to death because he thinks Injun Joe is gonna kill him.

Tom and Huck go out because they want to find some treasure. They go to some abandoned house and see Injun Joe and some dude with a box of gold coins. Injun Joe hides the gold, and Tom and Huck look for it. Then Tom goes on a picnic with Becky. While Tom is at the picnic, Huck watches Injun Joe to see where he goes. Huck finds out that Injun Joe plans on beating the crap out of some old lady. Huck gets help but Injun Joe runs away.

Meanwhile, back at the picnic, Tom and Becky get lost in some cave. While they are in the cave, they see Injun Joe. Tom finds a way out. Then Becky’s dad seals the cave shut with a huge door. Joe was trapped inside, so he dies.

Tom and Huck go back to the cave and get that box of gold. They plan on hiding the gold but they are caught and have to admit to everyone that they have it. But the boys get to keep it and they become rich.
        """
    },
    compress="gzip")

    f = open("input_files/tomsawyer.txt")
    full_text = f.read()
    chapters_raw = full_text.replace("\n\n", "@").replace("\n", " ").replace("@", "\n\n").split("# ")

    chapters = []
    for chap in chapters_raw:
        clean_chap = chap.strip()#.split("/n", 1)
        if len(clean_chap) == 0:
            continue

        title_and_body = clean_chap.split("\n", 1)
        title = title_and_body[0].strip()
        body = title_and_body[1].strip()

        # Add a second dataset
        rabuff.addDataset(title, data=body, compress="gzip")

    # write rabuff on disk
    rabuff.write(filepath)


def read(filepath):
    print("reading...")
    # create a RandomAccessBuffer instance
    rabuff = rabRandomAccessBuffer()

    # read an existing RandomAccessBuffer file
    rabuff.read(filepath)

    # get all available
    dataset_ids = rabuff.listDatasets()
    print("all datasets:", dataset_ids)

    for id in dataset_ids:
        # get data and metadata in one go!
        data, meta = rabuff.getDataset(id)
        print("------------ {} ---------------".format(id))
        print(meta)
        if rabuff.getDatasetType(id) == rab.TYPES.TEXT:
            print(data[:200], " [...]\n")
        else:
            print(data)



if __name__ == "__main__":
    filepath = "./data/tom_sawyer.rab"
    create(filepath)
    read(filepath)
