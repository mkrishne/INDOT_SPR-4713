import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
from scipy.signal import savgol_filter
import glob
import os
from datetime import datetime


MAIN_DIR = os.getcwd()
os.chdir("FWD Data")
fwd_txt_files = glob.glob('*.txt')
print(fwd_txt_files)
os.chdir(MAIN_DIR)
#fwd_txt_files = fwd_txt_files[0:1]

Sensor_Types = ["Asphalt Strain Gage", "Concrete Strain Gage", "Pressure Cell", "Thermocouple", "Digital/tacho"]
ASG_type = list(range(1,8))
ASG_placement = list(range(30,37))
ASG_cal_coeff = [0.849 ,0.838 ,0.847 ,0.846 ,0.849 ,0.847 ,0.85]
ASG_rated_output = [5890 ,5970 ,5900 ,5910 ,5890 ,5900 ,5880]

CSG_type = [1 ,2 ,3 ,4 ,5 ,6 ,7 ,8 ,9 ,10 ,11 ,13 ,19 ,20 ,21 ,22 ,23 ,24 ,25 ,26]
CSG_placement = [5 ,6 ,7 ,8 ,9 ,10 ,11 ,12 ,13 ,14 ,15 ,17 ,23 ,24 ,25 ,26 ,27 ,28 ,29 ,37] #not all number from 5 to 37 are present; CSG_type=1 has placement=5; CSG_type=2 has placement=6 and so on
CSG_lin_gage_fctr = [0.05076 ,0.05628 ,0.05286 ,0.05451 ,0.04877 ,0.04410 ,0.04682 ,0.04854 ,0.04618 ,0.04378 ,0.05302 ,0.04620 ,0.04751 ,0.04691 ,0.04781 ,0.04984 ,0.05111 ,0.05102 ,0.05269 ,0.05477]
CSG_poly_gage_fctr_A = [0.0013139 ,0.0016854 ,0.0016798 ,0.0016435 ,0.0025831 ,0.0023074 ,0.0017185 ,0.0017038 ,0.0027864 ,0.0016426 ,0.0041353 ,0.0020124 ,0.0017927 ,0.0009142 ,0.0008995 ,0.0028725 ,0.0008616 ,0.0021076 ,0.0021301 ,0.001704]       
CSG_poly_gage_fctr_B = [0.04730 ,0.05155 ,0.05022 ,0.05195 ,0.04582 ,0.03881 ,0.04278 ,0.04657 ,0.04131 ,0.04094 ,0.04732 ,0.03889 ,0.04198 ,0.04507 ,0.04573 ,0.04136 ,0.04794 ,0.04494 ,0.04845 ,0.05133]

PC_type = [1,2,3,4]
PC_lin_gauge_fctr = [2.516,2.516,2.481,2.481]
PC_poly_gage_fctr_A = [0.000109,0.000109,0.00000135,0.00000135]
PC_poly_gage_fctr_B = [2.5051,2.5051,2.4812,2.4812]
PC_poly_gage_fctr_C = [0.4319,0.4319,-0.2423,-0.2423]

file_numbers = []
for i in range(0,14):
    file_numbers =  file_numbers + ["#" + str(i)]
print(file_numbers) # ['#0', '#1', '#2', '#3', '#4', '#5', '#6', '#7', '#8', '#9', '#10', '#11', '#12', '#13']
try_instances = ["TRY 1","TRY 2"]

