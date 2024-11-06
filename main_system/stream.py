# stream.py

import sys 
import time
import requests
from PySide2.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, 
    QPushButton, QMessageBox, QLabel
)
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtCore import QUrl
from functools import partial

class MainWindow(QMainWindow):
    def __init__(self, raspberry_pi_ip):
        super().__init__()
        self.setWindowTitle("Video Stream")
        self.raspberry_pi_ip = raspberry_pi_ip

        # Create the central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Create a vertical layout
        self.layout = QVBoxLayout(self.central_widget)

        # Create the QWebEngineView
        self.browser = QWebEngineView()
        self.layout.addWidget(self.browser)

        # Create a loading label
        self.loading_label = QLabel("Loading...")
        self.loading_label.setVisible(False)
        self.layout.addWidget(self.loading_label)

        # Create buttons to switch cameras
        self.buttons = {}
        for camera_id in ['a', 'b', 'c', 'd']:
            button = QPushButton(f"Switch to Camera {camera_id.upper()}")
            # Use functools.partial to connect the button click to the switch_camera method
            button.clicked.connect(partial(self.switch_camera, camera_id))
            self.layout.addWidget(button)
            self.buttons[camera_id] = button

        # Load initial URL
        self.load_url(f"http://{self.raspberry_pi_ip}:5001/video_feed")

    def load_url(self, url):
        self.loading_label.setVisible(True)
        self.browser.loadFinished.connect(self.on_load_finished)
        self.browser.setUrl(QUrl(url))

    def on_load_finished(self):
        self.loading_label.setVisible(False)
        self.browser.loadFinished.disconnect(self.on_load_finished)

    def switch_camera(self, camera_id):
        try:
            self.set_buttons_enabled(False)
            self.loading_label.setVisible(True)
            response = requests.post(
                f'http://{self.raspberry_pi_ip}:5001/switch_camera',
                json={"camera_id": camera_id},
                timeout=20
            )
            response.raise_for_status()
            # Reload the video feed
            timestamp = int(time.time() * 1000)
            video_feed_url = f"http://{self.raspberry_pi_ip}:5001/video_feed?camera={camera_id}&t={timestamp}"
            self.load_url(video_feed_url)
        except requests.RequestException as e:
            self.show_error(f"HTTP request failed: {e}")
        finally:
            self.set_buttons_enabled(True)

    def set_buttons_enabled(self, enabled):
        for button in self.buttons.values():
            button.setEnabled(enabled)

    def show_error(self, message):
        self.loading_label.setVisible(False)
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setText(message)
        error_dialog.setWindowTitle("Error")
        error_dialog.exec_()

def run_main_window(raspberry_pi_ip):
    """
    Initializes the QApplication and runs the MainWindow.

    Parameters:
        raspberry_pi_ip (str): The IP address of the Raspberry Pi.
    """
    app = QApplication(sys.argv)
    window = MainWindow(raspberry_pi_ip)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    # Example usage (for standalone testing)
    raspberry_pi_ip = "130.179.113.194"  # Replace with your Raspberry Pi's IP address
    run_main_window(raspberry_pi_ip)

