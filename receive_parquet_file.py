import asyncio
import nats
import pandas as pd
from pyarrow import parquet as pq
import pyarrow as pa

async def main():
    # Function to handle incoming messages
    async def message_handler(msg):
        subject = msg.subject
        data = msg.data

        # Assuming the data is binary for a Parquet file
        print(f"Received message on '{subject}' with {len(data)} bytes")

        # Writing the data to a temporary Parquet file
        temp_filename = 'received_temp.parquet'
        with open(temp_filename, 'wb') as f:
            f.write(data)

        # Reading the first 10 lines of the Parquet file
        table = pq.read_table(temp_filename)
        df = table.to_pandas()
        print(df.head(10))

    # Connect to NATS server running on localhost
    nc = await nats.connect("nats://localhost:4222")

    # Subscribe to the subject 'test' with the above message handler
    await nc.subscribe("test", cb=message_handler)

    # Keep the subscription open
    await asyncio.Future()  # This line keeps the event loop running indefinitely

if __name__ == '__main__':
    asyncio.run(main())
