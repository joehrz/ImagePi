from PySide2.QtCore import QThread, Signal
import time
import requests
from pathlib import Path

class AllSnapshotsWorker(QThread):
    finished_all = Signal(str)
    error = Signal(str)

    def __init__(self, raspberry_pi_ip, camera_list, storage_folder):
        super().__init__()
        self.raspberry_pi_ip = raspberry_pi_ip
        self.camera_list = camera_list
        self.storage_folder = storage_folder

    def run(self):
        try:
            for cam in self.camera_list:
                url = f"http://{self.raspberry_pi_ip}:5001/snapshot/{cam}"
                response = requests.get(url, timeout=10)
                response.raise_for_status()

                ctype = response.headers.get("Content-Type", "")
                if "image" not in ctype.lower():
                    raise Exception(f"Non-image data from camera {cam}: {ctype}")

                timestamp = time.strftime("%Y_%m%d_%H_%M_%S")
                filename = f"Camera_{cam.upper()}_{timestamp}.jpg"
                filepath = Path(self.storage_folder) / filename

                with open(filepath, 'wb') as f:
                    f.write(response.content)

            self.finished_all.emit("All snapshots saved successfully.")
        except requests.RequestException as e:
            self.error.emit(f"HTTP request failed: {e}")
        except Exception as e:
            self.error.emit(str(e))