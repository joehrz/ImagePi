from PySide2.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QGridLayout,
    QPushButton, QMessageBox, QLabel, QFileDialog
)
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtCore import QUrl, Qt, Slot
from functools import partial
import sys
from pathlib import Path

from .snapshot_worker import SnapshotWorker
from .all_snapshots_worker import AllSnapshotsWorker

CAMERA_IDS = ['a', 'b', 'c', 'd']

class MainWindow(QMainWindow):
    def __init__(self, raspberry_pi_ip):
        super().__init__()
        self.setWindowTitle("Multi-Camera Stream and Snapshot")
        self.raspberry_pi_ip = raspberry_pi_ip

        self.storage_folder = str(Path.home() / "Pictures")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.folder_button = QPushButton("Change Storage Folder")
        self.folder_button.clicked.connect(self.choose_storage_folder)
        self.main_layout.addWidget(self.folder_button)

        # Button to take snapshots from all cameras
        self.all_snap_button = QPushButton("Take All Snapshots")
        self.all_snap_button.clicked.connect(self.take_snapshots_all)
        self.main_layout.addWidget(self.all_snap_button)

        # Grid for cameras
        self.camera_grid = QGridLayout()
        self.main_layout.addLayout(self.camera_grid)

        self.cameras = {}
        self.snapshot_workers = {}

        positions = [(0,0), (0,1), (1,0), (1,1)]
        for pos, cid in zip(positions, CAMERA_IDS):
            cam_layout = self.create_camera_widget(cid)
            self.camera_grid.addLayout(cam_layout, *pos)
            self.cameras[cid] = cam_layout

        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")

    def create_camera_widget(self, camera_id):
        layout = QVBoxLayout()

        title = QLabel(f"Camera {camera_id.upper()}")
        title.setStyleSheet("font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        video_url = f"http://{self.raspberry_pi_ip}:5001/video_feed/{camera_id}"
        browser = QWebEngineView()
        browser.setUrl(QUrl(video_url))
        browser.setFixedSize(320, 240)
        layout.addWidget(browser)

        snap_button = QPushButton(f"Take Snapshot {camera_id.upper()}")
        snap_button.clicked.connect(partial(self.take_snapshot, camera_id))
        layout.addWidget(snap_button)

        return layout

    def choose_storage_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", self.storage_folder)
        if folder:
            self.storage_folder = folder
            self.show_info(f"Storage folder changed to: {folder}")

    def take_snapshot(self, camera_id):
        self.set_buttons_enabled(False)
        self.show_info(f"Taking snapshot from Camera {camera_id.upper()}...")

        worker = SnapshotWorker(self.raspberry_pi_ip, camera_id, self.storage_folder)
        worker.snapshot_taken.connect(self.on_snapshot_taken)
        worker.error.connect(self.display_error)
        worker.finished.connect(lambda: self.on_snapshot_finished())
        worker.start()

        self.snapshot_workers[camera_id] = worker

    @Slot(str)
    def on_snapshot_taken(self, filepath):
        self.show_info(f"Snapshot saved: {filepath}")

    @Slot(str)
    def display_error(self, msg):
        self.set_buttons_enabled(True)
        self.statusBar().showMessage(msg, 5000)
        QMessageBox.critical(self, "Error", msg)

    def on_snapshot_finished(self):
        self.set_buttons_enabled(True)

    def set_buttons_enabled(self, enabled):
        self.folder_button.setEnabled(enabled)
        self.all_snap_button.setEnabled(enabled)
        for cid in CAMERA_IDS:
            cam_layout = self.cameras[cid]
            snap_btn = cam_layout.itemAt(2).widget()  # The snapshot button
            snap_btn.setEnabled(enabled)

    def stop_all_streams(self):
        """Stop streaming by setting each QWebEngineView to blank."""
        for cid in CAMERA_IDS:
            layout = self.cameras[cid]
            browser = layout.itemAt(1).widget()
            browser.setUrl(QUrl("about:blank"))

    def start_all_streams(self):
        """Restart streaming by pointing each QWebEngineView back to its URL."""
        for cid in CAMERA_IDS:
            layout = self.cameras[cid]
            browser = layout.itemAt(1).widget()
            video_url = f"http://{self.raspberry_pi_ip}:5001/video_feed/{cid}"
            browser.setUrl(QUrl(video_url))

    def take_snapshots_all(self):
        self.set_buttons_enabled(False)
        self.show_info("Taking snapshots from all cameras (A->D)...")

        # Stop streams first
        self.stop_all_streams()

        worker = AllSnapshotsWorker(self.raspberry_pi_ip, CAMERA_IDS, self.storage_folder)
        worker.finished_all.connect(self.on_all_snapshots_done)
        worker.error.connect(self.display_error)
        worker.finished.connect(lambda: self.set_buttons_enabled(True))
        worker.start()

    @Slot(str)
    def on_all_snapshots_done(self, msg):
        self.show_info(msg)
        # If you want to start streams again automatically:
        # self.start_all_streams()

    def show_info(self, msg):
        self.statusBar().showMessage(msg, 5000)
        QMessageBox.information(self, "Info", msg)
