import datetime
import sys
import csv
import keyboard

from labjack import ljm

handle8 = ljm.openS("ANY", "ANY", "My_T8")  
handle4 = ljm.openS("ANY", "ANY", "My_T4")  

info = ljm.getHandleInfo(handle8)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n"
      "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
      (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

info = ljm.getHandleInfo(handle4)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n"
      "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
      (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))
      
# Stream Configuration
aScanListNames_T8 = ["AIN0","AIN1","AIN2","AIN3","AIN4","AIN5","AIN6","AIN7"]  # Scan list names to stream
numAddresses_T8 = len(aScanListNames_T8)
aScanList_T8 = ljm.namesToAddresses(numAddresses_T8, aScanListNames_T8)[0]
scanRate_T8 = 40000
scansPerRead_T8 = int(scanRate_T8/numAddresses_T8) #5000 scans per read

# Stream Configuration
aScanListNames_T4 = ["AIN0","AIN1","AIN2","AIN3"]  # Scan list names to stream
numAddresses_T4 = len(aScanListNames_T4)
aScanList_T4 = ljm.namesToAddresses(numAddresses_T4, aScanListNames_T4)[0]
scanRate_T4 = 12000
scansPerRead_T4 = int(scanRate_T4/numAddresses_T4) #5000 scans per read

try:
    aNames_T4 = ["STREAM_SETTLING_US", "STREAM_RESOLUTION_INDEX"]
    aValues_T4 = [0, 0]
    numFrames_T4 = len(aNames_T4)
    ljm.eWriteNames(handle4, numFrames_T4, aNames_T4, aValues_T4)
    
    # Ensure triggered stream is disabled.
    ljm.eWriteName(handle8, "STREAM_TRIGGER_INDEX", 0)
    # Enabling internally-clocked stream.
    ljm.eWriteName(handle8, "STREAM_CLOCK_SOURCE", 0)

    # AIN0 and AIN1 ranges are +/-10 V and stream resolution index is
    # 0 (default).
    aNames_T8 = ["AIN0_RANGE", "AIN1_RANGE","AIN2_RANGE", "AIN3_RANGE","AIN4_RANGE", "AIN5_RANGE", "STREAM_RESOLUTION_INDEX"]
    aValues_T8 = [0.018,0.018,0.018,0.018,0.018,0.018,0.018,0.018,0]
    # stream settling time and stream resolution configuration.
    numFrames_T8 = len(aNames_T8)
    ljm.eWriteNames(handle8, numFrames_T8, aNames_T8, aValues_T8)

    # Configure and start stream
    scanRate_T4 = ljm.eStreamStart(handle4, scansPerRead_T4, numAddresses_T4, aScanList_T4, scanRate_T4)
    print("\nT4 Stream started with a scan rate of %0.0f Hz." % scanRate_T4)

    # Configure and start stream
    scanRate_T8 = ljm.eStreamStart(handle8, scansPerRead_T8, numAddresses_T8, aScanList_T8, scanRate_T8)
    print("\nT8 Stream started with a scan rate of %0.0f Hz." % scanRate_T8)
    
    totScans_T4 = 0
    totSkip_T4 = 0  # Total skipped samples

    totScans_T8 = 0
    totSkip_T8 = 0  # Total skipped samples
    i = 0
    
    # CSV file setup
    timestampFormat = "%Y-%m-%d %H:%M:%S.%f"
    # Correctly use datetime.datetime.now()
    t4_filename = f"T4_stream_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    t8_filename = f"T8_stream_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    with open(t4_filename, mode='w', newline='') as file_T4, \
         open(t8_filename, mode='w', newline='') as file_T8:

        writer_T4 = csv.writer(file_T4)
        writer_T8 = csv.writer(file_T8)

        # Write headers
        writer_T4.writerow(["Timestamp"] + aScanListNames_T4)
        writer_T8.writerow(["Timestamp"] + aScanListNames_T8)
        while True:
            if keyboard.is_pressed('q'):
                print("\nLogging stopped by user.")
                break
                
            ret4 = ljm.eStreamRead(handle4)
            aData4 = ret4[0]
            scans_T4 = len(aData4) / numAddresses_T4
            totScans_T4 += scans_T4
            curSkip_T4 = aData4.count(-9999.0)
            totSkip_T4 += curSkip_T4 
            print("\nlen data T4 %i" % len(aData4))
            ainStr4 = ""
            for j in range(0, numAddresses_T4):
                    ainStr4 += "%s = %0.5f, " % (aScanListNames_T4[j], aData4[j])
            print("  1st scan out of %i: %s" % (scans_T4, ainStr4))
            print(" T4 Scans Skipped = %0.0f, Scan Backlogs: Device = %i, LJM = "
                      "%i" % (curSkip_T4/numAddresses_T4, ret4[1], ret4[2]))
            
            for j in range(scansPerRead_T4):
                curTimeStr = datetime.datetime.now().strftime(timestampFormat)
                row_T4 = [curTimeStr] + aData4[j*numAddresses_T4:(j+1)*numAddresses_T4]
                writer_T4.writerow(row_T4)

            ret8 = ljm.eStreamRead(handle8)
            aData8 = ret8[0]
            scans_T8 = len(aData8) / numAddresses_T8
            totScans_T8 += scans_T8
            curSkip_T8 = aData8.count(-9999.0)
            totSkip_T8 += curSkip_T8 
            print("\nlen data T8 %i" % len(aData8))
            ainStr8 = ""
            for j in range(0, numAddresses_T8):
                    ainStr8 += "%s = %0.5f, " % (aScanListNames_T8[j], aData8[j])
            print("  1st scan out of %i: %s" % (scans_T8, ainStr8))
            print(" T8 Scans Skipped = %0.0f, Scan Backlogs: Device = %i, LJM = "
                      "%i" % (curSkip_T8/numAddresses_T8, ret8[1], ret8[2]))
                      
            print("\neStreamRead %i" % i) 
            
            for j in range(scansPerRead_T8):
                curTimeStr = datetime.datetime.now().strftime(timestampFormat)
                row_T8 = [curTimeStr] + aData8[j*numAddresses_T8:(j+1)*numAddresses_T8]
                writer_T8.writerow(row_T8)
            
            i += 1
except ljm.LJMError:
    ljme = sys.exc_info()[1]
    print(ljme)
except Exception:
    e = sys.exc_info()[1]
    print(e)

# Close handle
ljm.close(handle8)
ljm.close(handle4)