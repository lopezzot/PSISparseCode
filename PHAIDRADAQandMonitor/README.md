# PGAIDRA DAQ and Monitor

Simple Python GUI application for acquiring text data from the Phaidra logger over USB/serial.

The application uses:

- Python 3
- Tkinter for the GUI
- `pyserial` for USB/serial communication
- a virtual environment (`venv`) for dependency isolation

## 1. Requirements

The logger must appear as a serial USB device.

For the logger used during development, the USB interface is:

```text
FT232R USB UART
VID: 0403
PID: 6001
```

The logger is currently configured for:

```text
9600 baud
8 data bits
no parity
1 stop bit
```

## 2. Create the virtual environment before execution

Open a terminal and move to the project directory:

```bash
cd /path/to/phaidra
```

Create the virtual environment:

```bash
python3 -m venv .venv
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

After activation, the shell prompt should show something similar to:

```text
(.venv) user@computer:~/phaidra$
```

## 3. Install the Python dependency

Upgrade `pip`:

```bash
python -m pip install --upgrade pip
```

Install `pyserial` and `matplotlib`:

```bash
python -m pip install pyserial
python -m pip install matplotlib
```

Tkinter is normally available with the standard Python installation.

On Debian/Ubuntu Linux, if Tkinter is missing, install it with:

```bash
sudo apt install python3-tk
```

## 4. Run the program

With the virtual environment activated:

```bash
python phaidra.py
```

The GUI opens with two buttons:

- `START`
- `STOP`

## 5. Start an acquisition

Press `START`.

The program:

1. Creates a new file using the START date and time.
2. Uses the filename format:

```text
phaidra_data_YYYYMMDD_HHMMSS.txt
```

For example:

```text
phaidra_data_20260928_145500.txt
```

3. Searches for the FT232R USB logger.
4. Opens the serial port at 9600 baud.
5. Reads incoming text lines.
6. Writes every received line to the file.
7. Flushes the file after every line.

The program does not add or modify the logger data. It stores the received line as text.

## 6. Stop an acquisition

Press `STOP`.

The program requests the acquisition thread to stop and closes the serial connection.

No new acquisition file is created until `START` is pressed again.

## 7. Where the data file is created

The output file is created in the directory from which the program is started.

For example:

```bash
cd ~/phaidra
python phaidra.py
```

The output file will be created inside:

```text
~/phaidra/
```
