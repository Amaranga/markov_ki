from seaborn.utils import locator_to_legend_entries

import random
import glob
import calendar
import pandas as pd
from datetime import datetime
from tqdm import tqdm
import os
print(os.getcwd())


class DataPreprocessing:
    """
    This class preprocesses the data and computes
    transition probabilities
    """
    def __init__(self, datapath, pattern="csv"):
        self.datapath = datapath
        self.pattern = pattern

    def get_files(self):
        return glob.glob(f'{self.datapath}/*{self.pattern}')

    def order_files_by_day_of_week(self):
        files = self.get_files()
        filenames = []
        days = [i.split("/")[-1].split(".")[0].title() for i in files]
        for ordered_day in list(calendar.day_name):
            if ordered_day in days:
                index = days.index(ordered_day)
                filenames.append(files[index])
        return filenames

    def read_files(self):
        files = self.order_files_by_day_of_week()
        return [pd.read_csv(i, index_col = 0, parse_dates=True, sep=";") for i in files]

    def get_abbreviations_from_files(self):
        return [i.split("/")[-1].split(".")[0][0:3] for i in self.order_files_by_day_of_week()]

    def put_dfs_into_dict(self):
        weekly_names = self.get_abbreviations_from_files()
        df_dict = {}
        count = 0
        for week_name in weekly_names:
            df_dict[week_name] = self.read_files()[count]
            count += 1
        return df_dict

    def df_with_unique_ids(self):
        df_dict = self.put_dfs_into_dict()
        df_all = []
        for key in df_dict.keys():
            df = df_dict[key]
            df["day_of_week"] = df.index.day_name()
            df["customer_no"] = df["customer_no"].astype(str)
            df["shortened_day"] = [i[0:3] for i in df["day_of_week"].tolist()]
            df["customer_id"] = df["customer_no"] + "_" + df["shortened_day"]
            df.drop("shortened_day", axis = 1, inplace=True)
            df_all.append(df)
        return pd.concat(df_all)

    def add_checkout_for_customers(self):
        df_all = self.df_with_unique_ids()
        groups = df_all.groupby("customer_id")
        df_list = []
        for name, group in groups:
            last_location = group["location"][-1]
            if last_location != "checkout":
                get_last_row = group.iloc[-1, :]
                time = str(get_last_row.name)
                row_list = [i for i in get_last_row]
                time_last = datetime.strptime(f'{time.split(" ")[0]} 21:59:59', "%Y-%m-%d %H:%M:%S")
                group.loc[time_last] = [row_list[0], "checkout", row_list[2], row_list[3]]
            df_list.append(group)
        return pd.concat(df_list)


    def get_customer_and_location(self):
        df_mc = self.add_checkout_for_customers()[["customer_id", "location"]]
        df_with_entrance = df_mc[["customer_id", "location"]].groupby(["customer_id"])
        df_with_entrance_all = []
        for name, adf in tqdm(df_with_entrance):
            time_str = [i for i in adf.index.strftime("%Y-%m-%d %H:%M:%S")]
            time_first = datetime.strptime(time_str[0], "%Y-%m-%d %H:%M:%S") - pd.DateOffset(minutes=1)
            adf.loc[time_first] = [name, "entrance"]
            df_with_entrance_all.append(adf.sort_values("timestamp"))
        df = pd.concat(df_with_entrance_all)
        df.to_csv("customers_table.csv")
        return df

    def resample_by_one_minute(self):
        df_mc = self.get_customer_and_location()
        return df_mc.groupby("customer_id").resample('1T').ffill().sort_values("timestamp")

    def shift_by_one(self):
        df_mc = self.resample_by_one_minute()
        df_mc["before"] = df_mc["location"]
        df_mc["after"] =df_mc["location"].shift(-1)
        return df_mc

    def get_rid_of_checkout(self):
        df_mc = self.shift_by_one()
        return df_mc[df_mc["before"] != "checkout"]

    def get_transition_probabilities(self):
        df_mc_sub = self.get_rid_of_checkout()
        ct = pd.crosstab(df_mc_sub["after"], df_mc_sub["before"], normalize=1)
        ct["checkout"] = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        ct["entrance"] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        ct.to_csv("transition_probabilities.csv")
        return ct


