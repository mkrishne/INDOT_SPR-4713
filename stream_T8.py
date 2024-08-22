import datetime
import sys
import os
import csv

from labjack import ljm

# Open the T8 LabJack using the specific IP address
handle8 = ljm.openS("T8", "TCP", "172.31.0.113")

info = ljm.getHandleInfo(handle8)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n"
      "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
      (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

# Stream Configuration for T8
aScanListNames_T8 = ["AIN0", "AIN1", "AIN2", "AIN3", "AIN4", "AIN5", "AIN6", "AIN7"]  # Scan list names to stream
numAddresses_T8 = len(aScanListNames_T8)
aScanList_T8 = ljm.namesToAddresses(numAddresses_T8, aScanListNames_T8)[0]
scanRate_T8 = 40000
scansPerRead_T8 = int(scanRate_T8 / numAddresses_T8)  # 5000 scans per read

# Ensure the stream_log directory exists
log_dir = "stream_log"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# CSV file setup
timestampFormat = "%Y-%m-%d %H:%M:%S.%f"
t8_filename = os.path.join(log_dir, f"T8_stream_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

try:
    # Stream settling time and resolution configuration for T8
    aNames_T8 = ["AIN0_RANGE", "AIN1_RANGE", "AIN2_RANGE", "AIN3_RANGE", "AIN4_RANGE", "AIN5_RANGE", "AIN6_RANGE", "AIN7_RANGE", "STREAM_RESOLUTION_INDEX"]
    aValues_T8 = [0.018, 0.018, 0.018, 0.018, 0.018, 0.018, 0.018, 0.018, 0]
    numFrames_T8 = len(aNames_T8)
    ljm.eWriteNames(handle8, numFrames_T8, aNames_T8, aValues_T8)

    # Ensure triggered stream is disabled and clock source is internal
    ljm.eWriteName(handle8, "STREAM_TRIGGER_INDEX", 0)
    ljm.eWriteName(handle8, "STREAM_CLOCK_SOURCE", 0)

    # Start stream for T8
    scanRate_T8 = ljm.eStreamStart(handle8, scansPerRead_T8, numAddresses_T8, aScanList_T8, scanRate_T8)
    print("\nT8 Stream started with a scan rate of %0.0f Hz." % scanRate_T8)

    totScans_T8 = 0
    totSkip_T8 = 0  # Total skipped samples
    i = 0

    with open(t8_filename, mode='w', newline='') as file_T8:
        writer_T8 = csv.writer(file_T8)

        # Write headers
        writer_T8.writerow(["Timestamp"] + aScanListNames_T8)
        
        while True:
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
                  "%i" % (curSkip_T8 / numAddresses_T8, ret8[1], ret8[2]))

            for j in range(scansPerRead_T8):
                curTimeStr = datetime.datetime.now().strftime(timestampFormat)
                row_T8 = [curTimeStr] + aData8[j * numAddresses_T8:(j + 1) * numAddresses_T8]
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
