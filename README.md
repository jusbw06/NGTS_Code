# Replica Missile System Code

This repository contains the code I used when creating the NGTS missile replica. There were three devices which needed to be programmed seperately yet communicate with one another. They are as folows:
- Jetson Nano (`JetsonDevice`): This is a single board computer with the GPU glued to it. It was used to run a Jetson inference object detection neural network which would relay coordinates to the sensor control hub to control servo movement.
- Control Panel (`ControlDevice`): This device comprised of a raspberry pi 2 and an led touchscreen. Using the `guizero` library, I built a simple gui capable of controlling the movements of the missile replica by communicating wirelessly with the other two devices.
- Sensor Control Hub (`SensorControlDevice`): This device was a raspberry pi zero that fit inside of the small missile replica and as was responsible for reading in information from and controlling all of the systems internal sensors, including motor drivers, an IMU, and current & voltage sensors.


