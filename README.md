# examproject
Full stack project for our 2. semester exam. A physical rover that is controlled over the network via a web interface.

The rover has two brains. The motors and sensors runs on an Arduino Uno, and the camera, vision and communication runs on the Raspberry Pi 3. We've set up a backend server and a frontend for manual control via WASD and a live video feed. The video feed won't be archived, but the sensor data such as temperature and distance will be archived, which is handled by the backend.

## Structure
![Block diagram](rover_blokdiagram.png)

## Sources (source for code goes)
Links to tutorials, documentation or stackoverflow posts we used