import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

# Detector parameters
tau = 100.0  # Time constant of the rem counter in microseconds

def compute_signal(t_array, t_start, T, tau_const):
    """
    Computes the analytical response of the rem counter to a rectangular 
    neutron burst of duration T starting at t_start.
    Assuming constant total energy/neutrons per burst.
    """
    sig = np.zeros_like(t_array)
    
    # 1. During the burst (t_start <= t <= t_start + T)
    mask_during = (t_array >= t_start) & (t_array <= t_start + T)
    sig[mask_during] = (tau_const / T) * (1.0 - np.exp(-(t_array[mask_during] - t_start) / tau_const))
    
    # 2. After the burst (t > t_start + T)
    peak_val = (tau_const / T) * (1.0 - np.exp(-T / tau_const))
    mask_after = (t_array > t_start + T)
    sig[mask_after] = peak_val * np.exp(-(t_array[mask_after] - (t_start + T)) / tau_const)
    
    return sig

# ====================================================================
# PLOT 1: Varying burst duration at 2 kHz (Analytical Computation)
# ====================================================================
freq_1 = 2.0  # kHz
durations_ns = [0.1, 100.0]
durations_us = [d / 1000.0 for d in durations_ns]

# Non-uniform time grid for high sub-nanosecond resolution around t = 0
t_pre = np.linspace(-10, -0.001, 100)
t_fine = np.linspace(-0.001, 0.2, 10000)
t_post = np.linspace(0.2, 600, 2000)
t_array_1 = np.unique(np.concatenate([t_pre, t_fine, t_post]))

fig1, axes1 = plt.subplots(2, 1, figsize=(10, 8), layout='constrained')

for i, T in enumerate(durations_us):
    ax = axes1[i]
    
    # Calculate analytical response
    signal = compute_signal(t_array_1, t_start=0.0, T=T, tau_const=tau)
    
    # Main plot
    ax.plot(t_array_1, signal, color='blue', label='REM Counter Signal (Computed)')
    ax.axvspan(0, T, color='red', alpha=0.5, label=f'Burst Duration ({durations_ns[i]} ns)')
    
    ax.set_ylabel('Signal (a.u.)')
    ax.set_title(f'Burst Duration: {durations_ns[i]} ns (Frequency: {freq_1} kHz)')
    ax.grid(True)
    ax.legend(loc='upper right')
    
    # Inset plot for zoom near t = 0
    axins = inset_axes(ax, width="30%", height="30%", loc=5, borderpad=2)
    axins.plot(t_array_1, signal, color='blue')
    axins.axvspan(0, T, color='red', alpha=0.5)
    
    # Set zoom limits
    x1, x2 = -0.05, max(0.05, T * 2)
    axins.set_xlim(x1, x2)
    axins.set_ylim(0.9, 1.02)
    ax.indicate_inset_zoom(axins, edgecolor="black")

axes1[-1].set_xlabel(r'Time ($\mu$s)')
fig1.savefig('plot1_burst_duration_computed.png', bbox_inches='tight')

# ====================================================================
# PLOT 2: Varying repetition frequency (2, 10, 50 kHz) with fixed 0.1 ns burst
# ====================================================================
burst_duration_us = 0.1 / 1000.0  # 0.1 ns in microseconds
frequencies_khz = [2, 10, 50]
t_max = 1000.0
t_array_2 = np.linspace(0, t_max, 10000)

fig2, axes2 = plt.subplots(3, 1, figsize=(10, 10), sharex=True, layout='constrained')

for i, freq in enumerate(frequencies_khz):
    period_us = 1000.0 / freq
    burst_times = np.arange(0, t_max, period_us)
    
    signal = np.zeros_like(t_array_2)
    ax = axes2[i]
    
    for t_burst in burst_times:
        # Superimpose the analytical response for each new burst
        signal += compute_signal(t_array_2, t_start=t_burst, T=burst_duration_us, tau_const=tau)
        
        # Plot visual red band for the burst
        ax.axvspan(t_burst, t_burst + burst_duration_us, color='red', alpha=0.5)
    
    ax.plot(t_array_2, signal, color='blue', label='REM Counter Signal (Computed)')
    
    # Add proxy artist for legend
    red_patch = mpatches.Patch(color='red', alpha=0.5, label='Neutron Burst (0.1 ns)')
    handles, labels = ax.get_legend_handles_labels()
    handles.append(red_patch)
    
    ax.set_ylabel('Signal (a.u.)')
    ax.set_title(rf'Repetition Frequency: {freq} kHz (Period: {period_us:.1f} $\mu$s)')
    ax.grid(True)
    if i == 0:
        ax.legend(handles=handles, loc='upper right')

axes2[-1].set_xlabel(r'Time ($\mu$s)')
fig2.savefig('plot2_repetition_frequency_computed.png', bbox_inches='tight')

plt.show()
