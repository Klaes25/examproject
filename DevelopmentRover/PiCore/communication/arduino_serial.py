import serial
import serial.tools.list_ports
import time
import threading

# this is the class that handles talking to the arduino
class ArduinoSerial:

    def __init__(self, config):
        self.config = config
        self.ser = None  # the serial connection
        self.is_running = False
        self.sensor_data = {}  # store sensor readings here

        # needs a lock so threads dont fight over the data
        self.lock = threading.Lock()

    def connect(self):
        port = self.config.ARDUINO_PORT
        baud = self.config.ARDUINO_BAUD

        print(f"Connecting to Arduino on {port}...")

        try:
            # this opens the serial connection
            self.ser = serial.Serial(port, baud, timeout=1)

            time.sleep(2)

            self.ser.reset_input_buffer()
            self.is_running = True

            # start a thread that reads from arduino in the background
            t = threading.Thread(target=self.read_loop)
            t.daemon = True  # dies when main program dies
            t.start()

            print(f"Connected to Arduino on port {port} at {baud} baud.")
            return True

        except serial.SerialException as e:
            print(f"Error: Could not connect to Arduino - {e}")
            print("Available ports:")

            # show all ports so user knows what to pick
            ports = serial.tools.list_ports.comports()

            if len(ports) == 0:
                print("  No ports found. Is the Arduino plugged in?")

            for p in ports:
                print(f"  {p.device} - {p.description}")

            return False

    def disconnect(self):
        self.is_running = False

        if self.ser != None:
            if self.ser.is_open:
                self.ser.close()

        print("Disconnected from Arduino.")

    def is_connected(self):
        if self.ser == None:
            return False

        return self.ser.is_open

    # send a command to the arduino
        # send a command to the arduino
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

    # this runs in a thread and reads lines from arduino constantly
    def read_loop(self):
        print("Serial read loop started.")

        while self.is_running:

            try:
                if self.ser.in_waiting > 0:
                    raw = self.ser.readline()
                    line = raw.decode("utf-8").strip()

                    if line:  # ignore empty lines
                        self.parse_arduino_message(line)

            except serial.SerialException as e:
                print(f"Read error: {e}")
                print("Arduino disconnected. Attempting to reconnect...")

                time.sleep(self.config.SERIAL_RETRY_DELAY)
                self.connect()

            except Exception as e:
                pass

            time.sleep(0.01)  # small delay so we dont use 100% CPU

    def parse_arduino_message(self, line):
        parts = line.split(":")

        # check it's a sensor message
        if len(parts) >= 3 and parts[0] == "SENSOR":
            key = parts[1]
            val = parts[2]
            self.sensor_data[key] = val
        else:
            print(f"Arduino: {line}")

    # get a sensor value by name
    def get_sensor(self, key):

        if key in self.sensor_data:
            return self.sensor_data[key]

        return None  # not received yet

    def get_distance_cm(self):
        val = self.get_sensor("DIST")

        if val == None:
            return None

        try:
            return float(val)

        except:
            return None

    def get_temperature(self):
        val = self.get_sensor("TEMP")

        if val == None:
            return None

        try:
            return float(val)

        except:
            return None
        
    def get_humidity(self):
        val = self.get_sensor("HUM")

        if val == None:
            return None

        try:
            return float(val)

        except:
            return None
