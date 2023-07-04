import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
from scipy.signal import savgol_filter
import glob
import os

Sensor_Types = ["Asphalt Strain Gage 7","Asphalt Strain Gage 6", "Asphalt Strain Gage 5", "Asphalt Strain Gage 4", "Asphalt Strain Gage 3", "Asphalt Strain Gage 2", \
            "Asphalt Strain Gage 1", "Concrete Strain Gage 25", "Concrete Strain Gage 24", "Concrete Strain Gage Pressure23", "Concrete Strain Gage 22", "Concrete Strain Gage 21", \
             "Pressure Cell 1", "Pressure Cell 2", "Thermocouple 12"]
Placement = [36,35,34,33,32,31,30,29,28,27,26,25,"","",""]
captured_instance = ["first20", "last20"]

Raw_data_files_folder = 'Asphalt Traffic Testing\Sensors (First and Last 20 Passes)'
main_dir = os.getcwd()
os.chdir(Raw_data_files_folder)
raw_data_files = glob.glob('*.txt')
#print(raw_data_files)
os.chdir(main_dir)

dataframe_meta_data = pd.read_csv(r"meta_data.csv")
meta_data_column_names = dataframe_meta_data.columns.values.tolist()
processed_data_column_names = [*meta_data_column_names[:-1], "Filename", "Captured instance", "Sensor_type", "placement", "Extrema", "SecondsElapsed", "processed_datapoint",meta_data_column_names[-1] ]
print(processed_data_column_names)

processed_data_column_names = {processed_data_column_names[i]: [] for i in range(0, len(processed_data_column_names))}
processed_csv_data = pd.DataFrame(processed_data_column_names)

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
    files_of_day = [i for i in raw_data_files if day_string in i]
    for file_num in range(0,len(files_of_day)):
        print(files_of_day[file_num])
        meta_data_of_day = dataframe_meta_data.loc[dataframe_meta_data['Day'] == day]
        #notes_of_day = meta_data_of_day['Notes']
        #meta_data_of_day = meta_data_of_day[meta_data_of_day.columns[:-1]]
        meta_data_of_day['Filename'] = files_of_day[file_num]
        meta_data_of_day['Captured instance'] = captured_instance[file_num] #there is one to one mapping between two files of a day and "F20"&"L20"
        file_to_process = Raw_data_files_folder + "\\" + files_of_day[file_num]
        #print(file_to_process)
        dataframe_sensor = pd.read_csv(file_to_process, skiprows=3 , delimiter = '\t')
        SecondsElapsed_sensor  = np.array(dataframe_sensor.iloc[:,0])
        for sensor_num in range(0,len(Sensor_Types)):
            print(Sensor_Types[sensor_num])
            meta_data_of_day['Sensor_type'] = Sensor_Types[sensor_num]
            meta_data_of_day['placement'] = Placement[sensor_num]
            meta_data_of_day['Extrema'] = "maxima"
            meta_data_of_day['SecondsElapsed'] = 0.0
            meta_data_of_day['processed_datapoint'] = 0.0
            
            raw_sensor_data = dataframe_sensor.iloc[:,(sensor_num+1)]
            sensor_full_name = Sensor_Types[sensor_num]
            #a if a < b else b
            sensor_type = "asphalt" if "Asphalt" in sensor_full_name else "concrete" if "Concrete" in sensor_full_name else "press_cell" if "Pressure" in sensor_full_name else "thermo"
            seconds_max, data_points_max, seconds_min, data_points_min, filtered_data = find_extrema(sensor_type,raw_sensor_data,SecondsElapsed_sensor)
            
            plot_data(SecondsElapsed_sensor, seconds_max, data_points_max, seconds_min, data_points_min, filtered_data)
            
            for max_point_num in range(0,len(seconds_max)):
                meta_data_of_day['SecondsElapsed'] = seconds_max[max_point_num]
                meta_data_of_day['processed_datapoint'] = data_points_max[max_point_num]   
                meta_data_of_day_dict = meta_data_of_day.to_dict('list')                
                processed_csv_data = pd.concat([processed_csv_data, pd.DataFrame(meta_data_of_day_dict)], ignore_index=True)

                
            meta_data_of_day['Extrema'] = "minima"
            
            for min_point_num in range(0,len(seconds_min)):
                meta_data_of_day['SecondsElapsed'] = seconds_min[min_point_num]
                meta_data_of_day['processed_datapoint'] = data_points_min[min_point_num]  
                meta_data_of_day_dict = meta_data_of_day.to_dict('list')                  
                processed_csv_data = pd.concat([processed_csv_data, pd.DataFrame(meta_data_of_day_dict)], ignore_index=True)

processed_csv_data.to_csv("processed_data2.csv")

