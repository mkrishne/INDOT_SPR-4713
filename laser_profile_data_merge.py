import pandas as pd
import os

for i in range(1,27):
    filename = "processed_laser_profile_data_{}.csv".format(i)
    if(os.path.isfile(filename)):
        df = pd.read_csv(filename)
        df = df.iloc[:,1:]
        print(df)
        if(i == 1):
            df.to_csv('processed_laser_profile_data.csv', mode='a', index=False, header=True)
        else:
            df.to_csv('processed_laser_profile_data.csv', mode='a', index=False, header=False)