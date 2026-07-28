import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg') # Force matplotlib to use a non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# =============================================================================
# --- 1. DATA LOADING FUNCTIONS (Detector-Specific) ---
# =============================================================================

def load_machine_diagnostics(timestamp_path, charge_path, freq_path):
    """
    Loads SwissFEL machine diagnostics data and prepares stability shift windows.
    """
    timestamps = np.loadtxt(timestamp_path, skiprows=1)
    averages_charge = np.loadtxt(charge_path, skiprows=1)
    averages_freq = np.loadtxt(freq_path, skiprows=1)

    df = pd.DataFrame({
        'timestamp_ms': timestamps,
        'charge_pC': averages_charge,
        'frequency_Hz': averages_freq
    })

    # Convert Unix timestamps (ms) to local datetime (Europe/Zurich)
    df['datetime'] = pd.to_datetime(df['timestamp_ms'], unit='ms', utc=True)
    df['datetime'] = df['datetime'].dt.tz_convert('Europe/Zurich')
    df['datetime'] = df['datetime'].dt.as_unit('us')
    df = df.sort_values('datetime')

    # Create a wider stability window (shifting by 1 and 2 positions to clear longer transients)
    df['prev_freq_1'] = df['frequency_Hz'].shift(1)
    df['prev_freq_2'] = df['frequency_Hz'].shift(2)  # 4 minutes before
    df['next_freq_1'] = df['frequency_Hz'].shift(-1)
    df['next_freq_2'] = df['frequency_Hz'].shift(-2)  # 4 minutes after
    
    return df

def load_wendi_data(filepath):
    """
    Loads and parses WENDI passive neutron detector logs.
    """
    df_wendi = pd.read_csv(
        filepath, 
        skiprows=9, 
        sep=r'\s+',
        names=['date', 'time', 'val_int', 'unit_int', 'val_ext', 'unit_ext', 'status'],
        encoding='latin-1'
    )
    df_wendi['datetime_str'] = df_wendi['date'] + ' ' + df_wendi['time']
    df_wendi['datetime'] = pd.to_datetime(df_wendi['datetime_str'], format='%y.%m.%d %H:%M:%S')
    df_wendi['datetime'] = df_wendi['datetime'].dt.tz_localize('Europe/Zurich', ambiguous='infer')
    df_wendi['datetime'] = df_wendi['datetime'].dt.as_unit('us')
    
    return df_wendi.sort_values('datetime')

def load_nausicaa_data(file_list):
    """
    Loads and concatenates multiple NAUSICAA detector logs.
    Handles LabVIEW timestamps and time zone conversions.
    """
    df_list = []
    
    # Iterate through the provided file paths
    for filepath in file_list:
        df_temp = pd.read_csv(filepath, sep='\t')
        df_list.append(df_temp)
        
    # Concatenate all dataframes sequentially
    df_nausicaa = pd.concat(df_list, ignore_index=True)
    
    # Convert LabVIEW timestamp (seconds since 1904-01-01) to datetime
    df_nausicaa['datetime'] = pd.to_datetime(df_nausicaa['Seconds'], unit='s', origin='1904-01-01')
    
    # Localize to UTC (LabVIEW log baseline) and convert to Europe/Zurich
    df_nausicaa['datetime'] = df_nausicaa['datetime'].dt.tz_localize('UTC').dt.tz_convert('Europe/Zurich')
    df_nausicaa['datetime'] = df_nausicaa['datetime'].dt.as_unit('us')
    
    # Sort chronologically to ensure seamless transition between files
    return df_nausicaa.sort_values('datetime')

def load_lupin_data(filepath):
    """
    Loads LUPIN detector data using tab separation, converts timestamps,
    and filters out data points recorded before 07:00 AM local time.
    """
    # Load with tab separator to preserve column names with spaces
    df_lupin = pd.read_csv(filepath, sep='\t')
    
    # Convert LabVIEW timestamp (seconds since 1904-01-01) to datetime
    df_lupin['datetime'] = pd.to_datetime(df_lupin['Seconds'], unit='s', origin='1904-01-01')
    
    # Localize to UTC (LabVIEW log baseline) and convert to Europe/Zurich
    df_lupin['datetime'] = df_lupin['datetime'].dt.tz_localize('UTC').dt.tz_convert('Europe/Zurich')
    df_lupin['datetime'] = df_lupin['datetime'].dt.as_unit('us')
    
    # Filter: Keep only data from 07:00:00 onwards (drops hours 00:00 to 06:59)
    df_lupin = df_lupin[df_lupin['datetime'].dt.hour >= 7]
    
    return df_lupin.sort_values('datetime')

