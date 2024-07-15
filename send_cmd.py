import serial
import time

SERIAL_PORT = 'COM5'
BAUD_RATE = 115200
TIMEOUT = 1  # Timeout for reading from the serial port

def send_command(cmd,ser):
    # Open the serial port

        # Write the cmd to the serial port
        print(f"Sending cmd: {cmd}")
        ser.write(cmd.encode("ascii"))  # Send the character encoded

        response = ""
        while True:
            if ser.in_waiting > 0:
                char = ser.read().decode("ascii")
                if char == '\n':
                    print(response)
                    break

                response += char

if __name__ == "__main__":
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT) as ser:
        time.sleep(2)
        print("in main")
        while(1):
            cmd = '1R0!\n'  # Change this to the character you want to send ('a', '0', '1', '2', etc.)
            send_command(cmd,ser)
