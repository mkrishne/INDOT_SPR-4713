import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
from scipy.signal import savgol_filter
import glob
import os

MAIN_DIR = os.getcwd()

#pre traffick
pre_traffick_main_folder = "Asphalt Traffic Testing\Laser Profile\Pre Traffick 07-01-22 orig\\0 Passes"
os.chdir(pre_traffick_main_folder)
laser_pre_traffick_pts = glob.glob('*')
#print(laser_pre_traffick_pts)
os.chdir(MAIN_DIR)

meta_data_column_names = ["Pre Traffick Folder", "Date", "Time", "Ending Date", "Ending Time", "Order of Scan", "Laser beam offset(mm)", "Laser beam offset locn", \
                        "Laser beam vertical meas. Low limit(mm)", "Laser beam vertical meas. High limit(mm)", "Laser beam vertical meas. range(mm)", \
                        "Carriage Start Position(mm)", "Carriage End Position(mm)", "Axle Pos. E->W(mm)", "Laser Start Position(mm)", "Sample Number", \
                        "Horiz. mm = samp_no*(1384/8088)", "Laser reading(mm)", "Laserbeam locn(mm)", "Sampled Time", "Notes"]
#print(meta_data_column_names)

processed_data_column_names = {meta_data_column_names[i]: [] for i in range(0, len(meta_data_column_names))}
processed_csv_data = pd.DataFrame(processed_data_column_names)

dict_data_per_row = dict.fromkeys(meta_data_column_names)

def filter_data(raw_laser_reading):
    laser_reading = savgol_filter(raw_laser_reading, 1000, 3) #window size 1000 selected by trial and error
    return laser_reading

def plot_data(sample_no,raw_laser_reading,filtered_laser_reading):
    plt.plot(sample_no,filtered_laser_reading)
    plt.plot(sample_no,raw_laser_reading)
    plt.show()
    
pre_traffick_files_string_to_grep = ["PL1 ", "PL2 ", "PL3 ", "PL4 ", "PL5 ", "PL6 ", "PL7 ", "PL8 ", "PL9 ", "PL10 ", "PL11 "] 
#this list is to ensure the files are processed in the order PL1 -> PL2 -> PL3 ...; Otherwise it will be processed in the order PL1 -> PL10 -> PL11 -> PL2 -> PL3 -> ... due to sorting
pd.options.display.max_colwidth = 150 #to read long columns
for pre_traffick_pt in laser_pre_traffick_pts: #laser_pre_traffick_pts = ["Pt 0-ET", "Pt 1-ET", "Pt 4-ET"]
    pre_traffick_folder_path = pre_traffick_main_folder + "\\" + pre_traffick_pt
    print(pre_traffick_folder_path)
    dict_data_per_row['Pre Traffick Folder'] = pre_traffick_pt
    pre_traffick_files = os.listdir(pre_traffick_folder_path)
    for file_substring in pre_traffick_files_string_to_grep:
        filename = [i for i in pre_traffick_files if file_substring in i][0]
        full_file_path = pre_traffick_folder_path + "\\" + str(filename)
        print("\t"+filename)
        df_sheet1 = pd.read_excel(full_file_path,sheet_name=0)
        df_sheet2 = pd.read_excel(full_file_path,sheet_name=1, header=None)
        
        date_str = str(df_sheet1.iloc[0]) #APT Laser Profiler Output Data File    Date 2022-07-01
        dict_data_per_row['Date'] = date_str.split()[7]   
        
        time_str = str(df_sheet1.iloc[1]) #APT Laser Profiler Output Data File    Time 11:01:23
        dict_data_per_row['Time'] = time_str.split()[7] 
        
        end_date_str = str(df_sheet1.iloc[22]) #APT Laser Profiler Output Data File    Ending Date: 2022-07-01
        dict_data_per_row['Ending Date'] = end_date_str.split()[8]
        
        end_time_str = str(df_sheet1.iloc[23]) #APT Laser Profiler Output Data File    Ending Time: 11:02:55
        dict_data_per_row['Ending Time'] = end_time_str.split()[8]
        
        dict_data_per_row["Order of Scan"] = file_substring
        beam_ofst_str = str(df_sheet1.iloc[3]) #APT Laser Profiler Output Data File Laser beam is offset 619.7mm to East of the Carriage Axle ceneterline
        dict_data_per_row['Laser beam offset(mm)'] = beam_ofst_str.split()[10].replace('mm',"")
        dict_data_per_row['Laser beam offset locn'] = " ".join(beam_ofst_str.split()[12:18])
        
        beam_vert_meas_str = str(df_sheet1.iloc[4])
        dict_data_per_row['Laser beam vertical meas. Low limit(mm)'] =  beam_vert_meas_str.split()[12]
        dict_data_per_row['Laser beam vertical meas. High limit(mm)'] = beam_vert_meas_str.split()[16]
        dict_data_per_row['Laser beam vertical meas. range(mm)'] = beam_vert_meas_str.split()[21].replace('mm',"")
        
        carr_start_pos_str = str(df_sheet1.iloc[6])
        dict_data_per_row['Carriage Start Position(mm)'] = carr_start_pos_str.split()[10].replace('mm',"")
        dict_data_per_row['Axle Pos. E->W(mm)'] = str(''.join(filter(str.isdigit, carr_start_pos_str.split()[17]))) #not using replace as the value will be smething of the form "->6096mm"
        
        carr_end_pos_str = str(df_sheet1.iloc[21])
        dict_data_per_row['Carriage End Position(mm)'] = carr_end_pos_str.split()[9].replace('mm',"")
        
        laser_start_pos_str =  str(df_sheet1.iloc[7])
        dict_data_per_row["Laser Start Position(mm)"] = laser_start_pos_str.split()[10].replace('mm',"")
        
        raw_laser_reading = df_sheet2.iloc[:,1]
        filtered_laser_reading = filter_data(raw_laser_reading)
        sample_no = df_sheet2.iloc[:,0]
        #plot_data(sample_no,raw_laser_reading,filtered_laser_reading)

        for row_index in range(0,len(df_sheet2.index)):
            dict_data_per_row["Sample Number"] = df_sheet2.iloc[row_index,0]
            dict_data_per_row["Horiz. mm = samp_no*(1384/8088)"] = df_sheet2.iloc[row_index,0]*(1384/8088)
            dict_data_per_row["Laser reading(mm)"] = filtered_laser_reading[row_index]
            dict_data_per_row["Laserbeam locn(mm)"] = df_sheet2.iloc[row_index,2]
            dict_data_per_row["Sampled Time"] = df_sheet2.iloc[row_index,3]
            processed_csv_data = pd.concat([processed_csv_data, pd.DataFrame(dict_data_per_row, index=[0])], ignore_index=True)

