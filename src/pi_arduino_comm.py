import serial
import time

time_last_cmd_sent = time.time()

while True:
    try:
        ser = serial.Serial('/dev/ttyACM0', 115200, timeout=2.0)
        print("Successfully connected to Arduino Mega.")
        time.sleep(1)
        ser.reset_input_buffer()
        break
    except serial.SerialException:
        print("Could not connect to serial. Retrying in 1 second...")
        time.sleep(1)

try:
    while True:
        time.sleep(0.01)
        if ser.in_waiting > 0:
            msg = ser.readline().decode('utf-8').rstrip()
            print(msg)

        time_now = time.time()
        if time_now - time_last_cmd_sent > 1.0:
            time_last_cmd_sent = time_now
            ser.write("test\n".encode('utf-8'))
except KeyboardInterrupt:
    print("Closing serial communcation.")
    ser.close()
    print("Exit Program. ")