file_info_column_names = ["Filename", "File Number", "Try Instance", "Starting Timestamp"]
asg_processed_data_col_names = ["Filename", "Asphalt Strain Gage", "Placement", "Cal Coeff(x10-6/1x10-6)", "Rated Output(x10-6)", "Extrema", "SecondsElapsed", "processed_datapoint(microstrain)"]
csg_processed_data_col_names = ["Filename", "Concrete Strain Gage", "Placement", "Lin Gage Fctr(inches/mV/V)", "Poly Gage Fctr A", "Poly Gage Fctr B","Extrema", "SecondsElapsed", "processed_datapoint(inches)"]
pc_processed_data_col_names = ["Filename", "Pressure Cell", "Lin Gage Fctr(kPa/mV)", "Poly Gage Fctr A", "Poly Gage Fctr B","Poly Gage Fctr C","Extrema", "SecondsElapsed", "processed_datapoint(kPa)"]
thermo_processed_data_col_names = ["Filename", "Thermocouple", "Extrema", "SecondsElapsed", "processed_datapoint(F)"]
tacho_processed_data_col_names = ["Filename","SecondsElapsed","processed_datapoint"]

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

tacho_processed_data_col_names = {tacho_processed_data_col_names[i]: [] for i in range(0, len(tacho_processed_data_col_names))}
tacho_processed_csv_data = pd.DataFrame(tacho_processed_data_col_names)

dict_asg_info_per_row = dict.fromkeys(asg_processed_data_col_names)
dict_csg_info_per_row = dict.fromkeys(csg_processed_data_col_names)
dict_pc_info_per_row = dict.fromkeys(pc_processed_data_col_names)
dict_thermo_info_per_row = dict.fromkeys(thermo_processed_data_col_names)
dict_tacho_info_per_row = dict.fromkeys(tacho_processed_data_col_names)

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
    elif(sensor_type == "thermo"): 
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

asg_entry_num = 0
csg_entry_num = 0
pc_entry_num = 0
thermo_entry_num = 0
tacho_entry_num = 0

