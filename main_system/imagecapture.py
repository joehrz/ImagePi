import paramiko
import json
import os
import re
import io
import logging
from PIL import Image, ImageTk
import tkinter as tk
import posixpath
from pathlib import PureWindowsPath, PurePosixPath, Path
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ConfigLoader:
    def __init__(self, config_path='params.json'):
        self.config_path = config_path

    def load(self):
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.error(f"Error loading configuration: {e}")
            return {}

class SSHClientWrapper:
    def __init__(self, ssh_client):
        self.ssh_client = ssh_client

    def execute_command(self, command):
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            output = stdout.read().decode()
            error = stderr.read().decode()
            if error:
                logging.error(f"Error: {error}")
            return output
        except Exception as e:
            logging.error(f"SSH command execution failed: {e}")
            return ""

    def transfer_files(self, remote_path, local_path):
        try:
            logging.info(f"Starting file transfer from {remote_path} to {local_path}")
            
            # Ensure local directory exists
            if not os.path.exists(local_path):
                os.makedirs(local_path)
                logging.info(f"Created local directory: {local_path}")
            
            with self.ssh_client.open_sftp() as sftp_client:
                file_list = sftp_client.listdir(remote_path)
                logging.info(f"Found {len(file_list)} files in remote directory.")
                
                for file_name in file_list:
                    # Use posixpath for remote paths to ensure forward slashes
                    remote_file = posixpath.join(remote_path, file_name)
                    
                    # Use os.path.join for local paths to ensure correct separators
                    local_file = os.path.join(local_path, file_name)
                    
                    logging.debug(f"Transferring {remote_file} to {local_file}")

                    
                    sftp_client.get(remote_file, local_file)

            
            logging.info(f"Files successfully transferred to {local_path}")
        except FileNotFoundError as fnf_error:
            logging.error(f"File not found: {fnf_error}")
        except PermissionError as perm_error:
            logging.error(f"Permission denied: {perm_error}")
        except Exception as e:
            logging.error(f"File transfer failed: {e}")