def load_drps_data(folder_path):
    """
    Loads DRPS detector data from a directory containing start.txt and average.txt.
    Matches the SwissFEL archiver data structure.
    """
    start_path = os.path.join(folder_path, "start.txt")
    avg_path = os.path.join(folder_path, "average.txt")

    # Load timestamps (ms) and corresponding average dose rate values
    timestamps = np.loadtxt(start_path, skiprows=1)
    averages = np.loadtxt(avg_path, skiprows=1)

    df = pd.DataFrame({
        'timestamp_ms': timestamps,
        'dose_rate': averages
    })

    # Convert Unix timestamps (ms) to local datetime (Europe/Zurich)
    df['datetime'] = pd.to_datetime(df['timestamp_ms'], unit='ms', utc=True)
    df['datetime'] = df['datetime'].dt.tz_convert('Europe/Zurich')
    df['datetime'] = df['datetime'].dt.as_unit('us')

    return df.sort_values('datetime')

# =============================================================================
# --- 2. GENERIC PLOTTING & ANALYSIS ENGINE ---
# =============================================================================

def analyze_and_plot_detector(df_det, df_mach, detector_name, dose_col, threshold, ylim_plot=[-10, 500], splits=None, baseline_range=("07:00", "08:00"), correction_factor=None):
    """
    Synchronizes any detector with machine logs, generates a synchronized 3-panel plot (handling optional time splits),
    and calculates statistical dose rates for stable frequency plateaus independently per split.
    """
    
    # First calculate the baseline dose using baseline_range as temporal range
    baseline_value = 0.0
    if baseline_range is not None:
        start_bg, end_bg = baseline_range
        start_time = pd.to_datetime(start_bg).time()
        end_time = pd.to_datetime(end_bg).time()
        
        mask_bg = (df_det['datetime'].dt.time >= start_time) & (df_det['datetime'].dt.time < end_time)
        if mask_bg.any():
            baseline_value = df_det.loc[mask_bg, dose_col].mean()
            print(f"\n[*] Baseline calculated for {detector_name} ({start_bg} - {end_bg}): {baseline_value:.3f} µSv/h")
        else:
            print(f"\n[-] Warning: could not calculate baseline for {detector_name} in interval {start_bg} - {end_bg}.")

    # -------------------------------------------------------------------------
    # PART A: Synchronized 3-Panel Plotting
    # -------------------------------------------------------------------------
    # Set the style globally BEFORE creating the subplots to keep the light grey borders
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True, figsize=(10, 11), dpi=150)

    # 1. Top Subplot: Beam Charge (from machine dataframe)
    ax1.plot(df_mach['datetime'], df_mach['charge_pC'], color='#1f77b4', linewidth=1.5, label='Beam Charge')
    ax1.fill_between(df_mach['datetime'], df_mach['charge_pC'], color='#1f77b4', alpha=0.15)
    ax1.set_ylabel('Average Charge per Bunch (pC)', fontsize=11, labelpad=10)
    ax1.set_ylim(-5, 230)
    ax1.set_title(f'SwissFEL Diagnostics & {detector_name.upper()} Dose Rate Synchronization', fontsize=14, fontweight='bold', pad=15)
    ax1.grid(True, which='major', linestyle='--', alpha=0.7)
    ax1.minorticks_on()
    ax1.grid(True, which='minor', linestyle=':', alpha=0.4)

    # 2. Middle Subplot: Machine Frequency (from machine dataframe)
    ax2.plot(df_mach['datetime'], df_mach['frequency_Hz'], color='#2ca02c', linewidth=1.5, label='Repetition Rate')
    ax2.fill_between(df_mach['datetime'], df_mach['frequency_Hz'], color='#2ca02c', alpha=0.15)
    ax2.set_ylabel('Frequency (Hz)', fontsize=11, labelpad=10)
    ax2.grid(True, which='major', linestyle='--', alpha=0.7)
    ax2.grid(True, which='minor', linestyle=':', alpha=0.4)

    # 3. Bottom Subplot: Detector Neutron Dose Rate (Handling Optional Position/Time Splits)
    if splits:
        last_time = None
        for split in splits:
            mask = pd.Series(True, index=df_det.index)
            if last_time is not None:
                mask &= (df_det['datetime'].dt.time >= last_time)
            if split["time_boundary"] is not None:
                t_bound = pd.to_datetime(split["time_boundary"]).time()
                mask &= (df_det['datetime'].dt.time < t_bound)
                last_time = t_bound
            
            df_sub = df_det[mask]
            ax3.plot(df_sub['datetime'], df_sub[dose_col], color=split["color"], linewidth=1.2, label=split["name"])
            ax3.fill_between(df_sub['datetime'], df_sub[dose_col], color=split["color"], alpha=0.15)
    else:
        # Standard fallback if no time splits are passed
        ax3.plot(df_det['datetime'], df_det[dose_col], color='#9467bd', linewidth=1.2, label=f'{detector_name} Dose Rate')
        ax3.fill_between(df_det['datetime'], df_det[dose_col], color='#9467bd', alpha=0.15)

    ax3.set_xlabel('Local Time (Europe/Zurich)', fontsize=11, labelpad=10)
    ax3.set_ylabel(f'Dose Rate (µSv/h)', fontsize=11, labelpad=10)
    ax3.set_ylim(ylim_plot) 
    ax3.grid(True, which='major', linestyle='--', alpha=0.7)
    ax3.minorticks_on()
    ax3.grid(True, which='minor', linestyle=':', alpha=0.4)
    ax3.legend(loc='upper right')

    # Format X-axis with local time and 1-hour ticks
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M', tz=df_mach['datetime'].dt.tz))
    ax3.xaxis.set_major_locator(mdates.HourLocator(interval=1))

    plt.tight_layout()
    # --- Save images inside the target directory ---
    output_dir = "MultiDetectorResults"
    os.makedirs(output_dir, exist_ok=True)
    output_filename = os.path.join(output_dir, f"swissfel_diagnostics_and_{detector_name.lower()}.png")
    # -----------------------------------------------
    plt.savefig(output_filename, dpi=300)
    plt.close(fig)

    # -------------------------------------------------------------------------
    # PART B: Dataset Synchronization & Stability Filtering
    # -------------------------------------------------------------------------
    # MODIFIED: Added 'charge_pC' to the df_mach column selection so it's available for filtering
    df_analysis = pd.merge_asof(
        df_det,
        df_mach[['datetime', 'frequency_Hz', 'charge_pC', 'prev_freq_1', 'prev_freq_2', 'next_freq_1', 'next_freq_2']],
        on='datetime',
        direction='nearest'
    )

    target_frequencies = [10, 25]
    tolerance = 0.5

    print("\n" + "="*75)
    print(f"  {detector_name.upper()} NEUTRON DOSE RATE ANALYSIS")
    print("="*75)

    # Internal helper function to avoid repeating stats code for time blocks
    def run_statistics(dataframe_selection, label_suffix=""):
        for freq in target_frequencies:
            # Time mask: requiring a 4-minute stable frequency window around the data point
            time_mask = (
                ((dataframe_selection['frequency_Hz'] - freq).abs() < tolerance) &
                ((dataframe_selection['prev_freq_1'] - freq).abs() < tolerance) &
                ((dataframe_selection['prev_freq_2'] - freq).abs() < tolerance) &
                ((dataframe_selection['next_freq_1'] - freq).abs() < tolerance) &
                ((dataframe_selection['next_freq_2'] - freq).abs() < tolerance)
            )
            
            total_stable_intervals = time_mask.sum()
            
            # Active mask explicitly requires a non-null bunch charge (> 190 pC) 
            # to filter out machine drops/interlocks during a stable frequency regime.
            active_mask = time_mask & (dataframe_selection[dose_col] > threshold) & (dataframe_selection['charge_pC'] > 190.0)
            dose_rates_active = dataframe_selection.loc[active_mask, dose_col]
            charge_active = dataframe_selection.loc[active_mask, 'charge_pC']
            
            n_points = len(dose_rates_active)
            display_label = f"{freq} Hz ({label_suffix})" if label_suffix else f"{freq} Hz"

            if n_points > 0:
                mean_dose = dose_rates_active.mean()
                median_dose = dose_rates_active.median()
                std_dose = dose_rates_active.std() if n_points > 1 else 0.0
                sem_dose = dose_rates_active.sem() if n_points > 1 else 0.0

                # Calculate mean charge for normalization
                mean_charge = charge_active.mean()

                # Calculate dose per burst in nSv (multiplying µSv by 1000)
                bursts_per_hour = freq * 3600.0
                dose_per_burst_nsv = (mean_dose * 1000.0) / bursts_per_hour
                sem_per_burst_nsv = (sem_dose * 1000.0) / bursts_per_hour

                # Calculate dose normalized to charge (nSv/pC)
                dose_per_pc = dose_per_burst_nsv / mean_charge
                sem_per_pc = sem_per_burst_nsv / mean_charge
                
                print(f"\n[+] Frequency Regime: {display_label}")
                print(f"    Total intervals in stable window     : {total_stable_intervals}")
                print(f"    Active beam intervals (> {threshold} µSv/h) : {n_points}")
                print(f"    Average Bunch Charge                 : {mean_charge:.2f} pC")
                print(f"    Mean Dose Rate (Active Beam)        : {mean_dose:.3f} ± {sem_dose:.3f} µSv/h (SEM)")
                print(f"    Mean Dose per Burst                  : {dose_per_burst_nsv:.5f} ± {sem_per_burst_nsv:.5f} nSv/burst")
                print(f"    Mean Dose per pC                     : {dose_per_pc:.5f} ± {sem_per_pc:.5f} nSv/pC")
                
                # --- Print baseline and net dose if calculated ---
                if baseline_range is not None and baseline_value > 0:
                    net_dose = mean_dose - baseline_value
                    net_dose_per_burst_nsv = (net_dose * 1000.0) / bursts_per_hour
                    print(f"    Baseline ({baseline_range[0]}-{baseline_range[1]})               : {baseline_value:.3f} µSv/h")
                    print(f"    Net Mean Dose Rate (Mean-Baseline)  : {net_dose:.3f} ± {sem_dose:.3f} µSv/h (SEM)")
                    print(f"    Net Dose per Burst                   : {net_dose_per_burst_nsv:.5f} ± {sem_per_burst_nsv:.5f} nSv/burst")

                # Apply optional correction factor to the net dose
                    if correction_factor is not None:
                        corrected_net_dose = net_dose * correction_factor
                        corrected_sem = sem_dose * correction_factor # Propagate error through a constant
                        corrected_burst_nsv = (corrected_net_dose * 1000.0) / bursts_per_hour
                        corrected_burst_sem = (corrected_sem * 1000.0) / bursts_per_hour
                        # Colored in red
                        print(f"\033[31m    Corrected Net Dose by sensitivity (x {correction_factor:.2f})  : " f"{corrected_net_dose:.3f} ± {corrected_sem:.3f} µSv/h (SEM)\033[0m")
                        print(f"\033[31m    Corrected Net Dose per Burst         : " f"{corrected_burst_nsv:.5f} ± {corrected_burst_sem:.5f} nSv/burst\033[0m")
                
                #print(f"    Median Dose Rate (Robust Peak)      : {median_dose:.3f} µSv/h")
                #print(f"    Data Standard Deviation (σ)         : {std_dose:.3f} µSv/h")
            else:
                print(f"\n[-] Frequency Regime: {display_label}")
                print(f"    No data points passed the active plateau criteria.")

    # Conditional workflow based on splits definition
    if splits:
        last_time = None
        for split in splits:
            # Get dynamic string representations for the time interval
            start_t = last_time.strftime('%H:%M') if last_time is not None else df_analysis['datetime'].min().strftime('%H:%M')
            end_t = split["time_boundary"] if split["time_boundary"] is not None else df_analysis['datetime'].max().strftime('%H:%M')

            print(f"\n>>> Sub-Interval Analysis Block: {split['name']} ({start_t} - {end_t}) <<<")
            split_mask = pd.Series(True, index=df_analysis.index)
            if last_time is not None:
                split_mask &= (df_analysis['datetime'].dt.time >= last_time)
            if split["time_boundary"] is not None:
                t_bound = pd.to_datetime(split["time_boundary"]).time()
                split_mask &= (df_analysis['datetime'].dt.time < t_bound)
                last_time = t_bound
            
            run_statistics(df_analysis[split_mask], label_suffix=split['name'])
    else:
        run_statistics(df_analysis)
        
    print("="*75 + "\n")


