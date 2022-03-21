import pandas as pd

data = pd.read_csv("most_manips_done.csv", usecols=["Q1Income", "Q1Foodaway", "Q1Cereal", "Q1Foodhome",
                                                    "Q2Income", "Q2Foodaway", "Q2Cereal", "Q2Foodhome",
                                                    "Q3Income", "Q3Foodaway", "Q3Cereal", "Q3Foodhome",
                                                    "Q4Income", "Q4Foodaway", "Q4Cereal", "Q4Foodhome",
                                                    "Q5Income", "Q5Foodaway", "Q5Cereal", "Q5Foodhome",
                                                    "Year", "State"])
data = data.sort_values(['State', 'Year'], ascending=[True, False])
state_lst = data["State"].to_list()
year_lst = data["Year"].to_list()
print(data)
data.to_csv("elections2.csv")

col_names = ["Q1Income", "Q1Foodaway", "Q1Cereal", "Q1Foodhome",
             "Q2Income", "Q2Foodaway", "Q2Cereal", "Q2Foodhome",
             "Q3Income", "Q3Foodaway", "Q3Cereal", "Q3Foodhome",
             "Q4Income", "Q4Foodaway", "Q4Cereal", "Q4Foodhome",
             "Q5Income", "Q5Foodaway", "Q5Cereal", "Q5Foodhome"]
year = list(range(1997, 2021))
state_info = pd.read_csv("statenames.csv")
state_nums = state_info["NUM"].to_list()
state_name = state_info["NAME"].to_list()

election_df = pd.DataFrame()

cycle = 4
for name in col_names:
    col = data[f'{name}'].to_list()

    data_bin = 0
    data_lst = []
    for value in col:

        if cycle == 4:
            cycle = 4
            data_bin += value
            cycle -= 1

        elif cycle == 3:
            data_bin += value
            cycle -= 1

        elif cycle == 2:
            data_bin -= value
            cycle -= 1

        elif cycle == 1:
            data_bin -= value
            data_lst.append(round(data_bin, 2))
            data_bin = 0
            cycle = 4

    col_df = pd.DataFrame(data_lst, columns=[name])
    election_df = pd.concat([election_df, col_df], axis=1)
print(election_df)

tag = list(range(0, 1104, 4))
state_lst_cln = []
for index, value in enumerate(state_lst):
    for i in tag:
        if index == i:
            state_lst_cln.append(value)

year_lst_cln = []
for index, value in enumerate(year_lst):
    for i in tag:
        if index == i:
            year_lst_cln.append(value)

state_df = pd.DataFrame(state_lst_cln, columns=["State"])
year_df = pd.DataFrame(year_lst_cln, columns=["Year"])

election_df = pd.concat([year_df, state_df, election_df], axis=1)
election_df = election_df.dropna(thresh=3)
print(election_df)
election_df.to_csv("elections.csv")