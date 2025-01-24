from PySide2.QtCore import QThread, Signal
import time
import requests
from pathlib import Path

class SnapshotWorker(QThread):
    snapshot_taken = Signal(str)
    error = Signal(str)

    def __init__(self, raspberry_pi_ip, camera_id, storage_folder):
        super().__init__()
        self.raspberry_pi_ip = raspberry_pi_ip
        self.camera_id = camera_id
        self.storage_folder = storage_folder

    def run(self):
        try:
            url = f"http://{self.raspberry_pi_ip}:5001/snapshot/{self.camera_id}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            ctype = response.headers.get("Content-Type", "")
            if "image" not in ctype.lower():
                raise Exception(f"Received non-image data: {ctype}")

            timestamp = time.strftime("%Y_%m%d_%H_%M_%S")
            filename = f"Camera_{self.camera_id.upper()}_{timestamp}.jpg"
            filepath = Path(self.storage_folder) / filename

            with open(filepath, 'wb') as f:
                f.write(response.content)

            self.snapshot_taken.emit(str(filepath))
        except requests.RequestException as e:
            self.error.emit(f"HTTP request failed: {e}")
        except Exception as e:
            self.error.emit(f"Snapshot failed: {e}")