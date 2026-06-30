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

# 4. Load and parse WENDI neutron detector data
df_wendi = pd.read_csv(
    "SwissFEL_Passive.log", 
    skiprows=9, 
    sep=r'\s+',
    names=['date', 'time', 'val_int', 'unit_int', 'val_ext', 'unit_ext', 'status'],
    encoding='latin-1'
)

# Combine date and time columns into a single string column
df_wendi['datetime_str'] = df_wendi['date'] + ' ' + df_wendi['time']

# Convert to datetime objects using the correct 2-digit year format (%y.%m.%d)
df_wendi['datetime'] = pd.to_datetime(df_wendi['datetime_str'], format='%y.%m.%d %H:%M:%S')

# Localize to Europe/Zurich timezone (matching the machine diagnostics)
df_wendi['datetime'] = df_wendi['datetime'].dt.tz_localize('Europe/Zurich', ambiguous='infer')

# --- Updated Plotting: 3 Subplots sharing the same X axis ---
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True, figsize=(10, 11), dpi=150)
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

# 1. Top Subplot: Beam Charge
ax1.plot(df['datetime'], df['charge_pC'], color='#1f77b4', linewidth=1.5, label='Beam Charge')
ax1.fill_between(df['datetime'], df['charge_pC'], color='#1f77b4', alpha=0.15)
ax1.set_ylabel('Average Charge (pC)', fontsize=11, labelpad=10)
ax1.set_ylim(-5, 230)
ax1.set_title('SwissFEL Diagnostics & WENDI Neutron Dose Rate - 2025-07-01', fontsize=14, fontweight='bold', pad=15)
ax1.grid(True, which='major', linestyle='--', alpha=0.7)
ax1.minorticks_on()
ax1.grid(True, which='minor', linestyle=':', alpha=0.4)

# 2. Middle Subplot: Machine Frequency
ax2.plot(df['datetime'], df['frequency_Hz'], color='#2ca02c', linewidth=1.5, label='Repetition Rate')
ax2.fill_between(df['datetime'], df['frequency_Hz'], color='#2ca02c', alpha=0.15)
ax2.set_ylabel('Frequency (Hz)', fontsize=11, labelpad=10)
ax2.grid(True, which='major', linestyle='--', alpha=0.7)
ax2.grid(True, which='minor', linestyle=':', alpha=0.4)

# 3. Bottom Subplot: WENDI Neutron Dose Rate (Value ext.)
ax3.plot(df_wendi['datetime'], df_wendi['val_ext'], color='#9467bd', linewidth=1.2, label='Neutron Dose Rate')
ax3.fill_between(df_wendi['datetime'], df_wendi['val_ext'], color='#9467bd', alpha=0.15)
ax3.set_xlabel('Local Time (Europe/Zurich)', fontsize=11, labelpad=10)
ax3.set_ylabel('Neutron Dose Rate (µSv/h)', fontsize=11, labelpad=10)
# Set Y-axis limit to 500 to handle high outliers and prevent plot squashing
ax3.set_ylim(-10, 500) 
ax3.grid(True, which='major', linestyle='--', alpha=0.7)
ax3.minorticks_on()
ax3.grid(True, which='minor', linestyle=':', alpha=0.4)

# Format X-axis with local time and 1-hour interval ticks (applied to the bottom plot)
ax3.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M', tz=df['datetime'].dt.tz))
ax3.xaxis.set_major_locator(mdates.HourLocator(interval=1))

# Automatically adjust layout to prevent label clipping
plt.tight_layout()

# Save and export the final 3-panel synced plot
output_filename = "swissfel_diagnostics_and_wendi.png"
plt.savefig(output_filename, dpi=300)

plt.show()
# --- New Addition: Advanced filtering for true active plateaus (wider buffer & drop removal) ---

# Align datetime precision to microseconds ('us') to prevent MergeError
df['datetime'] = df['datetime'].dt.as_unit('us')
df_wendi['datetime'] = df_wendi['datetime'].dt.as_unit('us')

# Sort machine logs
df = df.sort_values('datetime')

# Create a wider stability window (shifting by 1 and 2 positions to clear longer transients)
df['prev_freq_1'] = df['frequency_Hz'].shift(1)
# 4 minutes before
df['prev_freq_2'] = df['frequency_Hz'].shift(2)  
df['next_freq_1'] = df['frequency_Hz'].shift(-1)
# 4 minutes after
df['next_freq_2'] = df['frequency_Hz'].shift(-2)  

# Sort WENDI data
df_wendi = df_wendi.sort_values('datetime')

# Synchronize DataFrames with expanded machine state columns
df_analysis = pd.merge_asof(
    df_wendi,
    df[['datetime', 'frequency_Hz', 'prev_freq_1', 'prev_freq_2', 'next_freq_1', 'next_freq_2']],
    on='datetime',
    direction='nearest'
)

# Configuration
target_frequencies = [10, 25]
tolerance = 0.5

# Threshold to reject beam trips/interruptions when the machine is supposed to be ON.
# Adjust this value if your background/noise level is different.
dose_threshold = 20.0  # in µSv/h

print("\n" + "="*75)
print("  WENDI NEUTRON DOSE RATE ANALYSIS (TRUE ACTIVE PLATEAUS)")
print("="*75)

for freq in target_frequencies:
    # 1. Time mask: requiring a 4-minute stable frequency window around the data point
    time_mask = (
        ((df_analysis['frequency_Hz'] - freq).abs() < tolerance) &
        ((df_analysis['prev_freq_1'] - freq).abs() < tolerance) &
        ((df_analysis['prev_freq_2'] - freq).abs() < tolerance) &
        ((df_analysis['next_freq_1'] - freq).abs() < tolerance) &
        ((df_analysis['next_freq_2'] - freq).abs() < tolerance)
    )
    
    total_stable_seconds = time_mask.sum()
    
    # 2. Active mask: combining time stability with the dose threshold to remove beam drops
    active_mask = time_mask & (df_analysis['val_ext'] > dose_threshold)
    dose_rates_active = df_analysis.loc[active_mask, 'val_ext']
    
    n_points = len(dose_rates_active)
    
    if n_points > 0:
        mean_dose = dose_rates_active.mean()
        median_dose = dose_rates_active.median()
        std_dose = dose_rates_active.std() if n_points > 1 else 0.0
        sem_dose = dose_rates_active.sem() if n_points > 1 else 0.0
        
        print(f"\n[+] Frequency Regime: {freq} Hz")
        print(f"    Total seconds in stable window       : {total_stable_seconds} s")
        print(f"    Active beam seconds (> {dose_threshold} µSv/h) : {n_points} s")
        print(f"    Mean Dose Rate (Active Beam)        : {mean_dose:.3f} ± {sem_dose:.3f} µSv/h (SEM)")
        print(f"    Median Dose Rate (Robust Peak)      : {median_dose:.3f} µSv/h")
        print(f"    Data Standard Deviation (σ)         : {std_dose:.3f} µSv/h")
    else:
        print(f"\n[-] Frequency Regime: {freq} Hz")
        print(f"    No data points passed the active plateau criteria.")
print("="*75 + "\n")
