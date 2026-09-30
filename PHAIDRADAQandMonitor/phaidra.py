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

import math
import shutil

# Serial communication settings used by the logger.
BAUDRATE = 9600
READ_TIMEOUT = 1

# FTDI FT232R USB UART identifiers observed for the logger.
LOGGER_VID = 0x0403
LOGGER_PID = 0x6001

# These are the input channels (3.7,9,10) on the logger.
CHANNEL_FIELDS = {
    1: 3, # gamma detector
    5: 7, # yellow neutron
    7: 9, # white neutron
    8: 10,# current
}

# Prefix used for acquisition files.
FILE_PREFIX = "phaidra_data"

# Destination directory for daily backup files.
BACKUP_DIR = Path("/path/to/drive") # this is where the backup disk is reachable


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
        self.root.minsize(1200, 850)

        # Allow the user to resize the window with the mouse.
        self.root.resizable(True, True)

        # Store the current acquisition thread and stop signal.
        self.acquisition_thread = None
        self.stop_event = threading.Event()

        # Store a request to rotate the daily output file.
        self.rotate_file_event = threading.Event()
        
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
        self.plot_axes = {}
        self.plot_lines = {}

        # Store the current serial port and output file path.
        self.serial_connection = None
        self.output_file = None

        # Store the computer calendar date associated with the current daily file.
        self.current_day = None

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

        # Create the header frame.
        header_frame = tk.Frame(self.root)
        header_frame.pack(
            fill=tk.X,
            padx=15,
            pady=(10, 5),
        )

        # Load the PSI logo.
        self.psi_logo = tk.PhotoImage(file="logo_psi.png")
        # Reduce the logo size.
        self.psi_logo = self.psi_logo.subsample(5, 5)

        # Create the PSI logo label.
        logo_label = tk.Label(
            header_frame,
            image=self.psi_logo,
        )
        logo_label.pack(
            side=tk.LEFT,
            anchor="nw",
        )

        # Create the application title.
        title_label = tk.Label(
            header_frame,
            text="Phaidra DAQ and Monitor",
            font=("Helvetica", 18, "bold"),
        )

        # Keep the title centered in the header.
        title_label.pack(
            side=tk.LEFT,
            expand=True,
            padx=10,
        )

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
            font=("Helvetica", 12, "bold"),
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
            font=("Helvetica", 12, "bold"),
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
        """Create the monitoring plots and embed them in the GUI."""

        # Create the frame that will contain the Matplotlib figure.
        plot_frame = tk.Frame(self.root)
        plot_frame.pack(
            fill=tk.BOTH,
            expand=True,
            padx=10,
            pady=10,
        )

        # Create one Matplotlib figure with three subplots.
        self.figure = Figure(figsize=(12, 4))
        axes = self.figure.subplots(1, 3)

        # Define the monitoring plots and their titles.
        plot_definitions = {
            "ratio_75": (
                axes[0],
                "Ratio of channel 7 and 5",
                "Ratio",
            ),
            "uncertainty_75": (
                axes[1],
                "Relative uncertainty of 7/5",
                "Relative uncertainty",
            ),
            "ratio_78": (
                axes[2],
                "Ratio of channel 7 and 8",
                "Ratio",
                ),
        }

        # Create one plot for each monitored quantity.
        for plot_name, (axis, title, ylabel) in plot_definitions.items():
            axis.set_title(title)
            axis.set_ylabel(ylabel)
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

            self.plot_axes[plot_name] = axis
            self.plot_lines[plot_name] = line

        # Improve spacing between the three plots.
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

        # Read the raw channel data used to calculate the monitoring quantities.
        times = self.channel_data[7]["times"]
        values_5 = self.channel_data[5]["values"]
        values_7 = self.channel_data[7]["values"]
        values_8 = self.channel_data[8]["values"]

        # Calculate the three derived quantities.
        ratio_75 = []
        relative_uncertainty_75 = []
        ratio_78 = []

        for value_5, value_7, value_8 in zip(
            values_5,
            values_7,
            values_8,
        ):
            # Calculate 7/5.
            if value_5 > 0:
                ratio = value_7 / value_5
            else:
                ratio = float("nan")

            ratio_75.append(ratio)

            # Calculate the relative uncertainty of 7/5.
            # Assume independent Poisson counting statistics.
            if value_5 > 0 and value_7 > 0:
                relative_uncertainty = math.sqrt(
                    1 / value_7 + 1 / value_5
                )
            else:
                relative_uncertainty = float("nan")

            relative_uncertainty_75.append(relative_uncertainty)

            # Convert channel 8 counts to mA.
            current_mA = value_8 / 1e6

            # Calculate 7/8 after converting channel 8 to mA.
            if current_mA > 0:
                ratio = value_7 / current_mA
            else:
                ratio = float("nan")

            ratio_78.append(ratio)

        # Update the 7/5 ratio plot.
        self.plot_lines["ratio_75"].set_data(
            times,
            ratio_75,
        )

        self.plot_axes["ratio_75"].relim()
        self.plot_axes["ratio_75"].autoscale_view()

        # Update the relative uncertainty plot.
        self.plot_lines["uncertainty_75"].set_data(
            times,
            relative_uncertainty_75,
        )

        self.plot_axes["uncertainty_75"].relim()
        self.plot_axes["uncertainty_75"].autoscale_view()

        # Update the 7/8 ratio plot.
        self.plot_lines["ratio_78"].set_data(
            times,
            ratio_78,
        )

        self.plot_axes["ratio_78"].relim()
        self.plot_axes["ratio_78"].autoscale_view()

        # Redraw the complete figure.
        self.canvas.draw_idle()

    def reset_plots(self):
        """Clear all monitoring data and reset the monitoring plots."""

        # Clear stored raw data for every acquired channel.
        for channel in CHANNEL_FIELDS:
            self.channel_data[channel]["times"].clear()
            self.channel_data[channel]["values"].clear()

        # Remove all data from the monitoring plot lines.
        for plot_name in self.plot_lines:
            self.plot_lines[plot_name].set_data([], [])

            # Reset the corresponding axes.
            self.plot_axes[plot_name].relim()
            self.plot_axes[plot_name].autoscale_view()

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

        # Clear any previous daily file rotation request.
        self.rotate_file_event.clear()

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

            # Store the current computer calendar date for the daily file.
            self.current_day = datetime.now().date()

            # Start monitoring the computer calendar date.
            self.root.after(1000, self.check_day_change)

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

            # Open the current output file in append mode.
            data_file = self.output_file.open(
                "a",
                encoding="utf-8",
            )

            try:
                # Read until STOP is pressed.
                while not self.stop_event.is_set():

                    if self.rotate_file_event.is_set():
                        old_file = self.output_file
                        old_file_name = old_file.name

                        data_file.close()

                        # Copy the closed daily file to the backup drive.
                        shutil.copy2(old_file, BACKUP_DIR / old_file.name)

                        self.create_output_file()
                        data_file = self.output_file.open("a", encoding="utf-8")

                        new_file_name = self.output_file.name

                        print(
                            f"Midnight reached: closed {old_file_name}, "
                            f"opened {new_file_name}"
                        )

                        self.rotate_file_event.clear()

                        self.root.after(
                            0,
                            lambda name=new_file_name: self.file_var.set(
                            f"Output file: {name}"
                            )
                        )

                    # Read one line from the logger.
                    raw_data = serial_connection.readline()

                    # Continue waiting when no complete line is available yet.
                    if not raw_data:
                        continue

                    # Decode the logger output while preserving unexpected bytes.
                    line = raw_data.decode(
                        "ascii",
                        errors="replace",
                    ).rstrip("\r\n")

                    # Ignore empty lines.
                    if not line:
                        continue

                    # Write exactly one logger line to the current daily file.
                    data_file.write(line + "\n")

                    # Flush immediately so the data is available on disk.
                    data_file.flush()

                    # Parse the received logger line for monitoring data.
                    parsed_data = self.parse_logger_line(line)

                    # Add valid parsed data to the GUI queue.
                    if parsed_data is not None:
                         self.data_queue.put(parsed_data)

            finally:
                # Always close the current output file.
                if not data_file.closed:
                    data_file.close()

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

        # Clear the current daily acquisition date.
        self.current_day = None

        # Clear any pending daily file rotation request.
        self.rotate_file_event.clear()

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

    def check_day_change(self):
        """Check whether the computer has entered a new calendar day."""

        # Stop checking when no acquisition is active.
        if self.current_day is None:
            return

        # Read the current date from the computer clock.
        today = datetime.now().date()

        # Request a daily file rotation when the calendar day changes.
        if today != self.current_day:
            # Request the worker thread to rotate the output file.
            self.rotate_file_event.set()

            # Update the current day immediately.
            self.current_day = today

            # Clear the monitoring plots for the new day.
            self.reset_plots()

        # Check again one second later.
        self.root.after(1000, self.check_day_change)
    
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
