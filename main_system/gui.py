# main_app.py

import tkinter as tk
from tkinter import filedialog, messagebox
import threading
from datetime import datetime
import paramiko
import logging
import time
import os
from dotenv import load_dotenv
import multiprocessing  # Import multiprocessing to handle separate processes

from imagecapture import CameraSystem
from credentials import NetworkConfig
from config import Config
from network import NetworkManager
# Remove the direct import of MainWindow from stream to prevent unintended side effects
# from stream import MainWindow

# Load environment variables from a .env file
load_dotenv()

# Configure the root logger in the main module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Import the run_main_window function from stream.py
from stream import run_main_window

class InputGUI:
    """
    The InputGUI class sets up and manages the graphical user interface for PhotoPI.
    It handles user inputs, manages network and SSH connections, and interfaces with the CameraSystem.
    """
    def __init__(self, master):
        """
        Initializes the InputGUI class, sets up the main window, and initializes network and SSH connections.

        Parameters:
            master (tk.Tk): The main window of the Tkinter application.
        """
        self.master = master
        self.master.title("ImagePI")
        self.master.geometry("500x500")
        self.config = Config()
        self.network_manager = None
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Load credentials from environment variables
        self.pi_username = os.getenv('PI_USERNAME')
        self.pi_password = os.getenv('PI_PASSWORD')

        if self.initialize_network_and_ssh():
            self.setup_gui_components()
        else:
            self.master.quit()

        # Keep track of the camera process
        self.camera_process = None

    def initialize_network_and_ssh(self):
        """
        Initializes network settings and SSH client using dynamic credentials.

        Returns:
            bool: True if the network and SSH connection are successfully established, False otherwise.
        """
        net_config = NetworkConfig(self.master)
        try:
            net_config.discover_pi_hostname()

            if net_config.hostname and self.pi_username and self.pi_password:
                self.network_manager = NetworkManager(net_config.hostname, self.pi_username, self.pi_password)
                self.config.set_value('pi_hostname', net_config.hostname)
                self.config.save_config()

                self.ssh_client.connect(net_config.hostname, username=self.pi_username, password=self.pi_password)
                logging.info("Network and SSH connection established successfully.")
                return True
            else:
                raise ValueError("Hostname, username, or password not provided or incorrect.")
        except (paramiko.ssh_exception.NoValidConnectionsError, ValueError) as e:
            messagebox.showerror("Connection Error", f"Failed to establish network or SSH connection: {str(e)}")
            return False

    def update_gui_from_thread(self, message):
        """
        Safely updates the GUI from a background thread.

        Parameters:
            message (str): The message to display in the GUI.
        """
        def update_status():
            if "successfully" in message:
                messagebox.showinfo("Success", message)
            else:
                messagebox.showerror("Error", message)
            self.enable_buttons()
        self.master.after(100, update_status)

    def validate_text_entry(self, text):
        """
        Validates text entry in the GUI.

        Parameters:
            text (str): The text to validate.

        Returns:
            bool: Always returns True (example validation function).
        """
        return True

    def setup_gui_components(self):
        """
        Sets up the GUI components including camera checkbuttons, plant name entry, folder path entry, and action buttons.
        """
        self.setup_camera_checkbuttons()
        self.setup_plant_name_entry()
        self.setup_folder_path_entry()
        self.setup_action_buttons()

    def setup_camera_checkbuttons(self):
        """
        Sets up the camera checkbuttons in the GUI.
        """
        self.camera_label = tk.Label(self.master, text="Cameras:")
        self.camera_label.grid(row=0, column=1)

        self.camera_a_var = tk.IntVar(value=0)
        self.camera_a_checkbutton = tk.Checkbutton(self.master, text="Camera A", variable=self.camera_a_var)
        self.camera_a_checkbutton.grid(row=1, column=1)

        self.camera_b_var = tk.IntVar(value=0)
        self.camera_b_checkbutton = tk.Checkbutton(self.master, text="Camera B", variable=self.camera_b_var)
        self.camera_b_checkbutton.grid(row=2, column=1)

        self.camera_c_var = tk.IntVar(value=0)
        self.camera_c_checkbutton = tk.Checkbutton(self.master, text="Camera C", variable=self.camera_c_var)
        self.camera_c_checkbutton.grid(row=3, column=1)

        self.camera_d_var = tk.IntVar(value=0)
        self.camera_d_checkbutton = tk.Checkbutton(self.master, text="Camera D", variable=self.camera_d_var)
        self.camera_d_checkbutton.grid(row=4, column=1)

    def setup_plant_name_entry(self):
        """
        Sets up the plant name entry field in the GUI.
        """
        tcmd = (self.master.register(self.validate_text_entry), "%P")

        self.plant_name_label = tk.Label(self.master, text="Plant Name:")
        self.plant_name_label.grid(row=5)
        self.plant_name_entry = tk.Entry(self.master, validate="key", validatecommand=tcmd)
        self.plant_name_entry.grid(row=5, column=1)

    def setup_folder_path_entry(self):
        """
        Sets up the folder path entry field and browse button in the GUI.
        """
        tk.Label(self.master, text="Folder Path:").grid(row=6)
        self.folder_path_entry = tk.Entry(self.master)
        self.folder_path_entry.grid(row=6, column=1)
        tk.Button(self.master, text="Browse", command=self.browse_folder).grid(row=6, column=2)

    def setup_action_buttons(self):
        """
        Sets up action buttons (Submit, Inspect Images, Start Imaging, Reset, Quit) in the GUI.
        """
        self.submit_button = tk.Button(self.master, text="Submit", command=self.submit)
        self.submit_button.grid(row=7, column=0)

        self.inspect_button = tk.Button(self.master, text="Inspect Images", command=self.perform_inspection)
        self.inspect_button.grid(row=9, column=0)

        self.start_imaging_button = tk.Button(self.master, text="Start Imaging", command=self.start_imaging)
        self.start_imaging_button.grid(row=9, column=1)

        self.live_inspection_button = tk.Button(self.master, text="Live Inspection", command=self.live_inspection)
        self.live_inspection_button.grid(row=9, column=2)

        self.reset_button = tk.Button(self.master, text="Reset", command=self.reset)
        self.reset_button.grid(row=9, column=3)

        self.quit_button = tk.Button(self.master, text="Quit", command=self.master.quit)
        self.quit_button.grid(row=9, column=4)

    def browse_folder(self):
        """
        Opens a dialog to select a folder path and updates the folder path entry field with the selected path.
        """
        folder_path = filedialog.askdirectory()
        self.folder_path_entry.delete(0, tk.END)
        self.folder_path_entry.insert(0, folder_path)

    def read_input_values(self):
        """
        Reads input values from the GUI and returns them as a dictionary.

        Returns:
            dict: A dictionary containing the input values.
        """
        raw_folder_path = self.folder_path_entry.get().strip()
        normalized_folder_path = os.path.normpath(raw_folder_path)
        print(f"Normalized Folder Path: {normalized_folder_path}")  # Debugging

        return {
            'camera_a': self.camera_a_var.get(),
            'camera_b': self.camera_b_var.get(),
            'camera_c': self.camera_c_var.get(),
            'camera_d': self.camera_d_var.get(),
            'plant_name': self.plant_name_entry.get().strip(),
            'folder_path': normalized_folder_path
        }


    def update_configuration(self, inputs):
        """
        Updates the configuration based on input values.

        Parameters:
            inputs (dict): A dictionary containing the input values.
        """
        timestamp = datetime.now().strftime('%Y-%m-%d-%H%M')
        inputs['timestamp'] = inputs['plant_name'] + timestamp

        inputs['folder_with_date'] = os.path.join(inputs['folder_path'], inputs['timestamp'])

        for key, value in inputs.items():
            self.config.set_value(key, value)
        self.config.save_config()

    def transfer_configuration(self):
        """
        Transfers the configuration file to the Raspberry Pi.
        """
        try:
            self.network_manager.connect()
            self.network_manager.transfer_file('params.json', '/home/imagepi/params.json')
            logging.info("Configuration transferred successfully.")
        except Exception as e:
            logging.error(f"Failed to transfer configuration: {e}")
        finally:
            self.network_manager.disconnect()

    def validate_inputs(self, inputs):
        """
        Validates input fields to ensure they are not empty.

        Parameters:
            inputs (dict): A dictionary containing the input values.

        Returns:
            bool: True if all required fields are not empty, False otherwise.
        """
        for key, value in inputs.items():
            if key in ['angle', 'plant_name', 'seconds', 'folder_path'] and not value:
                messagebox.showerror("Input Error", f"{key.replace('_', ' ').capitalize()} cannot be empty.")
                return False
        return True

    def submit(self):
        """
        Reads input values, validates them, updates the configuration, and transfers the configuration file.
        """
        inputs = self.read_input_values()
        if not self.validate_inputs(inputs):
            return
        self.update_configuration(inputs)
        self.transfer_configuration()

    def disable_buttons(self):
        """
        Disables the Inspect and Start Imaging buttons to prevent multiple clicks.
        """
        self.inspect_button.config(state=tk.DISABLED)
        self.start_imaging_button.config(state=tk.DISABLED)
        self.live_inspection_button.config(state=tk.DISABLED)

    def enable_buttons(self):
        """
        Enables the Inspect and Start Imaging buttons.
        """
        self.inspect_button.config(state=tk.NORMAL)
        self.start_imaging_button.config(state=tk.NORMAL)
        self.live_inspection_button.config(state=tk.NORMAL)

    def perform_inspection(self):
        """
        Creates and uses the CameraSystem instance for inspection.
        """
        self.disable_buttons()
        def task():
            try:
                if hasattr(self, 'ssh_client'):
                    camera_system = CameraSystem(self.ssh_client, self.master, self.config)
                    camera_system.inspect()
                    logging.info("Inspection performed successfully.")
                    self.update_gui_from_thread("Inspection performed successfully.")
                else:
                    self.update_gui_from_thread("SSH client is not initialized.")
            except Exception as e:
                self.update_gui_from_thread(f"Error during inspection: {str(e)}")
            finally:
                self.enable_buttons()

        threading.Thread(target=task).start()

    def start_imaging(self):
        """
        Starts a background task to create and use the CameraSystem instance for imaging.
        """
        self.disable_buttons()
        def task():
            try:
                if hasattr(self, 'ssh_client'):
                    camera_system = CameraSystem(self.ssh_client, self.master, self.config)
                    camera_system.imaging()
                    self.update_gui_from_thread("Imaging started successfully.")
                    
                else:
                    self.update_gui_from_thread("SSH client is not initialized.")
            except Exception as e:
                self.update_gui_from_thread(f"Error during imaging: {str(e)}")
            finally:
                self.enable_buttons()

        threading.Thread(target=task).start()

    def live_inspection(self):
        """
        Starts the PySide2 MainWindow in a separate process for live inspection and manages the remote steam_server.py script.
        """
        self.disable_buttons()

        def task():
            try:
                raspberry_pi_ip = self.config.get_value('pi_hostname')
                # raspberry_pi_ip = "130.179.113.194"  # Alternatively, retrieve dynamically

                # Start steam_server.py on the Raspberry Pi in the background
                # Using nohup to run the process independently
                command_start_server = 'sudo nohup python /home/imagepi/steam_server.py > /dev/null 2>&1 &'
                stdin, stdout, stderr = self.ssh_client.exec_command(command_start_server)
                time.sleep(4)
                # Optionally, you can read stdout and stderr if needed
                logging.info("steam_server.py started on Raspberry Pi.")

                # Check if the camera process is already running
                if self.camera_process is None or not self.camera_process.is_alive():
                    # Create a new process for the PySide2 GUI
                    self.camera_process = multiprocessing.Process(
                        target=run_main_window,
                        args=(raspberry_pi_ip,),
                        daemon=True  # Ensures the process exits when the main program does
                    )
                    self.camera_process.start()
                    logging.info("Live Inspection window started successfully.")
                    self.update_gui_from_thread("Live Inspection window started successfully.")

                    # Start a monitoring thread to watch the camera_process
                    monitor_thread = threading.Thread(target=self.monitor_camera_process, daemon=True)
                    monitor_thread.start()
                else:
                    self.update_gui_from_thread("Live Inspection window is already running.")
            except Exception as e:
                self.update_gui_from_thread(f"Error starting Live Inspection: {str(e)}")
                logging.error(f"Error in live_inspection: {e}")
            finally:
                self.enable_buttons()

        threading.Thread(target=task).start()

    def monitor_camera_process(self):
        """
        Monitors the PySide2 camera process. When it terminates, stops the steam_server.py script on the Raspberry Pi.
        """
        if self.camera_process:
            self.camera_process.join()  # Wait for the camera_process to finish
            logging.info("Live Inspection window has been closed.")

            # Stop the steam_server.py script on the Raspberry Pi
            try:
                # Using pkill to terminate the steam_server.py process
                command_stop_server = 'sudo pkill -f steam_server.py'
                stdin, stdout, stderr = self.ssh_client.exec_command(command_stop_server)
                # Optionally, you can read stdout and stderr if needed
                logging.info("steam_server.py stopped on Raspberry Pi.")
                self.update_gui_from_thread("Live Inspection ended and steam_server.py stopped.")
            except Exception as e:
                self.update_gui_from_thread(f"Error stopping steam_server.py: {str(e)}")
                logging.error(f"Error stopping steam_server.py: {e}")

    def reboot_raspberry_pi(self):
        """
        Reboots the Raspberry Pi by sending a reboot command over SSH.
        """
        try:
            self.ssh_client.exec_command('sudo reboot')
            logging.info("Reboot command sent to Raspberry Pi.")
            self.ssh_client.close()
            threading.Thread(target=self.wait_for_pi_to_reboot).start()
        except Exception as e:
            logging.error(f"Failed to send reboot command: {e}")
            messagebox.showerror("Reboot Error", f"Failed to send reboot command: {e}")

    def on_closing(self):
        """
        Handles the window close event. Ensures that the PySide2 process is terminated and the remote server script is stopped.
        """
        if self.camera_process and self.camera_process.is_alive():
            self.camera_process.terminate()
            self.camera_process.join()
            logging.info("Live Inspection window terminated by user.")

            # Stop the steam_server.py script on the Raspberry Pi
            try:
                command_stop_server = 'sudo pkill -f steam_server.py'
                stdin, stdout, stderr = self.ssh_client.exec_command(command_stop_server)
                logging.info("steam_server.py stopped on Raspberry Pi due to user termination.")
            except Exception as e:
                logging.error(f"Error stopping steam_server.py on user termination: {e}")

        self.master.destroy()



    def wait_for_pi_to_reboot(self):
        """
        Waits for the Raspberry Pi to come back online after a reboot.
        """
        time.sleep(60)  # Wait for 60 seconds before attempting to reconnect
        pi_hostname = self.config.get_value('pi_hostname')
        while True:
            try:
                self.ssh_client = paramiko.SSHClient()
                self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.ssh_client.connect(pi_hostname, username=self.pi_username, password=self.pi_password)
                logging.info("Raspberry Pi is back online.")
                self.master.after(100, lambda: messagebox.showinfo("Reboot", "Raspberry Pi is back online."))
                break
            except Exception as e:
                logging.info("Waiting for Raspberry Pi to come back online...")
                time.sleep(5)

    def reset(self):
        """
        Resets the application by rebooting the Raspberry Pi.
        """
        reboot_confirmation = messagebox.askyesno("Reboot Confirmation", "Are you sure you want to reboot the Raspberry Pi?")
        if reboot_confirmation:
            self.reboot_raspberry_pi()

def main():
    multiprocessing.freeze_support()  # For Windows support
    root = tk.Tk()
    app = InputGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()





