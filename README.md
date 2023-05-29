# Fault Detection System with MPS 500

The Fault Detection System with MPS 500 is a project aimed at monitoring and controlling various stations in an automated production line. The system utilizes Programmable Logic Controllers (PLCs) and incorporates image processing techniques to ensure accurate particle placement. The project's code is available on GitHub and provides an efficient and reliable solution for fault detection in industrial settings.

## Overview

The Fault Detection System consists of multiple stations, including a handling station, a processing station, a distribution station, and a testing station. Each station is connected to a dedicated PLC, and the system uses the Snap7 library for communication between the PLCs. Additionally, a camera is employed to capture video from the production line, and OpenCV is utilized for image processing tasks.

The key functionalities of the Fault Detection System include:

1. **Handling Station**: Reads data from a hand PLC and writes it to a slave PLC.
2. **Processing Station**: Reads data from a proc PLC and writes it to a slave PLC.
3. **Distribution Station**: Reads data from a dist PLC and writes it to a slave PLC.
4. **Testing Station**: Reads data from a test PLC and writes it to a slave PLC.
5. **Image Processing**: The system captures frames from a camera and allows the user to select a region of interest (ROI) on the video feed. Image processing techniques are applied to the ROI to filter out specific colors (red in this case) and detect contours. The system calculates the distance between the fixed center (initially set by the user) and the center of the detected particle. Based on the distance, the system updates the PLCs to indicate whether a particle is present or not.

The Fault Detection System provides real-time monitoring and control of the production line, enabling efficient fault detection and ensuring accurate placement of particles. By combining PLC communication and image processing capabilities, the system offers a comprehensive solution for industrial fault detection applications.
