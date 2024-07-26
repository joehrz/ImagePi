# ImagePi

**ImagePi** is a Python-based Raspberry Pi camera system designed for capturing and managing plant images. This project allows users to control cameras connected to a Raspberry Pi, capture images, and transfer them for inspection and analysis.

## Features

- Capture images using multiple cameras connected to a Raspberry Pi.
- Transfer captured images to a specified directory.
- Inspect captured images through a graphical user interface (GUI).
- Reset the system in case of failures.

## Requirements

### Main System

- Python 3.x
- Required Python packages (listed in `main_system/requirements.txt`)

### Raspberry Pi

- Raspberry Pi with camera(s) attached
- Python 3.x
- Required Python packages (listed in `raspberry_pi/requirements.txt`)
- Additional packages: `libcamera-apps`, `RPi.GPIO`, `wiringpi`

## Installation

### Main System

1. Clone the repository:

    ```bash
    git clone https://github.com/Dxxc/ImagePi.git
    cd ImagePi
    ```

2. Create a virtual environment (optional but recommended):

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:

    ```bash
    pip install -r main_system/requirements.txt
    ```

### Raspberry Pi

1. Ensure your Raspberry Pi is up to date:

    ```bash
    sudo apt-get update
    sudo apt-get upgrade
    ```

2. Install the required packages:

    ```bash
    sudo apt-get install -y python3 python3-pip python3-rpi.gpio libcamera-apps wiringpi
    sudo apt install -y python3-kms++ python3-libcamera python3-pyqt5 python3-prctl libatlas-base-dev ffmpeg
    sudo pip3 install numpy --upgrade
    sudo pip3 install picamera2
    ```

    These instructions are adapted from the [ArduCAM RaspberryPi repository](https://github.com/ArduCAM/RaspberryPi.git). See this repository for more details.

3. Add support for Pi 4B (if applicable):

    ```bash
    cd /tmp
    wget https://project-downloads.drogon.net/wiringpi-latest.deb
    sudo dpkg -i wiringpi-latest.deb
    ```

4. Deploy the Raspberry Pi code:

    ```bash
    ./deploy_to_pi.sh
    ```
## Usage

### Main System

1. Ensure your Raspberry Pi is connected to the network and the cameras are properly set up.
2. Run the `gui.py` script to launch the application:

    ```bash
    python main_system/gui.py
    ```

3. Use the GUI to configure camera settings, capture images, inspect images, and reset the system if necessary.

### Raspberry Pi

1. Navigate to the deployment directory:

    ```bash
    cd ~/ImagePi
    ```

2. Run the camera control script:

    ```bash
    python3 camera_control.py <image_folder>
    ```

## Configuration

Configuration settings are managed through a JSON file (`params.json`). You can update this file directly or use the GUI to modify settings.

## File Structure

```plaintext
ImagePi/
├──README.md
├──deploy_to_pi.sh
│
├── main_system/
│   ├── gui.py
│   ├── network.py
│   ├── credentials.py
│   ├── config.py
│   ├── imagecapture.py
│   ├── params.json
│   ├── requirements.txt
│   
│
└── raspberry_pi/
    ├── camera_control.py
    ├── params.json



