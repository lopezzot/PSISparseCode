#!/usr/bin/env python3

"""
Simple PhaiDRA logger acquisition GUI.

The program:
1. Creates a timestamped output file when START is pressed.
2. Searches for the FT232R USB serial logger.
3. Reads incoming logger lines at 9600 baud.
4. Appends each received line to the current output file.
5. Stops acquisition and closes the serial port when STOP is pressed.
"""

import threading
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

import serial
from serial.tools import list_ports


# Serial communication settings used by the logger.
BAUDRATE = 9600
READ_TIMEOUT = 1

# FTDI FT232R USB UART identifiers observed for the logger.
LOGGER_VID = 0x0403
LOGGER_PID = 0x6001

# Prefix used for acquisition files.
FILE_PREFIX = "phaidra_data"


class PhaiDRAApp:
    """Main GUI application and acquisition controller."""

    def __init__(self, root):
        """Initialize the GUI, application state, and output file state."""
        self.root = root

        # Configure the main window.
        self.root.title("Phaidra DAQ and Monitor")

        # Set a reasonable initial window size.
        self.root.geometry("1000x700")

        # Set a reasonable minimum size.
        self.root.minsize(700, 500)

        # Allow the user to resize the window with the mouse.
        self.root.resizable(True, True)

        # Store the current acquisition thread and stop signal.
        self.acquisition_thread = None
        self.stop_event = threading.Event()

        # Store the current serial port and output file path.
        self.serial_connection = None
        self.output_file = None

        # Store GUI status text.
        self.status_var = tk.StringVar(value="Stopped")
        self.file_var = tk.StringVar(value="No active file")

        # Create the GUI controls.
        tk.Label(
            self.root,
            text="Phaidra DAQ and Monitor",
            font=("Helvetica", 18, "bold"),
        ).pack(pady=(20, 10))

        # Create a frame for the status line.
        status_frame = tk.Frame(self.root)
        status_frame.pack(pady=5)

        # Create the static "Status:" label.
        tk.Label(
            status_frame,
            text="Status: ",
            font=("Helvetica", 12, "bold"),
        ).pack(side=tk.LEFT)

        # Create the dynamic status label.
        tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=("Helvetica", 12),
        ).pack(side=tk.LEFT, padx=(5, 0))

        # Create a frame for the status line.
        file_frame = tk.Frame(self.root)
        file_frame.pack(pady=5)

        # Create the static "Output file:" label.
        tk.Label(
            file_frame,
            text="Output file: ",
            font=("Helvetica", 12, "bold"),
        ).pack(side=tk.LEFT)

        # Create the dynamic file label.
        tk.Label(
            file_frame,
            textvariable=self.file_var,
            font=("Helvetica", 12),
        ).pack(side=tk.LEFT, padx=(5, 0))

        # Create and enable the START button.
        self.start_button = tk.Button(
            self.root,
            text="START",
            width=15,
            height=2,
            command=self.start_acquisition,
        )
        self.start_button.pack(pady=5)

        # Create the STOP button and keep it disabled initially.
        self.stop_button = tk.Button(
            self.root,
            text="STOP",
            width=15,
            height=2,
            command=self.stop_acquisition,
            state=tk.DISABLED,
        )
        self.stop_button.pack(pady=5)

        # Create the contact information shown at the bottom of the window.
        tk.Label(
             self.root,
             text="For problems/questions contact Lorenzo Pezzotti at lorenzo.pezzotti@psi.ch",
             font=("Helvetica", 10),
        ).pack(side=tk.BOTTOM, pady=(10, 15))

        # Make the window close safely.
        self.root.protocol("WM_DELETE_WINDOW", self.close_application)

    def create_output_file(self):
        """Create a new timestamped data file for the current acquisition."""
        # Use the current local date and time as the acquisition start time.
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Build a filename such as phaidra_data_20260928_145500.txt.
        filename = f"{FILE_PREFIX}_{timestamp}.txt"

        # Create the file in the current working directory.
        path = Path.cwd() / filename
        path.touch(exist_ok=False)

        # Store the path so the acquisition thread can append data to it.
        self.output_file = path

    def find_logger(self):
        """Search available serial ports and return the FT232R logger port."""
        # Get all serial ports currently visible to the operating system.
        ports = list_ports.comports()

        # First search by the exact USB VID/PID of the logger.
        for port in ports:
            if port.vid == LOGGER_VID and port.pid == LOGGER_PID:
                return port.device

        # Use a fallback search based on common FTDI/USB serial naming.
        for port in ports:
            device = (port.device or "").lower()
            description = (port.description or "").lower()

            if "usbserial" in device or "ft232" in description:
                return port.device

        # Return None when no suitable logger is found.
        return None

    def start_acquisition(self):
        """Start the logger acquisition thread."""
        # Ignore START presses while an acquisition is already running.
        if self.acquisition_thread and self.acquisition_thread.is_alive():
            return

        # Reset the output file reference for the new acquisition.
        self.output_file = None

        # Clear any previous stop request.
        self.stop_event.clear()

        # Update the GUI for the running state.
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("Searching for logger...")
        #self.file_var.set(f"Connecting to logger...")

        # Start the blocking serial work in a background thread.
        self.acquisition_thread = threading.Thread(
            target=self.acquire_data,
            daemon=True,
        )
        self.acquisition_thread.start()

    def acquire_data(self):
        """Connect to the logger and save each received line to the file."""
        serial_connection = None

        try:
            # Find the logger USB serial port.
            port_name = self.find_logger()

            if port_name is None:
                self.set_status("Logger not found")
                self.show_error(
                    "Logger not found.\n\n"
                    "Check the USB connection and press START again."
                )
                return

            # Open the serial connection using the known logger settings.
            serial_connection = serial.Serial(
                port=port_name,
                baudrate=BAUDRATE,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=READ_TIMEOUT,
            )

            # Create the output file only after the logger connection succeeds.
            try:
                # Create the output file only after the logger connection succeeds.
                self.create_output_file()
            except FileExistsError:
                self.set_status("File error")
                self.show_error("The output file already exists.")
                return
            except OSError as error:
               self.set_status("File error")
               self.show_error(f"Cannot create output file:\n\n{error}")
               return

            # Update the GUI with the newly created file name.
            self.root.after(
                 0,
                 lambda: self.file_var.set(f"File: {self.output_file.name}"),
            )

            # Keep a reference so STOP can expose the connection state.
            self.serial_connection = serial_connection

            # Tell the GUI that acquisition is active.
            self.set_status(f"Acquiring from {port_name}")

            # Open the timestamped output file in append mode.
            with self.output_file.open("a", encoding="utf-8") as data_file:
                # Read until STOP is pressed.
                while not self.stop_event.is_set():
                    raw_data = serial_connection.readline()

                    # Continue waiting when no complete line is available yet.
                    if not raw_data:
                        continue

                    # Decode the logger output while preserving unexpected bytes.
                    line = raw_data.decode("ascii", errors="replace").rstrip("\r\n")

                    # Ignore empty lines.
                    if not line:
                        continue

                    # Write exactly one logger line to the output file.
                    data_file.write(line + "\n")

                    # Flush immediately so data is physically handed to the OS
                    # instead of remaining in Python's file buffer.
                    data_file.flush()

        except serial.SerialException as error:
            # Report serial communication failures.
            self.set_status("Serial error")
            self.show_error(f"Serial communication error:\n\n{error}")

        except OSError as error:
            # Report file-system and device I/O failures.
            self.set_status("I/O error")
            self.show_error(f"I/O error:\n\n{error}")

        except Exception as error:
            # Catch unexpected errors to make debugging easier.
            self.set_status("Unexpected error")
            self.show_error(f"Unexpected error:\n\n{error}")

        finally:
            # Always close the serial port when acquisition ends.
            if serial_connection is not None and serial_connection.is_open:
                serial_connection.close()

            # Clear the shared serial connection reference.
            self.serial_connection = None

            # Restore the GUI controls on the main GUI thread.
            self.root.after(0, self.acquisition_finished)

    def stop_acquisition(self):
        """Request acquisition stop and allow the serial read to finish."""
        # Signal the acquisition thread to stop at the next read timeout.
        self.stop_event.set()

        # Update the GUI immediately.
        self.status_var.set("Stopping...")

    def acquisition_finished(self):
        """Restore the GUI to the stopped state after acquisition ends."""
        # Re-enable START and disable STOP.
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

        # Display the final stopped state.
        self.status_var.set("Stopped")

    def set_status(self, text):
        """Safely update the GUI status from the acquisition thread."""
        # Tkinter widgets must be updated from the main GUI thread.
        self.root.after(0, lambda: self.status_var.set(text))

    def show_error(self, text):
        """Safely display an error dialog from the acquisition thread."""
        # Tkinter dialogs must also run on the main GUI thread.
        self.root.after(
            0,
            lambda: messagebox.showerror("PhaiDRA", text),
        )

    def close_application(self):
        """Stop acquisition, close resources, and terminate the GUI."""
        # Request the acquisition thread to stop.
        self.stop_event.set()

        # Wait briefly for the acquisition thread to finish.
        if self.acquisition_thread and self.acquisition_thread.is_alive():
            self.acquisition_thread.join(timeout=2)

        # Close the serial connection if it is still open.
        if self.serial_connection is not None and self.serial_connection.is_open:
            self.serial_connection.close()

        # Close the GUI.
        self.root.destroy()


def main():
    """Create the Tkinter application and start the GUI event loop."""
    root = tk.Tk()

    # Create the application object and start the GUI.
    PhaiDRAApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
