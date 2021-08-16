import pandas as pd

from read_files import Data
import matplotlib.pyplot as plt
import seaborn as sns


def print_sth(x):
    print("")
    print("")
    print(x)
    print("")
    print("")

class EDA:
    def __init__(self, datapath):
        self.datapath = datapath

    def get_all_data(self):
        all_data = []
        for day_of_week in ["mon", "tue", "wed", "thu", "fri"]:
            print(f'Day of week: {day_of_week}')
            obj = Data(datapath=self.datapath, dayofweek=day_of_week)
            all_data.append(obj.read_file())
        return pd.concat(all_data)

    def summarize_data(self):
        all_data = self.get_all_data()
        print_sth({"shape": all_data.shape})
        print_sth({"head": all_data.head(3)})
        print_sth({"tail": all_data.tail(3)})
        print_sth({"describe": all_data.describe()})
        print_sth({"Null_values": all_data.isna().sum()})
        print_sth({"location": all_data["location"].unique()})


datapath = "data/"
eda_obj = EDA(datapath=datapath)
print(eda_obj.summarize_data())
# obj = EDA(data)
# print(obj.summarize_data())