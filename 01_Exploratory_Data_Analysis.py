from read_files import Data

class EDA:
    def __init__(self,data):
        self.data=data

    def explore_data(self):
        return data.shape
    
data_path = "data/"
dayofweek = "mon"
data_object = Data(datapath=data_path, dayofweek=dayofweek)

data = data_object.read_file()
obj = EDA(data)
print(obj.explore_data())