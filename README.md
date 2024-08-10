# Color-Based Object Tracking GUI

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/username/color-based-object-tracking-gui)

## Overview

The **Color-Based Object Tracking GUI** is a Python-based application designed to facilitate real-time detection and tracking of objects in video streams based on their color. Originally developed to track an orange ball and a robot, the application offers flexibility to be adapted for various color-based tracking needs. With an intuitive graphical user interface (GUI) built using PyQt5, users can easily load videos, adjust tracking parameters, and visualize the tracking process.

### Key Features

- **Video Loading and Processing:** Seamlessly load video files into the application for object detection and tracking.
- **Real-Time Tracking:** Track an orange ball and a robot in real-time as they move within video frames.
- **Customizable Parameters:** Fine-tune tracking parameters, such as color range, object size thresholds, and tracking speed to optimize performance.
- **User-Friendly Controls:** Start, pause, reset video playback, and select colors for tracking with simple and accessible buttons.
- **Visual Tracking Feedback:** Overlay tracking results directly onto the video, including trajectory lines and detection markers for easy monitoring.

### GUI Preview

Below is a screenshot of the application's main interface, showcasing the clean and intuitive design:

![Tracking Interface] ![image](https://github.com/user-attachments/assets/dd8bca3a-7d9b-4938-aa6e-d0b483b1520c)


### Installation (For Developers and Advanced Users)

#### Prerequisites

Ensure your system has the following versions installed:

- **Python**: 3.11.9
- **pip**: 24.1.2

The application also depends on several Python libraries:

- **PyQt5** (v5.15.10) - Used to build the GUI.
- **OpenCV** (v4.10.0.84) - Provides the core functionality for video processing and object detection.
- **NumPy** (v1.26.4) - Facilitates efficient numerical operations and array handling.

#### Setup Instructions

Follow these steps to set up the application on your local machine:

1. **Clone the Repository:**

   Clone the repository using Git:

   ```bash
   git clone https://github.com/username/color-based-object-tracking-gui.git
   cd color-based-object-tracking-gui
   
2. **Install Dependencies**
   Install the necessary Python packages using pip:
    ```bash
   pip install -r requirements.txt
   
4. **Launching the Application:**
   Start the application by running the main Python script:
   ```bash
   python main.py
   
### Using the Pre-Built Application
For users who prefer not to install Python or any dependencies, a pre-built version of the application is available. 
This version does not require any additional setup; simply download and run the application

To obtain the pre-built application:
1.  Contact Us: Reach out via GitHub at username or via email at ahmadnurimam19@gmail.com.
2.  Access Instructions: Upon contacting us, you will receive a .rar file containing the application along with the password to ensure secure access.

### Roadmap
We have a range of enhancements planned to further develop the application, including:
   - Support for Multiple Object Tracking: Expanding the application to track multiple objects with different colors simultaneously.
   - Integration of Machine Learning Models: Enhancing object detection accuracy by integrating advanced machine learning techniques.
   - Data Export Features: Adding capabilities to export tracking data for further analysis in external tools.

### Contributing
We welcome contributions from the community! If you have ideas for new features, improvements, or bug fixes, feel free to submit an issue or pull request. Please refer to our CONTRIBUTING.md for guidelines on how to contribute effectively to the project.

### License
This project is licensed under the MIT License. For more details, see the LICENSE.md file.

### Acknowledgments
We extend our gratitude to the open-source community for providing the essential libraries and tools that made this project possible. Special thanks to all contributors for their efforts in enhancing this application.

