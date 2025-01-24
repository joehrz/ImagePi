# ImagePi: A Multi-Camera Raspberry Pi System

**ImagePi** is a Python-based Raspberry Pi camera solution designed for capturing, managing, and inspecting images from multiple cameras. This version separates code into two main parts:

1. A **Flask server** on the Raspberry Pi for streaming low-resolution video and providing high-resolution snapshots.  
2. A **PySide2 GUI** for remote control and monitoring on a user’s local machine.

---

## Features

1. **Low-Resolution Live Streaming**  
   - Stream from multiple cameras via a web endpoint for lightweight, continuous previews.

2. **High-Resolution Snapshots**  
   - Switch each camera to a full-resolution mode on demand to capture quality stills.

3. **Multi-Camera Muxing**  
   - Use an Arducam Multi-Camera Adapter or similar multiplexer with GPIO and I2C switching.

4. **GUI Control**  
   - A cross-platform PySide2 interface lets you:
     - Start/stop individual streams,
     - Capture snapshots (single or multiple in sequence),
     - Select and change the local folder for saving images,
     - Reboot the Pi,
     - Quit the application.

5. **Organized Project Structure**  
   - Clearly separates server (Flask) and GUI (PySide2) code into different directories.

---

## Requirements

### Raspberry Pi (Server Side)

- **Hardware**:
  - Raspberry Pi (e.g., Raspberry Pi 4B)
  - Multiple cameras via an Arducam Multi-Camera Adapter (or similar)

- **Software**:
  - Raspberry Pi OS (Bullseye or newer, with libcamera)
  - Python 3.x
  - Recommended packages:
    - `libcamera-apps`, `python3-libcamera`, `python3-picamera2`
    - `opencv-python` (`cv2`)
    - `RPi.GPIO`
    - `numpy`
    - `Flask`
    - (See `requirements.txt` in the `server/` folder for a full list)

### Local System (GUI Side)

- **Operating System**: Windows, macOS, or Linux
- **Python Version**: Python 3.x
- **Python Packages**:
  - `PySide2`
  - `requests`
  - `opencv-python`
  - (See `requirements.txt` in the `gui/` folder)

---



## Installation

### Main System

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/joehrz/ImagePi.git
    cd ImagePi
    ```

2. **Create a Virtual Environment (Optional but Recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3. **Install Dependencies:**

    ```bash
    cd gui
    pip install -r requirements.txt
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
    cd ../scripts
    python run_gui.py --ip <Raspberry_Pi_IP>
    ```

### Usage and Workflow

- **Start the Server on the Raspberry Pi:**
  
  - Ensures /video_feed/<camera_id> and /snapshot/<camera_id> endpoints are available
  - Launch the GUI on your local machine

- **Taking Snapshots:**
  
  - Click “Take Snapshot A/B/C/D” to get a high-res image from that camera.
  - Or use “Take All Snapshots” to capture from all cameras in sequence.

- **Saving Images Locally:**
  - The GUI will prompt for or use a default folder to store .jpg images.

- **Reboot or Quit:**

    - A “Reboot Pi” button may call a server endpoint to reboot the Pi (if implemented).
    - A “Quit” button closes the GUI application.









