# ImagePi

**ImagePi** is a Python-based Raspberry Pi camera system designed for capturing, managing, and inspecting plant images. This project allows users to control multiple cameras connected to a Raspberry Pi, capture images, transfer them for inspection and analysis, and perform live inspections through a graphical user interface (GUI).

## Features

- **Capture Images:** Utilize multiple cameras connected to a Raspberry Pi to capture high-quality images of plants using the `picamera2` library.
- **Image Management:** Transfer captured images to a specified directory for organized storage and easy access.
- **Graphical User Interface (GUI):**
  - **Tkinter-Based Main Interface:** Configure camera settings, capture images, transfer configurations, and manage system operations.
  - **PySide2-Based Live Inspection Window:** Perform real-time inspections of the camera feeds through a separate, responsive window.
- **Remote Server Control:** Start and stop server scripts (`steam_server.py`) on the Raspberry Pi remotely via SSH.
- **System Reset:** Reset the system or reboot the Raspberry Pi in case of failures or maintenance needs.
- **Configuration Management:** Manage system settings through a JSON configuration file (`params.json`) using the GUI.

## Requirements

### Main System

- **Operating System:** Windows, macOS, or Linux
- **Python Version:** Python 3.x
- **Required Python Packages:** Listed in `main_system/requirements.txt`
  - `Pillow`
  - `paramiko`
  - `python-dotenv`
  - `PySide2`
  - `requests`


### Raspberry Pi

- **Hardware:**
  - Raspberry Pi (compatible models, e.g., Raspberry Pi 4B)
  - QH camera(s) attached
  - Arducam Multi Camera Adapter Module V2.2 for Raspberry Pi
- **Software:**
  - **Operating System:** Raspberry Pi OS (preferably the latest version)
  - **Python Version:** Python 3.x
- **Required Packages:**
  - `python3-pip`
  - `python3-rpi.gpio`
  - `libcamera-apps`
  - `wiringpi`
  - `python3-kms++`
  - `python3-libcamera`
  - `python3-pyqt5`
  - `python3-prctl`
  - `libatlas-base-dev`
  - `ffmpeg`
  - `numpy`
  - `picamera2`


## Installation

### Main System

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/Dxxc/ImagePi.git
    cd ImagePi
    ```

2. **Create a Virtual Environment (Optional but Recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the Required Packages:**

    ```bash
    pip install -r main_system/requirements.txt
    ```

### Raspberry Pi

1. **Update and Upgrade Your Raspberry Pi:**

    ```bash
    sudo apt-get update
    sudo apt-get upgrade -y
    ```

2. **Install the Required System Packages:**

    ```bash
    sudo apt-get install -y python3 python3-pip python3-rpi.gpio libcamera-apps wiringpi
    sudo apt install -y python3-kms++ python3-libcamera python3-pyqt5 python3-prctl libatlas-base-dev ffmpeg
    sudo pip3 install numpy --upgrade
    sudo pip3 install picamera2
    ```

    *These instructions are adapted from the [ArduCAM RaspberryPi repository](https://github.com/ArduCAM/RaspberryPi.git). Refer to this repository for more details.*

3. **Add Support for Raspberry Pi 4B (If Applicable):**

    ```bash
    cd /tmp
    wget https://project-downloads.drogon.net/wiringpi-latest.deb
    sudo dpkg -i wiringpi-latest.deb
    ```

4. **Deploy the Raspberry Pi Code:**

    ```bash
    ./deploy_to_pi.sh
    ```

    *Ensure that `deploy_to_pi.sh` has executable permissions. If not, run `chmod +x deploy_to_pi.sh` before executing.*

5. **Install Python Dependencies for Raspberry Pi:**

    Navigate to the `raspberry_pi/` directory and install Python packages using the provided `requirements.txt`:

    ```bash
    cd raspberry_pi/
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    ```

    *This ensures that all necessary Python packages are installed within a virtual environment.*

## Usage

### Main System

1. **Ensure Raspberry Pi Connectivity:**

    - Make sure your Raspberry Pi is connected to the same network as your main system.
    - Verify that the cameras are properly set up and connected to the Raspberry Pi.

2. **Configure Environment Variables:**

    - Create a `.env` file in the `main_system/` directory with the following content:

        ```env
        PI_USERNAME=your_pi_username
        PI_PASSWORD=your_pi_password
        ```

    - Replace `your_pi_username` and `your_pi_password` with your Raspberry Pi's SSH credentials.

3. **Run the Application:**

    ```bash
    python main_system/gui.py
    ```

4. **Using the GUI:**

    - **Configure Settings:** Select the cameras to use, enter the plant name, and specify the folder path for storing images.
    - **Submit Configuration:** Save and transfer the configuration to the Raspberry Pi.
    - **Start Imaging:** Begin capturing images based on the configured settings.
    - **Inspect Images:** Use the "Inspect Images" button to review captured images.
    - **Live Inspection:** Launch a separate PySide2 window for real-time camera feed inspection.
    - **Reset System:** Reboot the Raspberry Pi if necessary.
    - **Quit Application:** Exit the application gracefully.

### Live Inspection

- **Launching Live Inspection:**
  
  - Click the "Live Inspection" button in the main Tkinter GUI.
  - This action will:
    - Start the `steam_server.py` script on the Raspberry Pi via SSH.
    - Launch the PySide2-based `MainWindow` in a separate process to display the live camera feeds.

- **Closing Live Inspection:**
  
  - Closing the PySide2 window will automatically:
    - Terminate the `steam_server.py` script running on the Raspberry Pi.
    - Re-enable the buttons in the main Tkinter GUI for further operations.

## Configuration

Configuration settings are managed through a JSON file (`params.json`) located in both the `main_system/` and `raspberry_pi/` directories. You can update this file directly or use the GUI to modify settings.

### Parameters Managed:

- **Camera Selection:** Enable or disable cameras A, B, C, and D.
- **Plant Name:** Identifier for the plant being monitored.
- **Folder Path:** Directory where captured images will be stored.
- **Timestamp:** Automatically generated based on the plant name and current date-time.
- **Other Custom Settings:** As defined in the `config.py` and utilized by the application.

## File Structure

```plaintext
ImagePi/
├── README.md
├── deploy_to_pi.sh
│
├── main_system/
│   ├── gui.py
│   ├── network.py
│   ├── credentials.py
│   ├── config.py
│   ├── imagecapture.py
│   ├── stream.py
│   ├── params.json
│   ├── requirements.txt
│   └── .env
│   
└── raspberry_pi/
    ├── camera_control.py
    ├── steam_server.py
    ├── requirements.txt
    ├── params.json





