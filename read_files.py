import glob
import os
import pandas as pd

class Data:

    def __init__(self, datapath, dayofweek):
        """
        Initialization: where all initial conditions are listed
        :param datapath: path to the file
        :param dayofweek: lower case 3 letters for the day of the week
        """
        self.data_path = datapath
        self.dayofweek = dayofweek

    def get_all_files(self):
        return glob.glob(f'{self.data_path}/*csv')

    def read_file(self):

        all_files = self.get_all_files()
        days_of_week = [i.split("/")[1][0:3] for i in all_files]
        for day in days_of_week:
            if day == self.dayofweek:
                index = days_of_week.index(day)
                return pd.read_csv(all_files[index], sep = ";")


## This lines are meant to test the class if it does what it is meant to do!
data_path = "data/"
dayofweek = "fri"
obj = Data(data_path, dayofweek)

# print(obj.read_file())
