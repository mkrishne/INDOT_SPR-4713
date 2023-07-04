import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
from scipy.signal import savgol_filter
import glob
import os

MAIN_DIR = os.getcwd()
laser_profile_main_folder = "Asphalt Traffic Testing\Laser Profile"

file_column_names = ["Filename", "Order of Scan", "Starting Timestamp","Ending Timestamp","Laser beam offset(mm)", "Laser beam offset locn", \
                        "Laser beam vertical meas. Low limit(mm)", "Laser beam vertical meas. High limit(mm)", "Laser beam vertical meas. range(mm)", \
                        "Carriage Start Position(mm)", "Carriage End Position(mm)", "Axle Pos. E->W(mm)", "Laser Start Position(mm)", "Notes"]

laser_profile_data_column_names   = ["Day", "Pass Instance", "Filename", "Sample Number", "Horiz(mm)=samp_no*(1384/8088)", "Laser reading(mm)", "Laserbeam locn(mm)", "Sampled Time"]
#print(file_column_names)
#print(laser_profile_data_column_names)

file_column_names_for_pd = {file_column_names[i]: [] for i in range(0, len(file_column_names))}
lasr_prof_data_col_names_for_pd = {laser_profile_data_column_names[i]: [] for i in range(0, len(laser_profile_data_column_names))}

dict_file_info_per_row = dict.fromkeys(file_column_names)
dict_laser_profile_data_per_row = dict.fromkeys(laser_profile_data_column_names)

#print(dict_file_info_per_row)
#print(dict_laser_profile_data_per_row)

def filter_data(raw_laser_reading):
    laser_reading = savgol_filter(raw_laser_reading, 1000, 3) #window size 1000 selected by trial and error
    return laser_reading

def plot_data(sample_no,raw_laser_reading,filtered_laser_reading):
    plt.plot(sample_no,filtered_laser_reading)
    plt.plot(sample_no,raw_laser_reading)
    plt.show()
    
laser_profile_files_string_to_grep = ["PL1 ", "PL2 ", "PL3 ", "PL4 ", "PL5 ", "PL6 ", "PL7 ", "PL8 ", "PL9 ", "PL10 ", "PL11 "] 
#this list is to ensure the files are processed in the order PL1 -> PL2 -> PL3 ...; Otherwise it will be processed in the order PL1 -> PL10 -> PL11 -> PL2 -> PL3 -> ... due to sorting
laser_profile_folders_string_to_grep = ["D1 " ,"D3 " ,"D4 " ,"D5 " ,"D6 " ,"D7 " ,"D8 " ,"D9 " ,"D10 " ,"D11 " ,"D12 " ,"D13 " ,"D14 " ,"D15 " ,"D16 " ,"D17 " ,"D18 " ,"D19 " ,"D20 " ,"D21 " ,"D22 " ,"D23 " ,"D24 " ,"D25 " ,"D26 "]
#laser_profile_folders_string_to_grep serves same reason as laser_profile_files_string_to_grep; D2 is missing as it was not captured
laser_profile_folders = os.listdir(laser_profile_main_folder)
laser_profile_pass_instances = ["F20", "L20"]
pd.options.display.max_colwidth = 150 #to read long columns

