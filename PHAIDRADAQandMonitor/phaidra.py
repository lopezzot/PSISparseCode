#!/usr/bin/env python3

"""
Simple PhaiDRA logger acquisition GUI.

The program:
1. Searches for the FT232R USB serial logger when START is pressed.
2. Opens the USB serial connection.
3. Creates a timestamped output file after a successful connection.
4. Reads incoming logger lines at 9600 baud.
5. Appends each received line to the current output file.
6. Creates monitoring plots on the GUI
7. Stops acquisition and closes the serial port when STOP is pressed.
"""

import threading
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

import serial
from serial.tools import list_ports

import queue

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates


# Serial communication settings used by the logger.
BAUDRATE = 9600
READ_TIMEOUT = 1

# FTDI FT232R USB UART identifiers observed for the logger.
LOGGER_VID = 0x0403
LOGGER_PID = 0x6001

# These are the input channels (3.7,9,10) on the logger.
CHANNEL_FIELDS = {
    1: 3,
    5: 7,
    7: 9,
    8: 10,
}

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

        # Store parsed logger data exchanged between the acquisition thread and GUI thread.
        self.data_queue = queue.Queue() # the queue object is shared between the master and worker thread

        # Store timestamps and values for each monitored channel.
        self.channel_data = {
            1: {"times": [], "values": []},
            5: {"times": [], "values": []},
            7: {"times": [], "values": []},
            8: {"times": [], "values": []},
        }
        
        # Store the Matplotlib axes and line objects for each monitored channel.
        self.channel_axes = {}
        self.channel_lines = {}

        # Store the current serial port and output file path.
        self.serial_connection = None
        self.output_file = None

        # Store the acquisition start time.
        self.acquisition_start_time = None

        # Store the scheduled GUI update callback.
        self.elapsed_after_id = None

        # Store GUI status text.
        self.status_var = tk.StringVar(value="Stopped")
        self.file_var = tk.StringVar(value="No active file")

        # Store the acquisition start time and elapsed time shown in the GUI.
        self.start_time_var = tk.StringVar(value="Not started")
        self.elapsed_time_var = tk.StringVar(value="00:00:00")

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

        # Create a frame for the acquisition timing information.
        timing_frame = tk.Frame(self.root)
        timing_frame.pack(pady=5)

        # Create the acquisition start time label.
        tk.Label(
            timing_frame,
            text="Acquisition start time:",
            font=("Helvetica", 12),
        ).pack(side=tk.LEFT)

        # Display the acquisition start time.
        tk.Label(
            timing_frame,
            textvariable=self.start_time_var,
            font=("Helvetica", 12),
        ).pack(side=tk.LEFT, padx=(5, 20))

        # Create the elapsed time label.
        tk.Label(
            timing_frame,
            text="Acquisition duration:",
            font=("Helvetica", 12),
        ).pack(side=tk.LEFT)

        # Display the elapsed acquisition time.
        tk.Label(
            timing_frame,
            textvariable=self.elapsed_time_var,
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

        self.create_plots()

        # Start the periodic GUI update loop.
        self.root.after(100, self.process_data_queue)

    def create_plots(self):
        """Create the four monitoring plots and embed them in the GUI."""

        # Create the frame that will contain the Matplotlib figure.
        plot_frame = tk.Frame(self.root)
        plot_frame.pack(
            fill=tk.BOTH,
            expand=True,
            padx=10,
            pady=10,
        )

        # Create one Matplotlib figure with four subplots.
        self.figure = Figure(figsize=(10, 6))
        axes = self.figure.subplots(2, 2)

        # Define the monitored channels and their subplot positions.
        channel_positions = {
            1: axes[0, 0],
            5: axes[0, 1],
            7: axes[1, 0],
            8: axes[1, 1],
        }

        # Create one plot for each monitored channel.
        for channel, axis in channel_positions.items():
            axis.set_title(f"Channel {channel}")
            axis.set_ylabel("Counts")
            axis.grid(True)

            # Automatically choose a reasonable number of date/time ticks.
            locator = mdates.AutoDateLocator(
                minticks=3,
                maxticks=5,
            )

            # Use a compact date/time representation.
            formatter = mdates.ConciseDateFormatter(locator)

            # Apply the locator and formatter to the X axis.
            axis.xaxis.set_major_locator(locator)
            axis.xaxis.set_major_formatter(formatter)

            # Rotate the X-axis labels slightly for better readability.
            axis.tick_params(axis="x", labelrotation=30)

            # Create an empty line that will be updated later.
            line, = axis.plot([], [])

            self.channel_axes[channel] = axis
            self.channel_lines[channel] = line

        # Improve spacing between the four plots.
        self.figure.tight_layout()

        # Embed the Matplotlib figure inside the Tkinter window.
        self.canvas = FigureCanvasTkAgg(
            self.figure,
            master=plot_frame,
        )

        self.canvas.draw()

        # Make the canvas expand with the window.
        self.canvas.get_tk_widget().pack(
            fill=tk.BOTH,
            expand=True,
        )
    def parse_logger_line(self, line):
        """Parse one logger line and extract the timestamp and monitored channels."""

        # Split the ASCII line into individual fields.
        fields = line.split()

        # Ignore malformed lines.
        if len(fields) < 15:
            return None

        try:
            # Parse the date and time reported by the logger.
            timestamp = datetime.strptime(
                f"{fields[1]} {fields[2]}",
                "%d.%m.%y %H:%M:%S",
            )

            # Extract the requested channel counts.
            channel_values = {
                channel: int(fields[index])
                for channel, index in CHANNEL_FIELDS.items()
            }

            return timestamp, channel_values

        except (ValueError, IndexError):
            # Ignore lines that cannot be parsed.
            return None

    def process_data_queue(self):
        """Process new logger data and update all monitoring plots."""

        # Process all data currently waiting in the queue.
        while not self.data_queue.empty():
            timestamp, channel_values = self.data_queue.get() # note that get() removes the data from the queue

            # Add the new data point to every monitored channel.
            for channel, value in channel_values.items():
                self.channel_data[channel]["times"].append(timestamp)
                self.channel_data[channel]["values"].append(value)

        # Update the plots if new data is available.
        if any(
            self.channel_data[channel]["times"]
            for channel in CHANNEL_FIELDS
        ):
            self.update_plots()

        # Schedule the next queue check.
        self.root.after(100, self.process_data_queue)

    def update_plots(self):
        """Update all monitoring plots with the latest acquisition data."""

        # Update each monitored channel.
        for channel in CHANNEL_FIELDS:
            times = self.channel_data[channel]["times"]
            values = self.channel_data[channel]["values"]

            # Update the corresponding Matplotlib line.
            self.channel_lines[channel].set_data(times, values)

            # Automatically adjust the plot limits.
            self.channel_axes[channel].relim()
            self.channel_axes[channel].autoscale_view()

        # Redraw the complete figure.
        self.canvas.draw_idle()

    def reset_plots(self):
        """Clear all monitoring data and reset the four plots."""

        # Clear stored data for every monitored channel.
        for channel in CHANNEL_FIELDS:
            self.channel_data[channel]["times"].clear()
            self.channel_data[channel]["values"].clear()

            # Remove all data from the corresponding plot line.
            self.channel_lines[channel].set_data([], [])

            # Reset the axes.
            self.channel_axes[channel].relim()
            self.channel_axes[channel].autoscale_view()

        # Redraw the empty plots.
        self.canvas.draw_idle()

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

        # Clear the previous monitoring data.
        self.reset_plots()

        # Reset the output file reference for the new acquisition.
        self.output_file = None

        # Clear any previous stop request.
        self.stop_event.clear()

        # Update the GUI for the running state.
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("Searching for logger...")

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

            # Store the acquisition start time after the logger connection succeeds.
            self.acquisition_start_time = datetime.now()

            # Update the acquisition start time shown in the GUI.
            start_time = self.acquisition_start_time.strftime("%d/%m/%Y %H:%M:%S")

            self.root.after(
                0,
                lambda: self.start_time_var.set(start_time),
            )

            # Reset the elapsed acquisition time.
            self.root.after(
                0,
                lambda: self.elapsed_time_var.set("00:00:00"),
            )

            # Start updating the elapsed acquisition time every second.
            self.root.after(0, self.update_acquisition_time)

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

                    # Parse the received logger line for monitoring data.
                    parsed_data = self.parse_logger_line(line)

                    # Add valid parsed data to the GUI queue.
                    if parsed_data is not None:
                        self.data_queue.put(parsed_data)

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

    def update_acquisition_time(self):
        """Update the elapsed acquisition time once per second."""

        # Stop updating if there is no active acquisition.
        if self.acquisition_start_time is None:
            return

        # Calculate the elapsed acquisition time.
        elapsed = datetime.now() - self.acquisition_start_time

        # Convert the elapsed time to total seconds.
        total_seconds = int(elapsed.total_seconds())

        # Calculate hours, minutes, and seconds.
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        # Update the elapsed time shown in the GUI.
        self.elapsed_time_var.set(
            f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        )

        # Schedule the next update one second later.
        self.elapsed_after_id = self.root.after(
            1000,
            self.update_acquisition_time,
        )

    def acquisition_finished(self):
        """Restore the GUI to the stopped state after acquisition ends."""
        # Cancel the periodic elapsed-time update.
        if self.elapsed_after_id is not None:
            self.root.after_cancel(self.elapsed_after_id)
            self.elapsed_after_id = None

        # Clear the acquisition start time.
        self.acquisition_start_time = None

        # Reset the elapsed time display.
        self.elapsed_time_var.set("00:00:00")
        
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

        print("Terminating Phaidra DAQ and Monitor system. Bye.")


def main():
    """Create the Tkinter application and start the GUI event loop."""
    root = tk.Tk()

    # Create the application object and start the GUI.
    PhaiDRAApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
