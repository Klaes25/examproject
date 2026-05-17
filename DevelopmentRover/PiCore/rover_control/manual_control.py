# Creates joystick-style command dictionaries for rover control.
# These commands are sent through command_handler.py to the Arduino.

class ManualControl:
    CENTER = 512
    MIN_VALUE = 0
    MAX_VALUE = 1023

    def create_drive_command(self, direction: str, speed: int = 1023):
        speed = max(self.MIN_VALUE, min(self.MAX_VALUE, speed))

        command = {
            "type": "drive",
            "roverX": self.CENTER,
            "roverY": self.CENTER,
            "roverSW": False
        }

        if direction == "forward":
            command["roverY"] = speed

        elif direction == "backward":
            command["roverY"] = self.MIN_VALUE

        elif direction == "left":
            command["roverX"] = self.MIN_VALUE

        elif direction == "right":
            command["roverX"] = self.MAX_VALUE

        elif direction == "stop":
            command["roverX"] = self.CENTER
            command["roverY"] = self.CENTER

        return command

    def create_arm_command(self, arm_x=512, arm_y=512, wrist_button=False):
        return {
            "type": "arm",
            "armX": arm_x,
            "armY": arm_y,
            "armSW": wrist_button
        }

    def toggle_autonomous(self):
        # simulates rover joystick
        # Arduino uses roverSW to toggle autonomous mode.
        return {
            "type": "drive",
            "roverX": self.CENTER,
            "roverY": self.CENTER,
            "roverSW": True
        }

    def stop(self):
        return {
            "type": "stop"
        }