# =============================================================================
# --- 3. MAIN EXECUTION FLOW ---
# =============================================================================

if __name__ == "__main__":
    
    # Define paths for shared machine diagnostics logs
    timestamp_log = "SwissFEL_currentdata/CurrentDataLog_SATMA01-DBPM040_Q1/start.txt"
    charge_log = "SwissFEL_currentdata/CurrentDataLog_SATMA01-DBPM040_Q1/average.txt"
    freq_log = "SwissFEL_frequencydata/FrequencyDataLog_SIN-TIMAST-TMA_Bunch-2-Appl-Freq-RB/average.txt"

    # Load machine logs once for all detectors
    print("[*] Loading machine diagnostics logs...")
    df_machine = load_machine_diagnostics(timestamp_log, charge_log, freq_log)
    
    # -------------------------------------------------------------------------
    # RUN WENDI PIPELINE
    # -------------------------------------------------------------------------
    print("\n[*] Processing WENDI detector...")
    try:
        df_wendi = load_wendi_data("WENDI_data/SwissFEL_Passive.log")
        analyze_and_plot_detector(
            df_det=df_wendi, 
            df_mach=df_machine, 
            detector_name="Wendi", 
            dose_col="val_ext", 
            threshold=20.0,
            ylim_plot=(-10, 500),
            splits=None,
            correction_factor= 1.222
        )
    except Exception as e:
        print(f"[-] Failed to process WENDI data: {e}")

    # -------------------------------------------------------------------------
    # RUN LUPIN PIPELINE
    # -------------------------------------------------------------------------
    print("\n[*] Processing LUPIN detector...")
    try:
        lupin_position_splits = [
            {"name": "LUPIN Position 1", "time_boundary": "10:30", "color": "#9467bd"},
            {"name": "LUPIN Position 2", "time_boundary": None,    "color": "#e377c2"}
        ]
        
        df_lupin = load_lupin_data("LUPIN_data/20250701")
        analyze_and_plot_detector(
            df_det=df_lupin, 
            df_mach=df_machine, 
            detector_name="Lupin", 
            dose_col="Dose rate (uSv/h)", 
            threshold=25.0,
            ylim_plot=(-5, 650),
            splits=lupin_position_splits,
            correction_factor=0.9745
        )
    except Exception as e:
        print(f"[-] Failed to process LUPIN data: {e}")

    # -------------------------------------------------------------------------
    # RUN NAUSICAA PIPELINE
    # -------------------------------------------------------------------------
    print("\n[*] Processing NAUSICAA detector...")
    try:
        nausicaa_position_splits = [
            {"name": "NAUSICAA Position 1", "time_boundary": "10:30", "color": "#ff7f0e"},
            {"name": "NAUSICAA Position 2", "time_boundary": None,    "color": "#d62728"}
        ]

        nausicaa_files = [
            "NAUSICAA_data/20250630",
            "NAUSICAA_data/20250701"
        ]

        df_nausicaa = load_nausicaa_data(nausicaa_files)

        # Filter NAUSICAA times from 07:00 of 1 July 2025
        df_nausicaa = df_nausicaa[(df_nausicaa['datetime'].dt.day == 1) & (df_nausicaa['datetime'].dt.hour >= 7)]

        analyze_and_plot_detector(
            df_det=df_nausicaa,
            df_mach=df_machine,
            detector_name="Nausicaa",
            dose_col="Dose rate (uSv/h)",
            threshold=10.0,
            ylim_plot=(-5, 1100),
            splits=nausicaa_position_splits,
            correction_factor=0.811
        )
    except Exception as e:
        print(f"[-] Failed to process NAUSICAA data: {e}")

    # -------------------------------------------------------------------------
    # RUN DRPS 376m PIPELINE
    # -------------------------------------------------------------------------
    print("\n[*] Processing DRPS 376m detector...")
    try:
        df_drps_376 = load_drps_data("DRPS_data/DRPS_376m")
        analyze_and_plot_detector(
            df_det=df_drps_376,
            df_mach=df_machine,
            detector_name="DRPS_376m",
            dose_col="dose_rate",
            threshold=10.0,
            ylim_plot=(-5, 70),
            splits=None,
            baseline_range=("12:00","13:00")
        )
    except Exception as e:
        print(f"[-] Failed to process DRPS 376m data: {e}")

    # -------------------------------------------------------------------------
    # RUN DRPS 387m PIPELINE
    # -------------------------------------------------------------------------
    print("\n[*] Processing DRPS 387m detector...")
    try:
        # Assuming the folder for the second detector follows the same naming convention
        df_drps_387 = load_drps_data("DRPS_data/DRPS_387m")
        analyze_and_plot_detector(
            df_det=df_drps_387,
            df_mach=df_machine,
            detector_name="DRPS_387m",
            dose_col="dose_rate",
            threshold=10.0,
            ylim_plot=(-5, 300),
            splits=None,
            baseline_range=("12:00","13:00")
        )
    except Exception as e:
        print(f"[-] Failed to process DRPS 387m data: {e}")
