import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
from scipy.signal import savgol_filter
import glob
import os
import math

Sensor_Types = ["Asphalt Strain Gage", "Concrete Strain Gage", "Pressure Cell", "Thermocouple"]
ASG_types = [7,6,5,4,3,2,1]
CSG_types = [25,24,23,22,21]
PC_types = [3,4]
THERMO_types = [12]

ASG_placement = [36,35,34,33,32,31,30]
ASG_cal_coeff = [0.849,0.838,0.847,0.846,0.849,0.847,0.85]
ASG_rated_output = [5890,5970,5900,5910,5890,5900,5880]

CSG_placement = [29,28,27,26,25]
CSG_lin_gage_fctr = [0.05269,0.05102,0.05111,0.04984,0.04781]
CSG_poly_gage_fctr_A = [0.0021301,0.0021076,0.0008616,0.0028725,0.0008995]
CSG_poly_gage_fctr_B = [0.04845,0.04494,0.04794,0.04136,0.04573]

PC_lin_gauge_fctr = [2.516,2.481]
PC_poly_gage_fctr_A = [0.000109,0.00000135]
PC_poly_gage_fctr_B = [2.5051,2.4812]
PC_poly_gage_fctr_C = [0.4319,-0.2423]

captured_instance = ["first20", "last20"]

Raw_data_files_folder = 'Asphalt Traffic Testing\Sensors (First and Last 20 Passes)'
main_dir = os.getcwd()
os.chdir(Raw_data_files_folder)
raw_data_files = glob.glob('*.txt')
#print(raw_data_files)
os.chdir(main_dir)

dataframe_meta_data = pd.read_csv(r"meta_data.csv")
file_info_column_names = ["Filename"] + dataframe_meta_data.columns.values.tolist()
asg_processed_data_col_names = ["Filename", "Captured instance", "Asphalt Strain Gage", "Placement", "Cal Coeff(x10-6/1x10-6)", "Rated Output(x10-6)", "Extrema", "SecondsElapsed", "processed_datapoint(microstrain)"]
csg_processed_data_col_names = ["Filename", "Captured instance", "Concrete Strain Gage", "Placement", "Lin Gage Fctr(inches/mV/V)", "Poly Gage Fctr A", "Poly Gage Fctr B","Extrema", "SecondsElapsed", "processed_datapoint(inches)"]
pc_processed_data_col_names = ["Filename", "Captured instance", "Pressure Cell", "Lin Gage Fctr(kPa/mV)", "Poly Gage Fctr A", "Poly Gage Fctr B","Poly Gage Fctr C","Extrema", "SecondsElapsed", "processed_datapoint(kPa)"]
thermo_processed_data_col_names = ["Filename", "Captured instance", "Thermocouple", "Extrema", "SecondsElapsed", "processed_datapoint(F)"]

'''
print(file_info_column_names)
print(asg_processed_data_col_names)
print(csg_processed_data_col_names)
print(pc_processed_data_col_names)
print(thermo_processed_data_col_names)
'''
file_info_column_names = {file_info_column_names[i]: [] for i in range(0, len(file_info_column_names))}
file_info_csv_data = pd.DataFrame(file_info_column_names)

asg_processed_data_col_names = {asg_processed_data_col_names[i]: [] for i in range(0, len(asg_processed_data_col_names))}
asg_processed_csv_data = pd.DataFrame(asg_processed_data_col_names)

csg_processed_data_col_names = {csg_processed_data_col_names[i]: [] for i in range(0, len(csg_processed_data_col_names))}
csg_processed_csv_data = pd.DataFrame(csg_processed_data_col_names)

pc_processed_data_col_names = {pc_processed_data_col_names[i]: [] for i in range(0, len(pc_processed_data_col_names))}
pc_processed_csv_data = pd.DataFrame(pc_processed_data_col_names)

thermo_processed_data_col_names = {thermo_processed_data_col_names[i]: [] for i in range(0, len(thermo_processed_data_col_names))}
thermo_processed_csv_data = pd.DataFrame(thermo_processed_data_col_names)

