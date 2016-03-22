import pickle
import os.path


class Persistence(object):
    """Saves/loads data. Works synchronously."""

    def __init__(self, fileName):
        self.fileName = fileName

    def loadData(self):
        if os.path.isfile(self.fileName):
            with open(self.fileName, 'rb') as f:
                data = pickle.load(f)
                return data

    def saveData(self, data):
        with open(self.fileName, 'wb') as f:
            pickle.dump(data, f, protocol=0)
