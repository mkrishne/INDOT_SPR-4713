import asyncio
import pyarrow as pa
import pyarrow.ipc as ipc
from nats.aio.client import Client as NATS

async def run():
    # Connect to NATS
    nc = NATS()
    await nc.connect("nats://localhost:4222")

    async def message_handler(msg):
        subject = msg.subject
        data = msg.data
        channel_name = subject.split('.')[1]  # Assumes topic format "channel.channel_name"

        # Deserialize data using PyArrow
        reader = ipc.open_stream(data)
        batch = reader.read_next_batch()

        # Convert batch to an Arrow Table
        table = pa.Table.from_batches([batch])

        # Define the filename
        pa_filename = f"{channel_name}.pa"

        # Write the Arrow Table to a .pa file
        with pa.OSFile(pa_filename, 'wb') as f:
            with ipc.new_file(f, table.schema) as writer:
                writer.write_table(table)

        print(f"Data written to {pa_filename}")

    # Subscribe to the topic and keep the subscription active
    await nc.subscribe("channel.*", cb=message_handler)

    try:
        # Keep the coroutine running indefinitely
        await asyncio.Future()  # This will block forever unless cancelled
    except KeyboardInterrupt:
        print("Received exit signal, shutting down...")
    finally:
        # Perform cleanup
        print("Closing NATS connection...")
        await nc.close()
        print("NATS connection closed.")

if __name__ == '__main__':
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("Program terminated by user.")
