import serial
import serial.tools.list_ports
import time
import threading

class ArduinoSerial:

    def __init__(self, config):
        self.config = config
        self.ser = None
        self.is_running = False
        self.sensor_data = {}
        self.lock = threading.Lock()

    def connect(self):
        port = self.config.SERIAL_PORT
        baud = self.config.SERIAL_BAUDRATE

        print(f"Connecting to Arduino on {port}...")

        try:
            self.ser = serial.Serial(port, baud, timeout=1)
            time.sleep(2)
            self.ser.reset_input_buffer()
            self.is_running = True

            t = threading.Thread(target=self.read_loop)
            t.daemon = True
            t.start()

            print(f"Connected to Arduino on port {port} at {baud} baud.")
            return True

        except serial.SerialException as e:
            print(f"Error: Could not connect to Arduino - {e}")
            print("Available ports:")
            ports = serial.tools.list_ports.comports()
            if len(ports) == 0:
                print("  No ports found. Is the Arduino plugged in?")
            for p in ports:
                print(f"  {p.device} - {p.description}")
            return False

    def disconnect(self):
        self.is_running = False
        if self.ser is not None:
            if self.ser.is_open:
                self.ser.close()
        print("Disconnected from Arduino.")

    def is_connected(self):
        if self.ser is None:
            return False
        return self.ser.is_open

    def send_command(self, packet):
        if not self.is_connected():
            print("Warning: Tried to send command but Arduino is not connected.")
            return False

        try:
            message = (
                f"CONTROL:"
                f"{packet['roverX']},"
                f"{packet['roverY']},"
                f"{int(packet['roverSW'])},"
                f"{packet['armX']},"
                f"{packet['armY']},"
                f"{int(packet['armSW'])}\n"
            )

            with self.lock:
                self.ser.write(message.encode())

            print(f"Sent to Arduino: {message.strip()}")
            return True

        except Exception as e:
            print(f"Send error: {e}")
            return False

    def read_loop(self):
        print("Serial read loop started.")
        while self.is_running:
            try:
                if self.ser.in_waiting > 0:
                    raw = self.ser.readline()
                    line = raw.decode("utf-8").strip()

                    if line:
                        self.parse_arduino_message(line)

            except serial.SerialException as e:
                print(f"Read error: {e}")
                print("Arduino disconnected. Attempting to reconnect...")
                time.sleep(self.config.RECONNECT_DELAY)
                self.connect()
                break  

            except Exception as e:
                pass

            time.sleep(0.01)

    def parse_arduino_message(self, line):
        parts = line.split(":")

        if len(parts) >= 3 and parts[0] == "SENSOR":
            key = parts[1]
            val = parts[2]
            self.sensor_data[key] = val
        else:
            print(f"Arduino: {line}")

    def get_sensor(self, key):
        if key in self.sensor_data:
            return self.sensor_data[key]
        return None

    def get_distance_cm(self):
        val = self.get_sensor("DIST")
        if val is None:
            return None
        try:
            return int(val)
        except:
            return None

    def get_temperature(self):
        val = self.get_sensor("TEMP")
        if val is None:
            return None
        try:
            return float(val)
        except:
            return None