dict_asg_info_per_row = dict.fromkeys(asg_processed_data_col_names)
dict_csg_info_per_row = dict.fromkeys(csg_processed_data_col_names)
dict_pc_info_per_row = dict.fromkeys(pc_processed_data_col_names)
dict_thermo_info_per_row = dict.fromkeys(thermo_processed_data_col_names)

def find_extrema(sensor_type, raw_sensor_data, SecondsElapsed_sensor):
    #minima = elastic_recovery + lower_peaks
    window_size = 50 if "thermo" in sensor_type else 100 if "press_cell" in sensor_type else 1000
    filtered_data = savgol_filter(raw_sensor_data, window_size, 3) #window size 1000 selected by trial and error
    max_value = filtered_data.max(axis=0)
    min_value = filtered_data.min(axis=0)
    average_value = (min_value + max_value)/2
    if(sensor_type == "asphalt"):
        peaks, _ = find_peaks(filtered_data, height=average_value,distance=10000)
        bases, _ = find_peaks(-1*filtered_data, height= None,distance=10000)
    
        filtered_data_minima = filtered_data[bases]
        SecondsElapsed_minima = SecondsElapsed_sensor[bases]
        
        bases_lower_peaks, _ = find_peaks(-1*filtered_data_minima, height=None)
        filtered_data_elstc_rcvry = np.delete(filtered_data_minima, bases_lower_peaks)
        SecondsElapsed_elstc_rcvry = np.delete(SecondsElapsed_minima,bases_lower_peaks)
        return SecondsElapsed_sensor[peaks], filtered_data[peaks], SecondsElapsed_elstc_rcvry, filtered_data_elstc_rcvry, filtered_data
    elif(sensor_type == "concrete"):
        peaks, _ = find_peaks(filtered_data, height=average_value,distance=10000)
        bases, _ = find_peaks(-1*filtered_data, height= None,distance=10000)
    
        filtered_data_minima = filtered_data[bases]
        SecondsElapsed_minima = SecondsElapsed_sensor[bases]
        return SecondsElapsed_sensor[peaks], filtered_data[peaks], SecondsElapsed_minima, filtered_data_minima, filtered_data
    elif(sensor_type == "press_cell"):
        peaks, _ = find_peaks(filtered_data, height=average_value,distance=10000)
        bases, _ = find_peaks(-1*filtered_data, height= -1*average_value,distance=10000)
        
        filtered_data_minima = filtered_data[bases]
        SecondsElapsed_minima = SecondsElapsed_sensor[bases]
        return SecondsElapsed_sensor[peaks], filtered_data[peaks], SecondsElapsed_minima, filtered_data_minima, filtered_data
    else: #thermo
        peaks, _ = find_peaks(filtered_data, height=None,distance=10000)
        bases, _ = find_peaks(-1*filtered_data, height= None,distance=10000)
        filtered_data_peaks = filtered_data[peaks]
        SecondsElapsed_peaks = SecondsElapsed_sensor[peaks]
        higher_peaks, _ = find_peaks(filtered_data_peaks, height=None)
        
        filtered_data_minima = filtered_data[bases]
        SecondsElapsed_minima = SecondsElapsed_sensor[bases]
        return SecondsElapsed_peaks[higher_peaks], filtered_data_peaks[higher_peaks], SecondsElapsed_minima, filtered_data_minima, filtered_data
     
def plot_data(SecondsElapsed_sensor,seconds_max, data_points_max, seconds_min, data_points_min, filtered_data):
    plt.plot(SecondsElapsed_sensor,filtered_data)
    plt.plot(seconds_max, data_points_max, "x")
    plt.plot(seconds_min, data_points_min, "r+")
    plt.show()

