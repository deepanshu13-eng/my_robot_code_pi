import serial
import time


class ArduinoConnection:
    def __init__(self, port='/dev/ttyACM0', logger=None, baudrate=115200):
        self.port = port
        self.logger = logger
        self.baudrate = baudrate
        self.ser = None
        self.connect()

    def connect(self):
        while True:
            try:
                self.ser = serial.Serial(self.port, self.baudrate, timeout=2.0)
                self.logger.info(f"✅ Connected to Arduino. Port:{self.port}")
                time.sleep(2)
                self.ser.reset_input_buffer()
                return
            except serial.SerialException:
                self.logger.error(f"❌ Arduino not found on port:{self.port}. Retrying in 2 sec...")
                time.sleep(2)

    def readline(self):
        try:
            if self.ser is None or not self.ser.is_open:
                return None

            return self.ser.readline()
        except (serial.SerialException, OSError) as e:
            self.logger.error(f"Serial error: {e}")
            if self.ser:
                try:
                    self.ser.close()
                except:
                    pass
            
            self.ser = None
            self.logger.warn("⚠️ Arduino disconnected! Reconnecting...")
            return None

    