'''       
dataframe_asphalt = pd.read_csv(r"Asphalt Traffic Testing\Sensors (First and Last 20 Passes)\test.txt", skiprows=3 , delimiter = '\t')


SecondsElapsed_asphalt  = dataframe_asphalt.iloc[:,0]
ASG7 = dataframe_asphalt.iloc[:,15]

#ASG7 = savgol_filter(ASG7, 100, 3) #window size 1000 selected by trial and error

#minima = elastic_recovery + lower_peaks
max_value = ASG7.max(axis=0)
min_value = ASG7.min(axis=0)
average_value = (min_value + max_value)/2
peaks, _ = find_peaks(ASG7, height=average_value,distance=10000)
bases, _ = find_peaks(-1*ASG7, height= -1*average_value,distance=10000)

ASG7_bases_minima = ASG7[bases]
SecondsElapsed_bases_minima = np.array(SecondsElapsed_asphalt[bases])

bases_lower_peaks, _ = find_peaks(-1*ASG7_bases_minima, height=None)
ASG7_elastic_recovery = np.delete(ASG7_bases_minima,bases_lower_peaks)
SecondsElapsed_elastic_recovery = np.delete(SecondsElapsed_bases_minima,bases_lower_peaks)

#plt.plot(SecondsElapsed_asphalt,ASG7_main)
plt.plot(SecondsElapsed_asphalt,ASG7)
plt.plot(SecondsElapsed_asphalt[peaks],ASG7[peaks], "x")
plt.plot(SecondsElapsed_elastic_recovery,ASG7_elastic_recovery, "r+")
plt.show()
'''

#************************************************************************************************************************
#************************************************************************************************************************
'''
dataframe_laser = pd.read_csv(r"Asphalt Traffic Testing\Laser Profile\Traffic D1 07-07-22\F20\test_laser.txt", delimiter = '\t')

SecondsElapsed_laser  = dataframe_laser.iloc[:,0]
laser_reading_raw = dataframe_laser.iloc[:,1]
laser_reading = savgol_filter(laser_reading_raw, 1000, 3) #window size 1000 selected by trial and error

peaks, _ = find_peaks(laser_reading, height=None)
bases, _ = find_peaks(-1*laser_reading, height=None,distance=100)
laser_reading_bases_minima = laser_reading[bases]
SecondsElapsed_bases_minima = np.array(SecondsElapsed_laser[bases])

plt.plot(SecondsElapsed_laser,laser_reading_raw)
plt.plot(SecondsElapsed_laser,laser_reading)
plt.plot(SecondsElapsed_laser[peaks],laser_reading[peaks], "x")
plt.plot(SecondsElapsed_bases_minima,laser_reading_bases_minima, "r+")
plt.show()
'''
#************************************************************************************************************************
#************************************************************************************************************************

'''
dataframe_concrete = pd.read_csv(r"Concrete Traffic Testing\Concrete Traffic Testing\D1 F20 09-16.txt", skiprows=3 , delimiter = '\t')

SecondsElapsed_concrete  = dataframe_concrete.iloc[:,0]
CSG = dataframe_concrete.iloc[:,1]
CSG1 = savgol_filter(CSG, 1000, 3) #window size 1000 selected by trial and error
CSG2 = savgol_filter(CSG1, 100, 3) #window size 1000 selected by trial and error

#plt.plot(SecondsElapsed_concrete,CSG)
plt.plot(SecondsElapsed_concrete,CSG1)
plt.show()
plt.plot(SecondsElapsed_concrete,CSG2)
plt.show()
'''

'''
#CSG = savgol_filter(CSG, 1000, 3) #window size 1000 selected by trial and error

#minima = elastic_recovery + lower_peaks
max_value = CSG.max(axis=0)
min_value = CSG.min(axis=0)
average_value = (min_value + max_value)/2
peaks, _ = find_peaks(CSG, height=average_value,distance=10000)
bases, _ = find_peaks(-1*CSG, height=None,distance=10000)

CSG_bases_minima = CSG[bases]
SecondsElapsed_bases_minima = np.array(SecondsElapsed_concrete[bases])

bases_lower_peaks, _ = find_peaks(-1*CSG_bases_minima, height=None)
CSG_elastic_recovery = np.delete(CSG_bases_minima,bases_lower_peaks)
SecondsElapsed_elastic_recovery = np.delete(SecondsElapsed_bases_minima,bases_lower_peaks)

plt.plot(SecondsElapsed_concrete,CSG)
plt.plot(SecondsElapsed_concrete[peaks],CSG[peaks], "x")
plt.plot(SecondsElapsed_elastic_recovery,CSG_elastic_recovery, "r+")
plt.show()
'''