for hash_file_number in file_numbers:
    filenames = [j for j in fwd_txt_files if hash_file_number in j]
    if filenames: #only if list is not empty, then process the file
        file_info_data_per_day = {}
        for try_number in try_instances:
            process_filename = [j for j in filenames if try_number in j]
            if(process_filename):
                file_info_data_per_day['Filename'] = process_filename[0]
                file_info_data_per_day["File Number"] = hash_file_number.replace("#","")
                file_info_data_per_day["Try Instance"] = try_number
                file_path = "FWD Data" + "\\" + process_filename[0]
                print(file_path)
                dataframe_sensor = pd.read_csv(file_path, skiprows=3, delimiter = '\t')
                starting_timestamp = pd.read_csv(file_path, skiprows=2,nrows=1,header=None)
                starting_timestamp = str(starting_timestamp.iloc[0]) #starting_timestamp = "0    Start Time:  6/10/2022 10:49:04 AM"
                file_date = starting_timestamp.split()[3] #6/10/2022 
                d = datetime.strptime(file_date, "%m/%d/%Y")
                oracle_date = d.strftime('%Y-%m-%d')
                
                file_time = starting_timestamp.split()[4] + " " + starting_timestamp.split()[5] #file_time = "10:49:04 AM"
                in_time = datetime.strptime(file_time, "%I:%M:%S %p")
                oracle_time = datetime.strftime(in_time, "%H:%M:%S") #convert to 24hour format for oracle
                file_info_data_per_day["Starting Timestamp"] = oracle_date + " " + oracle_time
                file_info_csv_data = pd.concat([file_info_csv_data, pd.DataFrame(file_info_data_per_day,index=[0])], ignore_index=True)
                
                SecondsElapsed_sensor  = np.array(dataframe_sensor.iloc[:,0])
                data_columns = dataframe_sensor.columns[2:]
                for column_num in range(0,len(data_columns)):
                    column_name = data_columns[column_num]
                    sensor_type = "asphalt" if "ASG" in column_name else "concrete" if "CSG" in column_name else "press_cell" if "PC" in column_name else "thermo" if "Thermo" in column_name else "tacho"
                    print("\t" + sensor_type)
                    if(sensor_type == "asphalt"):  
                       asg_entry_num = asg_entry_num + 1
                       dict_asg_info_per_row['Filename'] = process_filename[0]
                       asg_processed_csv_data = pd.DataFrame(asg_processed_data_col_names)
                       dict_asg_info_per_row["Asphalt Strain Gage"] = str(column_name[4]) #ASG 7- #36 assignment; pick 7
                       ASG_type_indx = ASG_type.index(int(column_name[4]))
                       dict_asg_info_per_row["Placement"] = str(ASG_placement[ASG_type_indx])
                       dict_asg_info_per_row["Cal Coeff(x10-6/1x10-6)"] = ASG_cal_coeff[ASG_type_indx]
                       dict_asg_info_per_row["Rated Output(x10-6)"] = str(ASG_rated_output[ASG_type_indx])
                       
                       raw_sensor_data = dataframe_sensor.iloc[:,(column_num+1)]
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
                        
                       if((hash_file_number == "#0") and (asg_entry_num == 1)):
                            asg_processed_csv_data.to_csv('fwd_asg_processed_csv_data.csv', mode='a', index=False, header=True)
                       else:
                            asg_processed_csv_data.to_csv('fwd_asg_processed_csv_data.csv', mode='a', index=False, header=False)
                                
                    elif(sensor_type == "concrete"):
                        csg_entry_num = csg_entry_num + 1
                        dict_csg_info_per_row['Filename'] = process_filename[0]
                        csg_processed_csv_data = pd.DataFrame(csg_processed_data_col_names)
                        dict_csg_info_per_row["Concrete Strain Gage"]  = str(column_name[3:5].strip()) #CSG22 - #26 assignment; pick 22; strip() is to ensure no white spaces while picking strings like CSG1 - #5 assignment, "5 " is picked
                        CSG_type_indx = CSG_type.index(int(column_name[3:5].strip()))
                        dict_csg_info_per_row["Placement"] = str(CSG_placement[CSG_type_indx])
                        dict_csg_info_per_row["Lin Gage Fctr(inches/mV/V)"] = CSG_lin_gage_fctr[CSG_type_indx]
                        dict_csg_info_per_row["Poly Gage Fctr A"] = CSG_poly_gage_fctr_A[CSG_type_indx]
                        dict_csg_info_per_row["Poly Gage Fctr B"] = CSG_poly_gage_fctr_B[CSG_type_indx]
                        
                        raw_sensor_data = dataframe_sensor.iloc[:,(column_num+1)]
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
                        
                        if((hash_file_number == "#0") and (csg_entry_num == 1)):
                            csg_processed_csv_data.to_csv('fwd_csg_processed_csv_data.csv', mode='a', index=False, header=True)
                        else:
                            csg_processed_csv_data.to_csv('fwd_csg_processed_csv_data.csv', mode='a', index=False, header=False)
                    
                    elif(sensor_type == "press_cell"):
                        pc_entry_num = pc_entry_num + 1
                        dict_pc_info_per_row['Filename'] = process_filename[0]
                        pc_processed_csv_data = pd.DataFrame(pc_processed_data_col_names)
                        dict_pc_info_per_row["Pressure Cell"] = str(column_name[2]) #PC2 assignment; pick 2
                        PC_type_indx = PC_type.index(int(column_name[2]))
                        dict_pc_info_per_row["Lin Gage Fctr(kPa/mV)"] = PC_lin_gauge_fctr[PC_type_indx]
                        dict_pc_info_per_row["Poly Gage Fctr A"] = PC_poly_gage_fctr_A[PC_type_indx]
                        dict_pc_info_per_row["Poly Gage Fctr B"] = PC_poly_gage_fctr_B[PC_type_indx]
                        dict_pc_info_per_row["Poly Gage Fctr C"] = PC_poly_gage_fctr_C[PC_type_indx]
                        
                        raw_sensor_data = dataframe_sensor.iloc[:,(column_num+1)]
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
                        
                        if((hash_file_number == "#0") and (pc_entry_num == 1)):
                            pc_processed_csv_data.to_csv('fwd_pc_processed_csv_data.csv', mode='a', index=False, header=True)
                        else:
                            pc_processed_csv_data.to_csv('fwd_pc_processed_csv_data.csv', mode='a', index=False, header=False)
                    
                    elif(sensor_type == "thermo"):  
                        thermo_entry_num = thermo_entry_num + 1
                        thermo_processed_csv_data = pd.DataFrame(thermo_processed_data_col_names)
                        dict_thermo_info_per_row['Filename'] = process_filename[0]
                        dict_thermo_info_per_row["Thermocouple"] = str(column_name[14:16].strip()) #Thermocouple #19 assignme ; pick 19
                        
                        raw_sensor_data = dataframe_sensor.iloc[:,(column_num+1)]
                        seconds_max, data_points_max, seconds_min, data_points_min, filtered_data = find_extrema(sensor_type,raw_sensor_data,SecondsElapsed_sensor)
                        #plot_data(SecondsElapsed_sensor, seconds_max, data_points_max, seconds_min, data_points_min, filtered_data)
                        
                        dict_thermo_info_per_row['Extrema'] = "maxima"
                        for max_point_num in range(0,len(seconds_max)):
                            dict_thermo_info_per_row['SecondsElapsed'] = seconds_max[max_point_num]
                            dict_thermo_info_per_row['processed_datapoint'] = data_points_max[max_point_num]   
                            thermo_processed_csv_data = pd.concat([thermo_processed_csv_data, pd.DataFrame(dict_thermo_info_per_row,index=[0])], ignore_index=True)

                        dict_thermo_info_per_row['Extrema'] = "minima"
                        for min_point_num in range(0,len(seconds_min)):
                            dict_thermo_info_per_row[''] = seconds_min[min_point_num]
                            dict_thermo_info_per_row['processed_datapoint(F)'] = data_points_min[min_point_num]  
                            thermo_processed_csv_data = pd.concat([thermo_processed_csv_data, pd.DataFrame(dict_thermo_info_per_row,index=[0])], ignore_index=True)
                        
                        if((hash_file_number == "#0") and (thermo_entry_num == 1)):
                            thermo_processed_csv_data.to_csv('fwd_thermo_processed_csv_data.csv', mode='a', index=False, header=True)
                        else:
                            thermo_processed_csv_data.to_csv('fwd_thermo_processed_csv_data.csv', mode='a', index=False, header=False)
                
                    elif(sensor_type == "tacho"):
                        print("\t"+"skip")
                        '''
                        tacho_entry_num = tacho_entry_num + 1
                        tacho_processed_csv_data = pd.DataFrame(tacho_processed_csv_data)
                        dict_tacho_info_per_row['Filename'] = process_filename[0]
                        raw_sensor_data = np.array(dataframe_sensor.iloc[:,(column_num+1)])
                        #plt.plot(SecondsElapsed_sensor,raw_sensor_data)
                        #plt.show()
                        #tacho_indices = [x[0] for x in enumerate(raw_sensor_data) if x[1] > 0] 
                        print(len(raw_sensor_data))
                        for i in range(0,len(raw_sensor_data)): #all values are captured and stored in tachometer readings
                        #for i in tacho_indices: #tachometer readings are just 0 or 4; Here all values > 0 i.e. equal to 4 are taken; commented as unsure what is needed
                            print(i)
                            dict_tacho_info_per_row['SecondsElapsed'] = SecondsElapsed_sensor[i]
                            dict_tacho_info_per_row['processed_datapoint'] = raw_sensor_data[i]
                            tacho_processed_csv_data = pd.concat([tacho_processed_csv_data, pd.DataFrame(dict_tacho_info_per_row,index=[0])], ignore_index=True)
                            
                        if((hash_file_number == "#0") and (tacho_entry_num == 1)):
                            tacho_processed_csv_data.to_csv('fwd_tacho_processed_csv_data.csv', mode='a', index=False, header=True)
                        else:
                            tacho_processed_csv_data.to_csv('fwd_tacho_processed_csv_data.csv', mode='a', index=False, header=False)
                        '''
file_info_csv_data.to_csv('fwd_sensor_file_info.csv', mode='a', index=False, header=True)    
                        
                            
               
                