# command_handler.py

# Receives commands from the server and converts them into
# the same control packet Arduino code expects.

class CommandHandler:
    def __init__(self, arduino=None):
        self.arduino = arduino

        # This packet matches Arduino:
       
        self.control_packet = {
            "roverX": 512,
            "roverY": 512,
            "roverSW": False,

            "armX": 512,
            "armY": 512,
            "armSW": False
        }

    def handle_command(self, data):
        # data is the message received from the server

        command_type = data.get("type")

        if command_type == "drive":
            self.handle_drive_command(data)

        elif command_type == "arm":
            self.handle_arm_command(data)

        elif command_type == "mode":
            self.handle_mode_command(data)

        elif command_type == "stop":
            self.handle_stop_command()

        else:
            print(f"[CommandHandler] Unknown command type: {command_type}")

    def handle_drive_command(self, data):
        # roverX = left/right
        # roverY = forward/backward

        self.control_packet["roverX"] = data.get("roverX", 512)
        self.control_packet["roverY"] = data.get("roverY", 512)

        # roverSW = autonomous mode 
        self.control_packet["roverSW"] = data.get("roverSW", False)

        self.send_to_arduino()

    def handle_arm_command(self, data):
        # Updates robot arm joystick values
        # armX / armY control arm movement
        # armSW opens/closes the wrist

        self.control_packet["armX"] = data.get("armX", 512)
        self.control_packet["armY"] = data.get("armY", 512)
        self.control_packet["armSW"] = data.get("armSW", False)

        self.send_to_arduino()

    def handle_mode_command(self, data):
        # Used if the server sends a separate autonomous mode command

        autonomous = data.get("autonomous", False)

        # rover joystick button
        self.control_packet["roverSW"] = autonomous

        self.send_to_arduino()

        # Sets it back to false, so it behaves like a click
        self.control_packet["roverSW"] = False

    def handle_stop_command(self):
        # Centers all joystick values

        self.control_packet["roverX"] = 512
        self.control_packet["roverY"] = 512
        self.control_packet["roverSW"] = False

        self.control_packet["armX"] = 512
        self.control_packet["armY"] = 512
        self.control_packet["armSW"] = False

        self.send_to_arduino()

    def send_to_arduino(self):
        # Sends packet to Arduino
        # If Arduino isn't connected, print for test

        if self.arduino:
            self.arduino.send_command(self.control_packet)
        else:
            print(f"[CommandHandler] Arduino not connected: {self.control_packet}")