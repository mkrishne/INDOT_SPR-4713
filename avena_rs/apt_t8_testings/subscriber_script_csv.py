import asyncio
import csv
from nats.aio.client import Client as NATS
import pyarrow as pa

async def run():
    # Connect to NATS
    nc = NATS()
    await nc.connect("nats://localhost:4222")

    async def message_handler(msg):
        subject = msg.subject
        data = msg.data
        channel_name = subject.split('.')[1]  # Assumes topic format "channel.channel_name"

        # Deserialize data using pyarrow
        reader = pa.ipc.open_stream(data)
        batch = reader.read_next_batch()
        
        # Prepare data for CSV
        timestamps = batch.column(0).to_pylist()
        values = batch.column(1).to_pylist()

        # Write to CSV file
        csv_filename = f"{channel_name}.csv"
        with open(csv_filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            for timestamp, value in zip(timestamps, values):
                writer.writerow([timestamp, value])
        
        print(f"Data written to {csv_filename}")

    # Subscribe to the topic and keep the subscription active
    await nc.subscribe("channel.*", cb=message_handler)

    try:
        # Keep the coroutine running indefinitely
        await asyncio.Future()  # This will block forever unless cancelled
    except KeyboardInterrupt:
        print("Received exit signal, shutting down...")
    finally:
        # Perform any cleanup here
        print("Closing NATS connection...")
        await nc.close()
        print("NATS connection closed.")

if __name__ == '__main__':
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("Program terminated by user.")
