import bz2
import _pickle as cpickle


def save_pickle(file_path, data):
    with open(file_path, "wb") as f:
        cpickle.dump(data, f)


def load_pickle(file_path):
    with open(file_path, "rb") as f:
        return f.read()


def compressed_pickle(file_path, data):
    with bz2.BZ2File(file_path, "w") as f:
        cpickle.dump(data, f)


def decompress_pickle(file_path):
    data = bz2.BZ2File(file_path, "rb")
    data = cpickle.load(data)
    return data