class CameraSystem:
    def __init__(self, ssh_client, gui_root, config_loader):
        self.gui_root = gui_root
        self.ssh_client = SSHClientWrapper(ssh_client)
        self.config_loader = config_loader
        self.config = self.config_loader.load()

        self.image_frame = tk.Frame(self.gui_root)
        self.image_frame.grid(row=0, column=0)
        self.image_index = 0
        self.images = []
        self.image_label = None
        self.camera_labels = {}

    def inspect(self):
        plant_folder, plant_name, date_str = self.prepare_inspection_folders()
        self.setup_camera_labels(plant_name, date_str)
        self.capture_image('inspect')
        remote_inspect_dir = posixpath.join('/home/imagepi/Images', plant_folder, 'inspect')
        self.fetch_and_display_images(remote_inspect_dir)

    def prepare_inspection_folders(self):
        folder_with_date = self.config.get("folder_with_date", 'default_folder')
        
        # Handle both Windows and Unix-like paths
        if os.name == 'nt':  # Windows
            path = PureWindowsPath(folder_with_date)
        else:
            path = Path(folder_with_date)
        
        plant_folder = path.name  # Get the last part of the path
        plant_name = self.config.get("plant_name", "default_plant")
        date_str = self.extract_date_from_timestamp()
        
        # Construct remote path using posixpath
        remote_inspect_dir = posixpath.join('/home/imagepi/Images', plant_folder, 'inspect')
        self.ssh_client.execute_command(f'sudo mkdir -p {remote_inspect_dir}')
        return plant_folder, plant_name, date_str

    def extract_date_from_timestamp(self):
        match = re.search(r'\d{4}-\d{2}-\d{2}', self.config.get('timestamp', '20240101'))
        return match.group(0) if match else 'unknown_date'

    def setup_camera_labels(self, plant_name, date_str):
        self.camera_labels = {}
        for camera_id in ['A', 'B', 'C', 'D']:
            if self.config.get(f"camera_{camera_id.lower()}", 0) == 1:
                file_name = f"{plant_name}_Camera_{camera_id}_{date_str}.jpg"
                self.camera_labels[file_name] = camera_id

    def imaging(self):
        plant_folder = self.prepare_imaging_folders()
        self.capture_image('images')
        self.transfer_images(plant_folder, 'images')

    def prepare_imaging_folders(self):
        folder_with_date = self.config.get("folder_with_date", 'default_folder')
        
        # Handle both Windows and Unix-like paths
        if os.name == 'nt':  # Windows
            path = PureWindowsPath(folder_with_date)
        
        plant_folder = path.name  # Get the last part of the path
        remote_images_dir = posixpath.join('/home/imagepi/Images', plant_folder, 'images')
        self.ssh_client.execute_command(f'sudo mkdir -p {remote_images_dir}')
        return plant_folder

    def capture_image(self, image_folder):
        cmd = f'sudo python /home/imagepi/camera_control.py {image_folder}'
        self.ssh_client.execute_command(cmd)

    def fetch_and_display_images(self, image_directory):
        raw_images = self.fetch_images(image_directory)
        self.images = [(self.resize_image(img_data), file_name) for img_data, file_name in raw_images]
        self.images.sort(key=lambda x: self.camera_labels.get(x[1], "Unknown"))  # Sort images based on camera labels
        self.create_image_window()

    def fetch_images(self, image_directory):
        raw_images = []
        try:
            with self.ssh_client.ssh_client.open_sftp() as sftp_client:
                file_list = sftp_client.listdir(image_directory)
                for file_name in file_list:
                    if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                        # Use posixpath for remote paths
                        file_path = posixpath.join(image_directory, file_name)
                        with sftp_client.open(file_path, 'rb') as file_handle:
                            raw_images.append((file_handle.read(), file_name))
        except Exception as e:
            logging.error(f"An error occurred while fetching images: {e}")
        return raw_images

    def resize_image(self, image_data):
        max_size = (800, 600)
        image = Image.open(io.BytesIO(image_data))
        image.thumbnail(max_size, Image.ANTIALIAS)
        return ImageTk.PhotoImage(image)

    def create_image_window(self):
        if not self.images:
            logging.info("No images to display.")
            return

        window = tk.Toplevel(self.gui_root)
        window.title("Image Inspection")
        self.image_label = tk.Label(window)
        self.image_label.pack()

        self.camera_info_label = tk.Label(window, text="")
        self.camera_info_label.pack()

        tk.Button(window, text="<< Previous", command=self.show_previous_image).pack(side="left")
        tk.Button(window, text="Next >>", command=self.show_next_image).pack(side="right")

        self.show_image(0)

    def show_image(self, index):
        if 0 <= index < len(self.images):
            self.image_index = index
            image, file_name = self.images[index]
            self.image_label.config(image=image)
            camera_id = self.camera_labels.get(file_name, "Unknown")
            self.camera_info_label.config(text=f"Camera: {camera_id}")

    def show_next_image(self):
        if self.image_index < len(self.images) - 1:
            self.show_image(self.image_index + 1)

    def show_previous_image(self):
        if self.image_index > 0:
            self.show_image(self.image_index - 1)

    def transfer_images(self, plant_folder, image_folder):
        local_dir = self.config.get("folder_path", "C:\\default\\path")  # Ensure a valid default
        remote_dir = posixpath.join('/home/imagepi/Images', plant_folder, image_folder)
        self.ssh_client.transfer_files(remote_dir, local_dir)

if __name__ == "__main__":
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        pi_username = os.getenv('PI_USERNAME')
        pi_password = os.getenv('PI_PASSWORD')
        client.connect('raspberrypi.local', username=pi_username, password=pi_password)
        config_loader = ConfigLoader()
        root = tk.Tk()  # Initialize Tkinter root
        app = CameraSystem(client, root, config_loader)
        app.inspect()
        root.mainloop()
    finally:
        client.close()






