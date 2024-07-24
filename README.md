# ImagePi

**ImagePi** is a Python-based Raspberry Pi camera system designed for capturing and managing plant images. This project allows users to control cameras connected to a Raspberry Pi, capture images, and transfer them for inspection and analysis.

## Features

- Capture images using multiple cameras connected to a Raspberry Pi.
- Transfer captured images to a specified directory.
- Inspect captured images through a graphical user interface (GUI).
- Reset the system in case of failures.

## Requirements

- Python 3.x
- Raspberry Pi with camera(s) attached
- Required Python packages (listed in `requirements.txt`)

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/ImagePi.git
    cd ImagePi
    ```

2. Create a virtual environment (optional but recommended):

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```


## Usage

1. Ensure your Raspberry Pi is connected to the network and the cameras are properly set up.
2. Run the `gui.py` script to launch the application:

    ```bash
    python gui.py
    ```

3. Use the GUI to configure camera settings, capture images, inspect images, and reset the system if necessary.

## Configuration

Configuration settings are managed through a JSON file (`params.json`). You can update this file directly or use the GUI to modify settings.

