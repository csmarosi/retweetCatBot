import pickle
import os.path


class Persistence(object):
    """Saves/loads data. Works synchronously."""

    def loadData(self, fileName):
        if os.path.isfile(fileName):
            with open(fileName, 'rb') as f:
                data = pickle.load(f)
                return data

    def saveData(self, fileName, data):
        # print('============Persistence.saveData()============')
        with open(fileName, 'wb') as f:
            pickle.dump(data, f, protocol=0)