#dict_file_info_per_row
#dict_laser_profile_data_per_row
#Above two dicts are needed as we are creating two csv files, representing two files in the oracle database
#csv_file1/table1 having Filename, Order of Scan, Starting Time, Ending Time, etc
#csv_file2/table2 having Day, Pass Instance, Filename, Sample Number, Horiz(mm)=samp_no*(1384/8088), etc
#later the two files will be linked using FME. The Filename of table2 will link to index of the same filename of table1. Index will be created using FME
filename_count = 0
laser_profile_reading_count = 0
for folder_substring in laser_profile_folders_string_to_grep:
    foldername = [i for i in laser_profile_folders if folder_substring in i][0]
    print(foldername)
    for pass_instance_var in laser_profile_pass_instances: #do for both F20 and L20 folders, provided they exist
        processing_folder = laser_profile_main_folder + "\\" + foldername + "\\" + pass_instance_var
        if(os.path.exists(processing_folder)):
            os.chdir(processing_folder)
        else:
            continue
        print("\t" + pass_instance_var)
        laser_profile_files = glob.glob('*.xls')
        os.chdir(MAIN_DIR)
        for file_substring in laser_profile_files_string_to_grep:
            filename = [j for j in laser_profile_files if file_substring in j]
            if filename: #only if list is not empty, then process the file
                print("\t\t" + str(filename[0]))
                file_info_csv_data = pd.DataFrame(file_column_names_for_pd)
                laser_profile_csv_data = pd.DataFrame(lasr_prof_data_col_names_for_pd)
                filename_count = filename_count + 1
                laser_profile_reading_count = laser_profile_reading_count + 1
                dict_laser_profile_data_per_row["Day"] = folder_substring.strip() #strip to ensure the whitespace in "D1 " is not included; only "D1" is appended
                dict_laser_profile_data_per_row["Pass Instance"] = pass_instance_var
                dict_laser_profile_data_per_row["Filename"] = str(filename[0])
 
                dict_file_info_per_row["Filename"] = str(filename[0]) 
                dict_file_info_per_row["Order of Scan"] = file_substring.strip()
                full_file_path = processing_folder + "\\" +filename[0]
                df_sheet1 = pd.read_excel(full_file_path,sheet_name=0)
                df_sheet2 = pd.read_excel(full_file_path,sheet_name=1, header=None)
                
                date_str = str(df_sheet1.iloc[0]) #APT Laser Profiler Output Data File    Date 2022-07-01
                time_str = str(df_sheet1.iloc[1]) #APT Laser Profiler Output Data File    Time 11:01:23
                dict_file_info_per_row['Starting Timestamp'] = str(date_str.split()[7] + " " + time_str.split()[7]) 
                
                end_date_str = str(df_sheet1.iloc[22]) #APT Laser Profiler Output Data File    Ending Date: 2022-07-01
                end_time_str = str(df_sheet1.iloc[23]) #APT Laser Profiler Output Data File    Ending Time: 11:02:55
                dict_file_info_per_row['Ending Timestamp'] = str(end_date_str.split()[8] + " " + end_time_str.split()[8]) 
                
                beam_ofst_str = str(df_sheet1.iloc[3]) #APT Laser Profiler Output Data File Laser beam is offset 619.7mm to East of the Carriage Axle ceneterline
                dict_file_info_per_row['Laser beam offset(mm)'] = beam_ofst_str.split()[10].replace('mm',"")
                dict_file_info_per_row['Laser beam offset locn'] = " ".join(beam_ofst_str.split()[12:18])
                
                beam_vert_meas_str = str(df_sheet1.iloc[4])
                dict_file_info_per_row['Laser beam vertical meas. Low limit(mm)'] =  beam_vert_meas_str.split()[12]
                dict_file_info_per_row['Laser beam vertical meas. High limit(mm)'] = beam_vert_meas_str.split()[16]
                dict_file_info_per_row['Laser beam vertical meas. range(mm)'] = beam_vert_meas_str.split()[21].replace('mm',"")
                
                carr_start_pos_str = str(df_sheet1.iloc[6])
                dict_file_info_per_row['Carriage Start Position(mm)'] = carr_start_pos_str.split()[10].replace('mm',"")
                dict_file_info_per_row['Axle Pos. E->W(mm)'] = str(''.join(filter(str.isdigit, carr_start_pos_str.split()[17]))) #not using replace as the value will be smething of the form "->6096mm"
                
                carr_end_pos_str = str(df_sheet1.iloc[21])
                dict_file_info_per_row['Carriage End Position(mm)'] = carr_end_pos_str.split()[9].replace('mm',"")
                
                laser_start_pos_str =  str(df_sheet1.iloc[7])
                dict_file_info_per_row["Laser Start Position(mm)"] = laser_start_pos_str.split()[10].replace('mm',"")
                
                raw_laser_reading = df_sheet2.iloc[:,1]
                filtered_laser_reading = filter_data(raw_laser_reading)
                sample_no = df_sheet2.iloc[:,0]
                #plot_data(sample_no,raw_laser_reading,filtered_laser_reading)
                file_info_csv_data = pd.concat([file_info_csv_data, pd.DataFrame(dict_file_info_per_row, index=[0])], ignore_index=True)
                for row_index in range(0,len(df_sheet2.index)):
                    dict_laser_profile_data_per_row["Sample Number"] = str(df_sheet2.iloc[row_index,0])
                    dict_laser_profile_data_per_row["Horiz(mm)=samp_no*(1384/8088)"] = df_sheet2.iloc[row_index,0]*(1384/8088)
                    dict_laser_profile_data_per_row["Laser reading(mm)"] = filtered_laser_reading[row_index]
                    dict_laser_profile_data_per_row["Laserbeam locn(mm)"] = str(df_sheet2.iloc[row_index,2])
                    dict_laser_profile_data_per_row["Sampled Time"] = df_sheet2.iloc[row_index,3]
                    laser_profile_csv_data = pd.concat([laser_profile_csv_data, pd.DataFrame(dict_laser_profile_data_per_row, index=[0])], ignore_index=True)
                    
                if(laser_profile_reading_count == 1):
                    laser_profile_csv_data.to_csv('processed_asphalt_laser_profile_data.csv', mode='a', index=False, header=True)
                else:
                    laser_profile_csv_data.to_csv('processed_asphalt_laser_profile_data.csv', mode='a', index=False, header=False)
                
                if(filename_count == 1):
                    file_info_csv_data.to_csv('asphalt_laser_profile_file_info.csv', mode='a', index=False, header=True)
                else:
                    file_info_csv_data.to_csv('asphalt_laser_profile_file_info.csv', mode='a', index=False, header=False)
        print("")

#processed_csv_data.to_csv("processed_laser_profile_data.csv")


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