processed_csv_data.to_csv("process_laser_pretraffick_data.csv")

#df_sheet1 dataframe
'''
                  APT Laser Profiler Output Data File
0                                     Date 2022-07-01
1                                       Time 10:57:15
2                                                 NaN
3   Laser beam is offset 619.7mm to East of the Ca...
4   Laser beam vertical measurement in Vert_mm, 17...
5                                                 NaN
6   Carriage Start Position = 1400mm = Axle Pos. E...
7                       Laser Start Position = 1410mm
8                                                 NaN
9   Sheet 2 of this Workbook has the data in four ...
10  Column A us Sample Number, about 1 to 8,000 fo...
11                   Column B is Laser reading in mm.
12  Column C is Laserbeam location in mm.(not reco...
13  Column D is Time.(not recorded for vertical pr...
14                                                NaN
15  Copy Column A to Column E and change sample # ...
16  Column E will now be scaled from 0 to 1384mm w...
17  Fixed aluminium brackets protruding in beam pa...
18                                                NaN
19  For Horizontal Profiles, Copy Column B to Colu...
20  Use chart wizard to plot scatter plot of Colum...
21                    Ending Carriage Position 1413mm
22                            Ending Date: 2022-07-01
23                              Ending Time: 10:58:47
                  APT Laser Profiler Output Data File
1                                       Time 10:57:15
2                                                 NaN
3   Laser beam is offset 619.7mm to East of the Ca...
4   Laser beam vertical measurement in Vert_mm, 17...
5                                                 NaN
6   Carriage Start Position = 1400mm = Axle Pos. E...
7                       Laser Start Position = 1410mm
8                                                 NaN
9   Sheet 2 of this Workbook has the data in four ...
10  Column A us Sample Number, about 1 to 8,000 fo...
11                   Column B is Laser reading in mm.
12  Column C is Laserbeam location in mm.(not reco...
13  Column D is Time.(not recorded for vertical pr...
14                                                NaN
15  Copy Column A to Column E and change sample # ...
16  Column E will now be scaled from 0 to 1384mm w...
17  Fixed aluminium brackets protruding in beam pa...
18                                                NaN
19  For Horizontal Profiles, Copy Column B to Colu...
20  Use chart wizard to plot scatter plot of Colum...
21                    Ending Carriage Position 1413mm
22                            Ending Date: 2022-07-01
23                              Ending Time: 10:58:47
'''