for day in range(1,27):
    print("Day{}".format(day))
    if(day == 2):
        continue
    day_string = "D{} ".format(day)
    files_of_day = [i for i in raw_data_files if day_string in i] #two files of a day one for F20 and other for L20
    file_info_meta_data_of_day = dataframe_meta_data.loc[dataframe_meta_data['Day'] == day]
    for file_num in range(0,len(files_of_day)): #file_num -> [1,2]; files_of_day -> two files of day
        print(files_of_day[file_num]) 
        file_info_data_per_day = dataframe_meta_data.loc[dataframe_meta_data['Day'] == day]
        file_info_data_per_day['Filename'] = files_of_day[file_num]
        notes_str = file_info_data_per_day["Notes"]
        file_info_data_per_day = file_info_data_per_day.astype(str) #to prevent integer fields like day, number of passes, etc appearing as 1.0, 2.0, etc
        file_info_data_per_day["Day"] = str(day) #somehow file_info_data_per_day.astype(str) is not converting Day field to integer. It was still float
        file_info_data_per_day["Notes"] = notes_str #after file_info_data_per_day.astype(str) notes appaering as nan
        file_info_data_per_day_dict = file_info_data_per_day.to_dict('list')                
        file_info_csv_data = pd.concat([file_info_csv_data, pd.DataFrame(file_info_data_per_day_dict)], ignore_index=True)
        
        dict_asg_info_per_row['Filename'] = files_of_day[file_num]
        dict_csg_info_per_row['Filename'] = files_of_day[file_num]
        dict_pc_info_per_row['Filename'] = files_of_day[file_num]
        dict_thermo_info_per_row['Filename'] = files_of_day[file_num]
        
        dict_asg_info_per_row['Captured instance'] = captured_instance[file_num] #there is one to one mapping between two files of a day and "F20"&"L20"
        dict_csg_info_per_row['Captured instance'] = captured_instance[file_num]
        dict_pc_info_per_row['Captured instance'] = captured_instance[file_num]
        dict_thermo_info_per_row['Captured instance'] = captured_instance[file_num]
        
        file_to_process = Raw_data_files_folder + "\\" + files_of_day[file_num]
        #print(file_to_process)
        dataframe_sensor = pd.read_csv(file_to_process, skiprows=3 , delimiter = '\t')
        SecondsElapsed_sensor  = np.array(dataframe_sensor.iloc[:,0])
        
        #Sensor_Types = ["Asphalt Strain Gage", "Concrete Strain Gage", "Pressure Cell", "Thermocouple"]
        for sensor_full_name in Sensor_Types:
            #a if a < b else b
            sensor_type = "asphalt" if "Asphalt" in sensor_full_name else "concrete" if "Concrete" in sensor_full_name else "press_cell" if "Pressure" in sensor_full_name else "thermo"
            if(sensor_full_name == "Asphalt Strain Gage"):                
                for asg_type_num in range(0,len(ASG_types)):
                   asg_processed_csv_data = pd.DataFrame(asg_processed_data_col_names)
                   dict_asg_info_per_row["Asphalt Strain Gage"] = str(ASG_types[asg_type_num])
                   dict_asg_info_per_row["Placement"] = str(ASG_placement[asg_type_num])
                   dict_asg_info_per_row["Cal Coeff(x10-6/1x10-6)"] = ASG_cal_coeff[asg_type_num]
                   dict_asg_info_per_row["Rated Output(x10-6)"] = str(ASG_rated_output[asg_type_num])
                   
                   raw_sensor_data = dataframe_sensor.iloc[:,(asg_type_num+1)]
                   seconds_max, data_points_max, seconds_min, data_points_min, filtered_data = find_extrema(sensor_type,raw_sensor_data,SecondsElapsed_sensor)
                   #plot_data(SecondsElapsed_sensor, seconds_max, data_points_max, seconds_min, data_points_min, filtered_data)
                   
                   dict_asg_info_per_row['Extrema'] = "maxima"
                   for max_point_num in range(0,len(seconds_max)):
                        dict_asg_info_per_row['SecondsElapsed'] = seconds_max[max_point_num]
                        dict_asg_info_per_row['processed_datapoint(microstrain)'] = data_points_max[max_point_num]   
                        asg_processed_csv_data = pd.concat([asg_processed_csv_data, pd.DataFrame(dict_asg_info_per_row,index=[0])], ignore_index=True)

                   dict_asg_info_per_row['Extrema'] = "minima"
                   for min_point_num in range(0,len(seconds_min)):
                        dict_asg_info_per_row['SecondsElapsed'] = seconds_min[min_point_num]
                        dict_asg_info_per_row['processed_datapoint(microstrain)'] = data_points_min[min_point_num]  
                        asg_processed_csv_data = pd.concat([asg_processed_csv_data, pd.DataFrame(dict_asg_info_per_row,index=[0])], ignore_index=True)
                    
                   if((day == 1) and (file_num == 0) and (asg_type_num == 0)):
                        asg_processed_csv_data.to_csv('asphalt_asg_processed_csv_data.csv', mode='a', index=False, header=True)
                   else:
                        asg_processed_csv_data.to_csv('asphalt_asg_processed_csv_data.csv', mode='a', index=False, header=False)
                        
            elif(sensor_full_name == "Concrete Strain Gage"):
                for csg_type_num in range(0,len(CSG_types)):
                    csg_processed_csv_data = pd.DataFrame(csg_processed_data_col_names)
                    dict_csg_info_per_row["Concrete Strain Gage"]  = str(CSG_types[csg_type_num])
                    dict_csg_info_per_row["Placement"] = str(CSG_placement[csg_type_num])
                    dict_csg_info_per_row["Lin Gage Fctr(inches/mV/V)"] = CSG_lin_gage_fctr[csg_type_num]
                    dict_csg_info_per_row["Poly Gage Fctr A"] = CSG_poly_gage_fctr_A[csg_type_num]
                    dict_csg_info_per_row["Poly Gage Fctr B"] = CSG_poly_gage_fctr_B[csg_type_num]
                    
                    raw_sensor_data = dataframe_sensor.iloc[:,len(ASG_types)+(csg_type_num+1)]
                    seconds_max, data_points_max, seconds_min, data_points_min, filtered_data = find_extrema(sensor_type,raw_sensor_data,SecondsElapsed_sensor)
                    #plot_data(SecondsElapsed_sensor, seconds_max, data_points_max, seconds_min, data_points_min, filtered_data)
                    
                    dict_csg_info_per_row['Extrema'] = "maxima"
                    for max_point_num in range(0,len(seconds_max)):
                        dict_csg_info_per_row['SecondsElapsed'] = seconds_max[max_point_num]
                        dict_csg_info_per_row['processed_datapoint(inches)'] = data_points_max[max_point_num]   
                        csg_processed_csv_data = pd.concat([csg_processed_csv_data, pd.DataFrame(dict_csg_info_per_row,index=[0])], ignore_index=True)

                    dict_csg_info_per_row['Extrema'] = "minima"
                    for min_point_num in range(0,len(seconds_min)):
                        dict_csg_info_per_row['SecondsElapsed'] = seconds_min[min_point_num]
                        dict_csg_info_per_row['processed_datapoint(inches)'] = data_points_min[min_point_num]  
                        csg_processed_csv_data = pd.concat([csg_processed_csv_data, pd.DataFrame(dict_csg_info_per_row,index=[0])], ignore_index=True)
                    
                    if((day == 1) and (file_num == 0) and (csg_type_num == 0)):
                        csg_processed_csv_data.to_csv('asphalt_csg_processed_csv_data.csv', mode='a', index=False, header=True)
                    else:
                        csg_processed_csv_data.to_csv('asphalt_csg_processed_csv_data.csv', mode='a', index=False, header=False)
            
            elif(sensor_full_name == "Pressure Cell"):
                for pc_type_num in range(0,len(PC_types)):
                    pc_processed_csv_data = pd.DataFrame(pc_processed_data_col_names)
                    dict_pc_info_per_row["Pressure Cell"] = PC_types[pc_type_num]
                    dict_pc_info_per_row["Lin Gage Fctr(kPa/mV)"] = PC_lin_gauge_fctr[pc_type_num]
                    dict_pc_info_per_row["Poly Gage Fctr A"] = PC_poly_gage_fctr_A[pc_type_num]
                    dict_pc_info_per_row["Poly Gage Fctr B"] = PC_poly_gage_fctr_B[pc_type_num]
                    dict_pc_info_per_row["Poly Gage Fctr C"] = PC_poly_gage_fctr_C[pc_type_num]
                    
                    raw_sensor_data = dataframe_sensor.iloc[:,len(ASG_types)+len(CSG_types)+(pc_type_num+1)]
                    seconds_max, data_points_max, seconds_min, data_points_min, filtered_data = find_extrema(sensor_type,raw_sensor_data,SecondsElapsed_sensor)
                    #plot_data(SecondsElapsed_sensor, seconds_max, data_points_max, seconds_min, data_points_min, filtered_data)
                    
                    dict_pc_info_per_row['Extrema'] = "maxima"
                    for max_point_num in range(0,len(seconds_max)):
                        dict_pc_info_per_row['SecondsElapsed'] = seconds_max[max_point_num]
                        dict_pc_info_per_row['processed_datapoint(kPa)'] = data_points_max[max_point_num]   
                        pc_processed_csv_data = pd.concat([pc_processed_csv_data, pd.DataFrame(dict_pc_info_per_row,index=[0])], ignore_index=True)

                    dict_pc_info_per_row['Extrema'] = "minima"
                    for min_point_num in range(0,len(seconds_min)):
                        dict_pc_info_per_row['SecondsElapsed'] = seconds_min[min_point_num]
                        dict_pc_info_per_row['processed_datapoint(kPa)'] = data_points_min[min_point_num]  
                        pc_processed_csv_data = pd.concat([pc_processed_csv_data, pd.DataFrame(dict_pc_info_per_row,index=[0])], ignore_index=True)
                    
                    if((day == 1) and (file_num == 0) and (pc_type_num == 0)):
                        pc_processed_csv_data.to_csv('asphalt_pc_processed_csv_data.csv', mode='a', index=False, header=True)
                    else:
                        pc_processed_csv_data.to_csv('asphalt_pc_processed_csv_data.csv', mode='a', index=False, header=False)
            
            elif(sensor_full_name == "Thermocouple"):                
                for thermo_type_num in range(0,len(THERMO_types)):
                    thermo_processed_csv_data = pd.DataFrame(thermo_processed_data_col_names)
                    dict_thermo_info_per_row["Thermocouple"] = THERMO_types[thermo_type_num]
                    
                    raw_sensor_data = dataframe_sensor.iloc[:,len(ASG_types)+len(CSG_types)+len(PC_types)+(thermo_type_num+1)]
                    seconds_max, data_points_max, seconds_min, data_points_min, filtered_data = find_extrema(sensor_type,raw_sensor_data,SecondsElapsed_sensor)
                    #plot_data(SecondsElapsed_sensor, seconds_max, data_points_max, seconds_min, data_points_min, filtered_data)
                    
                    dict_thermo_info_per_row['Extrema'] = "maxima"
                    for max_point_num in range(0,len(seconds_max)):
                        dict_thermo_info_per_row['SecondsElapsed'] = seconds_max[max_point_num]
                        dict_thermo_info_per_row['processed_datapoint(F)'] = data_points_max[max_point_num]   
                        thermo_processed_csv_data = pd.concat([thermo_processed_csv_data, pd.DataFrame(dict_thermo_info_per_row,index=[0])], ignore_index=True)

                    dict_thermo_info_per_row['Extrema'] = "minima"
                    for min_point_num in range(0,len(seconds_min)):
                        dict_thermo_info_per_row['SecondsElapsed'] = seconds_min[min_point_num]
                        dict_thermo_info_per_row['processed_datapoint(F)'] = data_points_min[min_point_num]  
                        thermo_processed_csv_data = pd.concat([thermo_processed_csv_data, pd.DataFrame(dict_thermo_info_per_row,index=[0])], ignore_index=True)
                    
                    if((day == 1) and (file_num == 0) and (thermo_type_num == 0)):
                        thermo_processed_csv_data.to_csv('asphalt_thermo_processed_csv_data.csv', mode='a', index=False, header=True)
                    else:
                        thermo_processed_csv_data.to_csv('asphalt_thermo_processed_csv_data.csv', mode='a', index=False, header=False)
            
file_info_csv_data.to_csv('asphalt_sensor_file_info.csv', mode='a', index=False, header=True)    