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
pre_traffick_main_folder = "Concrete Traffic Testing\Concrete Pre-Traffic Laser Data"
os.chdir(pre_traffick_main_folder)
folder_date_strings = glob.glob('*')
#print(folder_date_strings)
os.chdir(MAIN_DIR)

file_column_names = ["Date", "Pre Traffick Folder","Filename","Order of Scan", "Starting Timestamp","Ending Timestamp","Laser beam offset(mm)", "Laser beam offset locn", \
                        "Laser beam vertical meas. Low limit(mm)", "Laser beam vertical meas. High limit(mm)", "Laser beam vertical meas. range(mm)", \
                        "Carriage Start Position(mm)", "Carriage End Position(mm)", "Axle Pos. E->W(mm)", "Laser Start Position(mm)", "Notes"]
pre_traffick_column_names   = ["Filename", "Sample Number", "Horiz(mm)=samp_no*(1384/8088)", "Laser reading(mm)", "Laserbeam locn(mm)", "Sampled Time"]
#print(file_column_names)
#print(pre_traffick_column_names)

file_column_names_for_pd = {file_column_names[i]: [] for i in range(0, len(file_column_names))}
pre_traffick_col_names_for_pd = {pre_traffick_column_names[i]: [] for i in range(0, len(pre_traffick_column_names))}

dict_file_info_per_row = dict.fromkeys(file_column_names)
dict_pre_traffick_per_row = dict.fromkeys(pre_traffick_column_names)

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
filename_count = 0
pre_traffick_reading_count = 0

for date_folder in folder_date_strings:
    pre_traffick_sub_folder = pre_traffick_main_folder + "\\" + date_folder + "\\0 Passes"
    os.chdir(pre_traffick_sub_folder)
    laser_pre_traffick_pts = glob.glob('*')
    #print(laser_pre_traffick_pts)
    os.chdir(MAIN_DIR)
    for pre_traffick_pt in laser_pre_traffick_pts: #laser_pre_traffick_pts varies for every date string
        pre_traffick_folder_path = pre_traffick_sub_folder + "\\" + pre_traffick_pt
        print(pre_traffick_folder_path)
        pre_traffick_files = os.listdir(pre_traffick_folder_path)
        for file_substring in pre_traffick_files_string_to_grep:
            filename_count = filename_count + 1
            pre_traffick_reading_count = pre_traffick_reading_count + 1
            file_info_csv_data = pd.DataFrame(file_column_names_for_pd)
            pre_traffick_csv_data = pd.DataFrame(pre_traffick_col_names_for_pd)
            
            filename = [i for i in pre_traffick_files if file_substring in i]
            if filename:
                full_file_path = pre_traffick_folder_path + "\\" + str(filename[0])
                print("\t"+filename[0])
                
                dict_file_info_per_row["Date"] = date_folder
                dict_file_info_per_row['Pre Traffick Folder'] = pre_traffick_pt
                dict_file_info_per_row["Filename"] = filename[0]
                dict_pre_traffick_per_row["Filename"] = filename[0]
                dict_file_info_per_row["Order of Scan"] = file_substring
                
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
                    dict_pre_traffick_per_row["Sample Number"] = str(df_sheet2.iloc[row_index,0])
                    dict_pre_traffick_per_row["Horiz(mm)=samp_no*(1384/8088)"] = df_sheet2.iloc[row_index,0]*(1384/8088)
                    dict_pre_traffick_per_row["Laser reading(mm)"] = filtered_laser_reading[row_index]
                    dict_pre_traffick_per_row["Laserbeam locn(mm)"] = str(df_sheet2.iloc[row_index,2])
                    dict_pre_traffick_per_row["Sampled Time"] = df_sheet2.iloc[row_index,3]
                    pre_traffick_csv_data = pd.concat([pre_traffick_csv_data, pd.DataFrame(dict_pre_traffick_per_row, index=[0])], ignore_index=True)
                    
                if(pre_traffick_reading_count == 1):
                    pre_traffick_csv_data.to_csv('processed_concrete_pre_traffick_data.csv', mode='a', index=False, header=True)
                else:
                    pre_traffick_csv_data.to_csv('processed_concrete_pre_traffick_data.csv', mode='a', index=False, header=False)
            
                if(filename_count == 1):
                    file_info_csv_data.to_csv('concrete_pre_traffick_file_info.csv', mode='a', index=False, header=True)
                else:
                    file_info_csv_data.to_csv('concrete_pre_traffick_file_info.csv', mode='a', index=False, header=False)
        print("")