#print(DataPreprocessing("/home/njeri/markov_ki/data").get_transition_probabilities())

class Customer:
    """"
    This class implements the MCMC for a single customer
    """

    def __init__(self, name, state, transition_probs, budget=100):
        self.name = name
        self.state = state
        self.budget = budget
        self.transition_probs = transition_probs

    def __repr__(self):
        # return f'Customer: {self.name} in location {self.state} with a budget of {self.budget}'
        return ""

    def next_state(self):
        '''
        Propagate the customer to the next state
        Returns nothing
        '''
        indices = list(self.transition_probs.index)
        self.state = random.choices(indices, weights=self.transition_probs[self.state])[0]
        return self.state

    # def is_active(self):
    #     not_churned = True
    #     while not_churned:
    #         next_state = self.next_state()
    #         if next_state != "checkout":
    #             print(f'Customer "{self.name}" is at location {self.state}')
    #             not_churned = True
    #         else:
    #             print(f'Customer "{self.name}" is inactive since he has reached {self.state}')
    #             not_churned = False
    #     return not_churned

    def is_active(self):
        if self.state == "checkout":
            return False
        return True



class Supermarket:
    """
Start with this to implement the supermarket simulator.
"""

import numpy as np
import pandas as pd

class Supermarket:
    """manages multiple Customer instances that are currently in the market.
    """

    def __init__(self):
        # a list of Customer objects
        self.customers = []
        self.minutes = 0
        self.last_id = 0

    def __repr__(self):
        return f'Customers: {self.customers}  Minutes: {self.minutes}   Last id: {self.last_id}'

    def get_time(self):
        """current time in HH:MM format,
        """
        return datetime.now().strftime("%H:%M")

    def print_customers(self):
        """print all customers with the current time and id in CSV format.
        """
        print(self.customers)
        return None

    def next_minute(self):
        """propagates all customers to the next state.
        """
        for customer in self.customers:
            old_state = customer.state
            next_state = customer.next_state()
            print(f'Customer {customer.name} has advanced from the {old_state} section to the {next_state} section')
        self.minutes += 1

    def add_new_customers(self, customer):
        """randomly creates new customers.
        """
        self.customers.append(customer)
        return None

    def remove_exiting_customers(self):
        """removes every customer that is not active any more.
        """
        new_customer_list = []
        for customer in self.customers:
            if customer.is_active():
                new_customer_list.append(customer)
        self.customers = new_customer_list
        return None

# Read transition probabilities
tpm_dir = "/home/njeri/spiced_projects/unsupervised-lemons/unsupervised-lemon-student-code/week08/project/transition_probabilities.csv"
where2save = "/home/njeri/spiced_projects/unsupervised-lemons/unsupervised-lemon-student-code/week08/data"
tpm_df = pd.read_csv(tpm_dir, index_col=0)

# Read customer data table
customer_data_path = "/home/njeri/spiced_projects/unsupervised-lemons/unsupervised-lemon-student-code/week08/data/customers_table.csv"
customer_df = pd.read_csv(customer_data_path)

# Get customer ids
customer_ids = customer_df["customer_id"].unique()
customer_objects = []
for customer_id in customer_ids[0:10]:
    # Instantiate a customer class
    get_df = customer_df[customer_df["customer_id"] == customer_id]
    current_state = get_df["location"].tolist()[0]
    customer_objects.append(Customer(name=customer_id, state=current_state, transition_probs=tpm_df))



# ------- Dealing with multiple customers------
# Instantiate supermarket class
supermarket_obj = Supermarket()

for customer_object in customer_objects:
    # Add customer
    supermarket_obj.add_new_customers(customer_object)

# print all customers in the supermarket
#supermarket_obj.print_customers()
from faker import Faker
f = Faker()

"""
for i in range(3):
    print("")
    print(f'minute {i+1}')
    print("=========")
    print(supermarket_obj.next_minute())
    print("")
    supermarket_obj.remove_exiting_customers()
    customer_obj = Customer(name=f.name(), state="entrance", transition_probs=tpm_df)
    supermarket_obj.add_new_customers(customer_obj)
"""





