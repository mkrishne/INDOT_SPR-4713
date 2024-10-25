import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.feather as feather
import datetime
import os
import sys
import asyncio
import nats
from labjack import ljm

async def main():
    # Open the T7 LabJack
    handle7 = ljm.openS("ANY", "ANY", "My_T7")
    info = ljm.getHandleInfo(handle7)
    print("Opened a LabJack with Device type: {}, Connection type: {}, Serial number: {}, IP address: {}, Port: {}, Max bytes per MB: {}".format(
        info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

    # Stream Configuration
    aScanListNames_T7 = ["AIN0", "AIN1", "AIN2", "AIN3"]
    numAddresses_T7 = len(aScanListNames_T7)
    aScanList_T7 = ljm.namesToAddresses(numAddresses_T7, aScanListNames_T7)[0]
    scanRate_T7 = 20000
    scansPerRead_T7 = int(scanRate_T7 / numAddresses_T7)

    # Prepare Arrow structures
    fields = [pa.field("Timestamp", pa.string())] + [pa.field(name, pa.float64()) for name in aScanListNames_T7]
    schema = pa.schema(fields)
    record_batches = []

    try:
        # Stream settings
        ljm.eWriteNames(handle7, len(["STREAM_SETTLING_US", "STREAM_RESOLUTION_INDEX"]), ["STREAM_SETTLING_US", "STREAM_RESOLUTION_INDEX"], [0, 0])
        ljm.eWriteName(handle7, "STREAM_TRIGGER_INDEX", 0)
        ljm.eWriteName(handle7, "STREAM_CLOCK_SOURCE", 0)
        ljm.eWriteNames(handle7, len(aScanListNames_T7), ["AIN{}_RANGE".format(i) for i in range(len(aScanListNames_T7))], [10.0] * len(aScanListNames_T7))

        # Start stream
        scanRate_T7 = ljm.eStreamStart(handle7, scansPerRead_T7, numAddresses_T7, aScanList_T7, scanRate_T7)
        print("Stream started with a scan rate of {:.0f} Hz.".format(scanRate_T7))

        # Collect data
        i = 0
        while i < 10:
            ret7 = ljm.eStreamRead(handle7)
            aData7 = ret7[0]
            scans_T7 = int(len(aData7) / numAddresses_T7)

            timestamp_strs = [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f") for _ in range(scansPerRead_T7)]
            batch_data = [pa.array(timestamp_strs, pa.string())] + [pa.array(aData7[j::numAddresses_T7], pa.float64()) for j in range(numAddresses_T7)]
            batch = pa.RecordBatch.from_arrays(batch_data, schema=schema)
            record_batches.append(batch)

            i += 1

        # Create Arrow Table from batches
        table = pa.Table.from_batches(record_batches)

        # Save to Parquet
        parquet_filename = "T7_stream_{}.parquet".format(datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
        pq.write_table(table, parquet_filename)
        print("Parquet file size: {} bytes".format(os.path.getsize(parquet_filename)))

        # Save to Feather
        feather_filename = "T7_stream_{}.feather".format(datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
        feather.write_feather(table, feather_filename)
        print("Feather file size: {} bytes".format(os.path.getsize(feather_filename)))

        # Save to Apache Arrow
        arrow_filename = "T7_stream_{}.arrow".format(datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
        with pa.OSFile(arrow_filename, 'wb') as sink:
            with pa.RecordBatchFileWriter(sink, table.schema) as writer:
                writer.write_table(table)
        print("Arrow file size: {} bytes".format(os.path.getsize(arrow_filename)))

        # Publish Parquet file to NATS
        await publish_file_to_nats(parquet_filename)

    except ljm.LJMError as e:
        print(e)
    except Exception as e:
        print(e)
    finally:
        ljm.close(handle7)

async def publish_file_to_nats(filename):
    # Connect to NATS
    nc = await nats.connect("nats://localhost:4222")

    # Read file data
    with open(filename, 'rb') as file:
        file_data = file.read()

    # Publish file data
    await nc.publish("test", file_data)
    print(f"Published {len(file_data)} bytes to 'test'")

    # Close the connection
    await nc.close()

if __name__ == '__main__':
    asyncio.run(main())
