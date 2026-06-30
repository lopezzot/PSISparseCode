import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 1. Load data from text files (skipping the '#array...' header row)
timestamps = np.loadtxt("../SwissFEL_currentdata/CurrentDataLog_SATMA01-DBPM040_Q1/start.txt", skiprows=1)
averages_charge = np.loadtxt("../SwissFEL_currentdata/CurrentDataLog_SATMA01-DBPM040_Q1/average.txt", skiprows=1)
averages_freq = np.loadtxt("../SwissFEL_frequencydata/FrequencyDataLog_SIN-TIMAST-TMA_Bunch-2-Appl-Freq-RB/average.txt", skiprows=1)

# 2. Create the unified pandas DataFrame
df = pd.DataFrame({
    'timestamp_ms': timestamps,
    'charge_pC': averages_charge,
    'frequency_Hz': averages_freq
})

# 3. Convert Unix timestamps (ms) to local datetime (Europe/Zurich)
df['datetime'] = pd.to_datetime(df['timestamp_ms'], unit='ms', utc=True)
df['datetime'] = df['datetime'].dt.tz_convert('Europe/Zurich')

# 4. Set up the subplots sharing the same X axis (Time)
fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(10, 8), dpi=150)
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

# --- Top Subplot: Beam Charge ---
ax1.plot(df['datetime'], df['charge_pC'], color='#1f77b4', linewidth=1.5, label='Beam Charge')
ax1.fill_between(df['datetime'], df['charge_pC'], color='#1f77b4', alpha=0.15)
ax1.set_ylabel('Average Charge per Bunch (pC)', fontsize=11, labelpad=10)
ax1.set_ylim(-5, 230)
ax1.set_title('SwissFEL Machine Diagnostics - 2025-07-01', fontsize=14, fontweight='bold', pad=15)

# Configure grids for top plot
ax1.grid(True, which='major', linestyle='--', alpha=0.7)
ax1.minorticks_on()
ax1.grid(True, which='minor', linestyle=':', alpha=0.4)

# --- Bottom Subplot: Machine Frequency ---
ax2.plot(df['datetime'], df['frequency_Hz'], color='#2ca02c', linewidth=1.5, label='Repetition Rate')
ax2.fill_between(df['datetime'], df['frequency_Hz'], color='#2ca02c', alpha=0.15)
ax2.set_xlabel('Local Time (Europe/Zurich)', fontsize=11, labelpad=10)
ax2.set_ylabel('Frequency (Hz)', fontsize=11, labelpad=10)

# Configure grids for bottom plot
ax2.grid(True, which='major', linestyle='--', alpha=0.7)
ax2.grid(True, which='minor', linestyle=':', alpha=0.4)

# 5. Format X-axis with local time and 1-hour interval ticks
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M', tz=df['datetime'].dt.tz))
ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))

# Automatically adjust spacing between plots to prevent overlap
plt.tight_layout()

# Save the final synced plots
output_filename = "swissfel_charge_and_frequency.png"
plt.savefig(output_filename, dpi=300)
plt.show()
