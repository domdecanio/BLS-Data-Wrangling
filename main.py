import pandas as pd
import numpy as np
import os
import glob

wd = 'C:/Users/Dom/Desktop/Data Science Project 1/python code/'

yr = ["97", "98", "99", "00", "01", "02", "03", "04", "05", "06", "07", "08",
      "09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20"]
year = list(range(1997, 2021))
qtr = ["1", "2", "3", "4"]
quintile = list(range(1, 6))

state_info = pd.read_csv("statenames.csv")
state_nums = state_info["NUM"].to_list()
state_name = state_info["NAME"].to_list()

# This CPI data is the annual ave, whose interpretation is by year end.
# Data is collected from year end 1997 to year end 2020.
cpi_lst = [160.5, 163.0, 166.6, 172.2, 177.1, 179.9, 184.0, 188.9, 195.3, 201.6, 207.342, 215.303, 214.537, 218.056,
           224.939, 229.594, 232.957, 236.736, 237.017, 240.007, 245.120, 251.107, 255.657, 258.811]
cpi_mult = []
for i in cpi_lst:
    cpi_mult.append(round(i * .01, 5))

year_level_agreg = pd.DataFrame()

for index, i in enumerate(yr):
    # this is by year
    # inc_mult creates the multiplier with which the yearly income will be standardized. "cpi_mult[index]" indicates
    # the average cpi that is current for the year whose data is being manipulated. This standardizes income value to
    # the value of $1 in 2020, thereby allowing us to use the income bracket quintiles given by current reports while
    # maintaining purchasing power representation over time.
    inc_mult = (cpi_mult[23] / cpi_mult[index])


    # Here we use "inc_mult" to scale the income and income brackets on a yearly basis.
    def update_funct(data):
        '''
        This function takes a column of data-as a list-and scales the dollar values of
        each data point to reflect 2020 purchasing power equivalents.
        :param data: list of numeric data
        :return: list of scaled, rounded, 2020 equivalent values
        '''
        new_data = []
        for i in data:
            new_data.append(round(inc_mult * i, 2))
        return new_data


    year_data = pd.DataFrame()

    for j in qtr:
        # this is by quarter
        glob.glob(os.path.join(wd, f'fmld{i}{j}.csv'))
        fmld = pd.read_csv(f'fmld{i}{j}.csv')

        if i in ["97", "98", "99", "00", "01", "02", "03"]:
            wages = fmld["EARNX"].to_list()
            retir = fmld["FSS_RRX"].to_list()
        else:
            wages = fmld["FWAGEXM"].to_list()
            retir = fmld["FSS_RRXM"].to_list()

        income_lst = [wages, retir]
        income_dat = list(map(sum, zip(*income_lst)))

        income_scaled = update_funct(income_dat)
        income_ary = np.asarray(income_scaled)

        income_df = pd.DataFrame(income_dat, columns=["Income"])

        quint_col = np.where((0 <= income_ary) & (income_ary < 27000), 1,
                             np.where((27000 <= income_ary) & (income_ary < 52000), 2,
                                      np.where((52000 <= income_ary) & (income_ary < 85000), 3,
                                               np.where((85000 <= income_ary) & (income_ary < 141000), 4,
                                                        np.where((141000 <= income_ary), 5, 9999999)))))

        quint_df = pd.DataFrame(quint_col, columns=["Inc Quint"])

        newid_lst_og = fmld["NEWID"].to_list()
        newid_lst_cl = []
        for newid in newid_lst_og:
            newid = str(newid)
            newid = newid[:-1]
            newid = int(newid)
            newid_lst_cl.append(newid)
        newid_df = pd.DataFrame(newid_lst_cl, columns=["NEWID_Cl"])

        newid = fmld["NEWID"]

        # here are all the numeric variables that I will use, which must be scaled to reflect 2020 equivalent values
        foodaway = fmld["FOODAWAY"].to_list()
        foodaway2 = update_funct(foodaway)
        foodaway_df = pd.DataFrame(foodaway2, columns=["FOODAWAY"])

        cereal = fmld["CEREAL"].to_list()
        cereal2 = update_funct(cereal)
        cereal_df = pd.DataFrame(cereal2, columns=["CEREAL"])

        foodhome = fmld["FOODHOME"].to_list()
        foodhome2 = update_funct(foodhome)
        foodhome_df = pd.DataFrame(foodhome2, columns=["FOODHOME"])

        # This section of code compiles all prepared columns into one dataframe for subsequent manipulation.
        cu_info = pd.read_csv(f"fmld{i}{j}.csv", usecols=["STRTYEAR", "STATE"])
        cu_info = pd.concat([newid, newid_df, cu_info, income_df, quint_df,
                             foodaway_df,
                             cereal_df,
                             foodhome_df,
                             ], axis=1)
        cu_info['Duplicate'] = cu_info.NEWID_Cl.duplicated()
        cu_info = cu_info.drop(cu_info[cu_info.Duplicate == True].index)
        cu_info.drop('Duplicate', axis=1, inplace=True)
        cu_info.drop('NEWID', axis=1, inplace=True)

        year_data = pd.concat([year_data, cu_info])

    year_data['Duplicate'] = year_data.NEWID_Cl.duplicated()
    year_data = year_data.drop(year_data[year_data.Duplicate == True].index)
    year_data.drop('Duplicate', axis=1, inplace=True)
    #year_data.drop('STRTYEAR', axis=1, inplace=True)
    year_data.drop('NEWID_Cl', axis=1, inplace=True)
    year_data = year_data.dropna(subset=["STATE"])

    # print(year_data)

    for bindex, value in enumerate(state_nums):
        state_df = year_data[year_data["STATE"] == value]
        state_df["STATE2"] = state_name[bindex]
        # print(state_df)

        state_quint_yr_inc_df = pd.DataFrame()


        for each in quintile:
            state_quint_df = state_df[state_df["Inc Quint"] == each]
            inc_info = round(state_quint_df["Income"].mean(axis=0), 2)
            fo1_info = round(state_quint_df["FOODAWAY"].mean(axis=0), 2)
            cer_info = round(state_quint_df["CEREAL"].mean(axis=0), 2)
            fo2_info = round(state_quint_df["FOODHOME"].mean(axis=0), 2)
            info_lst = [inc_info, fo1_info, cer_info, fo2_info]
            info_df = pd.DataFrame(info_lst, columns=["Year"])

            state_quint_yr_inc_df = pd.concat([state_quint_yr_inc_df, info_df], axis=0)

        state_quint_yr_inc_df = state_quint_yr_inc_df.transpose()
        state_quint_yr_inc_df["Year"] = year[index]
        state_quint_yr_inc_df["State"] = str(state_name[bindex])
        year_level_agreg = pd.concat([state_quint_yr_inc_df, year_level_agreg], axis=0)

col_names_list = ["Q1Income", "Q1Foodaway", "Q1Cereal", "Q1Foodhome",
                  "Q2Income", "Q2Foodaway", "Q2Cereal", "Q2Foodhome",
                  "Q3Income", "Q3Foodaway", "Q3Cereal", "Q3Foodhome",
                  "Q4Income", "Q4Foodaway", "Q4Cereal", "Q4Foodhome",
                  "Q5Income", "Q5Foodaway", "Q5Cereal", "Q5Foodhome", "Year", "State",]
year_level_agreg.columns = col_names_list
print(year_level_agreg)
#year_level_agreg.to_csv("most_manips_done.csv")
