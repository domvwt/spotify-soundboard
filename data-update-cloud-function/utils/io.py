import _pickle as cpickle
import bz2


def save_pickle(file_path, data):
    with open(file_path, "wb") as f:
        cpickle.dump(data, f)


def load_pickle(file_path):
    with open(file_path, "rb") as f:
        return cpickle.load(f)


def compress_pickle(file_path, data):
    with bz2.BZ2File(file_path, "w") as f:
        cpickle.dump(data, f)


def decompress_pickle(file_path):
    data = bz2.open(file_path, "rb")
    data = cpickle.load(data)
    return data
